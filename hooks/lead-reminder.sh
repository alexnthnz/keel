#!/bin/sh
# UserPromptSubmit: keep the lead's method sticky across turns, as pstack's `reminder:` frontmatter does for
# poteto-mode in Cursor. Claude Code has no sticky-mode flag, so the reminder is re-injected on every prompt.
# Set KEEL_REMINDER=off to silence it.
[ "${KEEL_REMINDER:-on}" = "off" ] && exit 0
cat >/dev/null
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"keel reminder: New task? A playbook match or a need for rigor means the lead method applies: load the keel:lead skill if it is not loaded yet in this session, then follow it. A casual turn, or a user who opts out, does not."}}'
