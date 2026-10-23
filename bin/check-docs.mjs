#!/usr/bin/env node
// Checks README.md and docs/guide/*.md against keel's skill tree so structural
// doc drift fails CI. Idea credit: pstack's scripts/check-pstack-docs.mjs (not copied).
import { readdirSync, readFileSync, existsSync, statSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const read = (rel) => readFileSync(join(root, rel), "utf8");
const stems = (dir, ext) =>
  readdirSync(join(root, dir))
    .filter((f) => f.endsWith(ext))
    .map((f) => f.slice(0, -ext.length))
    .sort();

const sectionOf = (text, heading) => {
  const start = text.indexOf(heading);
  if (start < 0) return "";
  const next = text.indexOf("\n#", start + heading.length);
  return text.slice(start, next < 0 ? undefined : next);
};

function buildTree() {
  const skills = readdirSync(join(root, "skills"))
    .filter((d) => existsSync(join(root, "skills", d, "SKILL.md")))
    .sort();
  const setupStep4 = sectionOf(read("skills/setup/SKILL.md"), "### 4. Validate");
  return {
    skills,
    principles: skills.filter((s) => s.startsWith("principle-")),
    commands: skills.filter((s) => !s.startsWith("principle-")),
    playbooks: stems("skills/lead/playbooks", ".md"),
    agents: stems("agents", ".md"),
    setupValues: new Set([...setupStep4.matchAll(/`([a-z-]+)`/g)].map((m) => m[1])),
    upstreamSlugs: new Set(
      [...sectionOf(read("UPSTREAM.md"), "## Translation table").matchAll(MODEL_SLUG)].map((m) => cleanSlug(m[0])),
    ),
  };
}

const MODEL_SLUG = /\b(?:claude-(?:[a-z]+-)?\d|grok-\d|gpt-\d)[\w.-]*/g;
const cleanSlug = (s) => s.replace(/[.-]+$/, "");

function loadDoc(file) {
  let fenced = false;
  const lines = read(file)
    .split("\n")
    .map((text, i) => {
      if (/^\s*(```|~~~)/.test(text)) {
        fenced = !fenced;
        return { n: i + 1, text, fenced: true };
      }
      return { n: i + 1, text, fenced };
    });
  return { file, lines };
}

const proseLines = (doc) => doc.lines.filter((l) => !l.fenced);
const finding = (doc, line, message) => ({ file: doc.file, line, message });

const BUILTIN_COMMANDS = new Set(["loop", "simplify", "bg", "plugin", "hooks", "schedule"]);
const PLACEHOLDERS = new Set(["name"]);
const RENAMED = {
  "poteto-mode": "lead",
  "setup-pstack": "setup",
  deslop: "simplify",
};
const REMOVED = new Set(["poteto-help"]);

function checkSlashCommands(tree, doc) {
  const out = [];
  const known = new Set(tree.skills);
  for (const l of doc.lines) {
    const text = l.text.replace(/\]\([^)]*\)/g, "]").replace(/https?:\/\/\S+/g, "");
    for (const m of text.matchAll(/(?<![\w./<>~$:}-])\/(?:keel:)?([a-z][a-z0-9-]*)(?![\w/<>:-]|\.\w)/g)) {
      const name = m[1];
      if (known.has(name) || BUILTIN_COMMANDS.has(name) || PLACEHOLDERS.has(name)) continue;
      if (name in RENAMED) out.push(finding(doc, l.n, `/${name} is upstream's name, use /keel:${RENAMED[name]}`));
      else if (REMOVED.has(name)) out.push(finding(doc, l.n, `/${name} was removed and has no keel equivalent`));
      else out.push(finding(doc, l.n, `/${name} is not a keel skill or an allowlisted Claude Code built-in`));
    }
  }
  return out;
}

const slugCache = new Map();
function headingSlugs(abs) {
  if (slugCache.has(abs)) return slugCache.get(abs);
  const seen = new Map();
  const slugs = new Set();
  let fenced = false;
  for (const line of readFileSync(abs, "utf8").split("\n")) {
    if (/^\s*(```|~~~)/.test(line)) fenced = !fenced;
    const m = !fenced && line.match(/^#{1,6}\s+(.*?)\s*#*\s*$/);
    if (!m) continue;
    const base = m[1]
      .replace(/!?\[([^\]]*)\]\([^)]*\)/g, "$1")
      .replace(/[`*~]|<[^>]+>/g, "")
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s_-]/gu, "")
      .trim()
      .replace(/\s/g, "-");
    const count = seen.get(base) ?? 0;
    seen.set(base, count + 1);
    slugs.add(count ? `${base}-${count}` : base);
  }
  slugCache.set(abs, slugs);
  return slugs;
}

function checkLinks(_tree, doc) {
  const out = [];
  for (const l of proseLines(doc)) {
    for (const m of l.text.matchAll(/!?\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)) {
      const target = m[1];
      if (/^[a-z][a-z0-9+.-]*:/i.test(target)) continue;
      const [pathPart, anchor] = target.split("#");
      const abs = pathPart ? resolve(root, dirname(doc.file), pathPart) : join(root, doc.file);
      if (!existsSync(abs)) {
        out.push(finding(doc, l.n, `link target ${pathPart} does not exist`));
      } else if (anchor && abs.endsWith(".md") && statSync(abs).isFile() && !headingSlugs(abs).has(anchor)) {
        out.push(finding(doc, l.n, `anchor #${anchor} matches no heading in ${relative(root, abs)}`));
      }
    }
  }
  return out;
}

const ONES = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(" ");
const TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split(" ");
const NUMBER_WORDS = new Map(ONES.map((w, i) => [w, i + 1]));
for (const [t, tw] of TENS.entries()) {
  NUMBER_WORDS.set(tw, (t + 2) * 10);
  ONES.slice(0, 9).forEach((w, i) => NUMBER_WORDS.set(`${tw}-${w}`, (t + 2) * 10 + i + 1));
}
const numberPattern = `\\d{1,2}|${[...NUMBER_WORDS.keys()].sort((a, b) => b.length - a.length).join("|")}`;

// A count is a whole-set claim when a number of 10 or more directly precedes a
// set noun (one adjective allowed) and does not follow "pstack's". Smaller
// numbers are skipped because prose names subsets ("the two skills").
// "short skills" means the principles.
const COUNT_CLAIM = new RegExp(
  `(?<!pstack's\\s)\\b(?<num>${numberPattern})\\s+(?:(?<adj>short)\\s+)?(?<noun>playbook|principle|skill|agent|command)s\\b`,
  "gi",
);

function checkCounts(tree, doc) {
  const out = [];
  const actual = {
    playbook: tree.playbooks.length,
    principle: tree.principles.length,
    skill: tree.skills.length,
    agent: tree.agents.length,
    command: tree.commands.length,
  };
  for (const l of proseLines(doc)) {
    for (const m of l.text.matchAll(COUNT_CLAIM)) {
      const { num, adj, noun } = m.groups;
      const claimed = /^\d/.test(num) ? Number(num) : NUMBER_WORDS.get(num.toLowerCase());
      if (claimed < 10) continue;
      const kind = adj && noun.toLowerCase() === "skill" ? "principle" : noun.toLowerCase();
      if (claimed !== actual[kind]) {
        out.push(finding(doc, l.n, `"${m[0].trim()}" but the tree has ${actual[kind]} ${kind}s`));
      }
    }
  }
  return out;
}

function checkReadmeTables(tree, doc) {
  if (doc.file !== "README.md") return [];
  const text = doc.lines.map((l) => l.text).join("\n");
  const wanted = [
    ...tree.skills.map((s) => [`./skills/${s}/SKILL.md`, `skill ${s}`]),
    ...tree.playbooks.map((p) => [`./skills/lead/playbooks/${p}.md`, `playbook ${p}`]),
    ...tree.agents.map((a) => [`./agents/${a}.md`, `agent ${a}`]),
  ];
  return wanted
    .filter(([link]) => !text.includes(`](${link})`))
    .map(([link, what]) => finding(doc, 1, `README does not link ${what} (${link})`));
}

const BUILTIN_AGENTS = new Set(["general-purpose", "Explore", "Plan"]);

function checkAgents(tree, doc) {
  const out = [];
  const allowed = new Set([...BUILTIN_AGENTS, ...tree.agents.map((a) => `keel:${a}`)]);
  for (const l of doc.lines) {
    for (const m of l.text.matchAll(/subagent_type[`"']?\s*[:=]\s*[`"']?([\w:-]+)/g)) {
      if (!allowed.has(m[1])) out.push(finding(doc, l.n, `subagent_type "${m[1]}" is not a keel agent or a Claude Code built-in`));
    }
  }
  return out;
}

function readmeModelRows(doc) {
  const start = doc.lines.findIndex((l) => /^#+\s+models\s*$/i.test(l.text));
  if (start < 0) return [];
  const rows = [];
  for (const l of doc.lines.slice(start + 1)) {
    if (/^#/.test(l.text)) break;
    if (/^\|/.test(l.text) && !/^\|[\s|:-]+\|?$/.test(l.text)) rows.push(l);
  }
  return rows.slice(1);
}

function checkModels(tree, doc) {
  const out = [];
  for (const l of doc.lines) {
    for (const m of l.text.matchAll(MODEL_SLUG)) {
      const slug = cleanSlug(m[0]);
      if (!tree.upstreamSlugs.has(slug)) out.push(finding(doc, l.n, `model slug ${slug} is not in UPSTREAM.md's translation table`));
    }
  }
  if (doc.file === "README.md") {
    for (const l of readmeModelRows(doc)) {
      const keelCell = l.text.split("|")[3] ?? "";
      const aliases = keelCell.replace(/\([^)]*\)/g, "").match(/[a-z][a-z-]*/g) ?? [];
      for (const alias of aliases) {
        if (!tree.setupValues.has(alias)) out.push(finding(doc, l.n, `model alias ${alias} is not a value /keel:setup accepts`));
      }
    }
  }
  return out;
}

const CHECKS = [checkSlashCommands, checkLinks, checkCounts, checkReadmeTables, checkAgents, checkModels];

function unnamedCommands(tree, guideDocs) {
  const guide = guideDocs.map((d) => d.lines.map((l) => l.text).join("\n")).join("\n");
  return tree.commands.filter((c) => !new RegExp(`/(?:keel:)?${c}(?![\\w-])`).test(guide));
}

const tree = buildTree();
const docs = ["README.md", ...stems("docs/guide", ".md").map((s) => `docs/guide/${s}.md`)].map(loadDoc);
const findings = docs.flatMap((doc) => CHECKS.flatMap((check) => check(tree, doc)));

console.log(
  `${tree.skills.length} skills (${tree.commands.length} commands, ${tree.principles.length} principles), ` +
    `${tree.playbooks.length} playbooks, ${tree.agents.length} agents; ${docs.length} docs read`,
);
for (const f of findings) console.log(`FAIL ${f.file}:${f.line} ${f.message}`);
const unnamed = unnamedCommands(tree, docs.filter((d) => d.file.startsWith("docs/guide/")));
if (unnamed.length) console.log(`note: the guide never names ${unnamed.length} commands: ${unnamed.join(", ")}`);
console.log(`${findings.length} problems`);
process.exit(findings.length ? 1 : 0);
