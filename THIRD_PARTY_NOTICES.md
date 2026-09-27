# Third-party notices

keel is built from other people's work. The projects below are redistributed under the MIT License, with each
copyright notice and license text reproduced as that license requires. Sources used under Creative Commons or
cited as references are listed after them.

## pstack

- **Author:** Lauren Tan ([poteto](https://x.com/poteto))
- **Source:** <https://github.com/cursor/plugins/tree/main/pstack>, pstack 0.15.5 at commit `12d587d`
- **Used for:** the skills, playbooks, principles, references, scripts and guide that keel adapts, and the two
  agents keel renames to `ponytail` and `critic`. keel's changes are described in [`UPSTREAM.md`](./UPSTREAM.md).
  pstack itself adapted some material from the projects below.

```
MIT License

Copyright (c) 2026 Lauren Tan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## cursor-team-kit: thermo-nuclear code quality review

- **Author:** Eric Zakariasson, Cursor
- **Source:** <https://github.com/cursor/plugins/tree/main/cursor-team-kit>, skill `thermo-nuclear-code-quality-review`
- **Used for:** [`skills/interrogate/references/code-quality-review.md`](./skills/interrogate/references/code-quality-review.md),
  adapted by way of pstack.

```
MIT License

Copyright (c) 2026 Cursor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## humanizer

- **Author:** Siqi Chen
- **Source:** <https://github.com/blader/humanizer>
- **Used for:** the patterns and examples in [`skills/unslop/SKILL.md`](./skills/unslop/SKILL.md) and the rhythm
  advice in [`skills/technical-writing/SKILL.md`](./skills/technical-writing/SKILL.md), adapted by way of pstack.
  humanizer builds on Wikipedia's "Signs of AI writing" guide.

```
MIT License

Copyright (c) 2025 Siqi Chen

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Git guardrails (mattpocock/skills)

- **Author:** Matt Pocock
- **Source:** <https://github.com/mattpocock/skills>, the `git-guardrails-claude-code` skill
- **Used for:** [`hooks/git-guard.py`](./hooks/git-guard.py), adapted to inspect only real git command segments
  and to allow `--force-with-lease` onto a named branch that is not protected.

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Google developer documentation style guide

- **Author:** Google
- **Source:** <https://developers.google.com/style>
- **License:** [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Used for:** the "Write sentences to the reader" section of
  [`skills/technical-writing/SKILL.md`](./skills/technical-writing/SKILL.md). Changes: condensed and reworded, with
  some of the guide's examples kept.

## Credited references (ideas summarized in keel's own words)

- **Diátaxis** by Daniele Procida, <https://diataxis.fr>, licensed CC BY-SA 4.0. The four documentation modes in
  `skills/technical-writing` follow its framework; no Diátaxis text is reproduced.
- **ASD Simplified Technical English**, ASD-STE100 Issue 9 (2025), <https://www.asd-ste100.org>.
- **John R. Kohl**, *The Global English Style Guide* (SAS Institute, 2008).
- **John Ousterhout**, *A Philosophy of Software Design* (Yaknyam Press, 2018), for the red flags in
  `skills/architect/references/design-red-flags.md`.
- **Wikipedia, "Signs of AI writing"** (WikiProject AI Cleanup), the source humanizer draws on.

## Trademarks

pstack, Cursor, Claude, Claude Code and other names belong to their owners and are used here only to describe
where keel comes from and what it runs on. keel is not affiliated with or endorsed by Lauren Tan, Anysphere
(Cursor), Siqi Chen, Matt Pocock, Google or Anthropic.
