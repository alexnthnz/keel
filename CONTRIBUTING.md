# Contributing to keel

Thanks for helping. keel is adapted from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan,
so a good change keeps that work recognizable and credited.

## Before you start

- For anything bigger than a small fix, open an issue first so we can agree on the shape.
- If the change is really about pstack's method or wording, consider proposing it upstream too.

## Making a change

1. Fork the repository and create a branch.
2. Make the change. Keep poteto's voice in the skills and playbooks you touch, and keep every credit and source note.
3. Run the same checks CI runs:

   ```bash
   claude plugin validate .
   python3 codex/scripts/validate-package.py
   sh -n codex/hooks/lead-reminder.sh
   python3 -m py_compile hooks/git-guard.py
   python3 hooks/test_git_guard.py
   (cd skills/lead/scripts && bun install --frozen-lockfile && bun test orch watch-pr)
   ```

4. Open a pull request with a [Conventional Commits](https://www.conventionalcommits.org) title, such as
   `fix(lead): …`. Pull requests are squash-merged.

## Material from other projects

Only bring in text or code whose license allows it, and credit it in
[`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md) in the same pull request, with its copyright notice and license.
Share-alike material (such as CC BY-SA) can't be copied into this MIT project; describe the idea in your own words and
cite it instead.

## Pulling in pstack updates

[`UPSTREAM.md`](./UPSTREAM.md) explains how: compare against upstream pstack, then re-apply the translation table and
the rename table.

## License

By contributing, you agree that your contributions are licensed under the [MIT License](./LICENSE). Everyone taking
part agrees to follow the [code of conduct](./CODE_OF_CONDUCT.md).
