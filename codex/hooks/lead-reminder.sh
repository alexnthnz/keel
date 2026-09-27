#!/bin/sh

[ "${KEEL_REMINDER:-on}" = "off" ] && exit 0
cat >/dev/null
printf '%s\n' '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"Keel reminder: For a new nontrivial engineering task or a matching Keel playbook, load the installed Keel lead skill if it is not already loaded in this session, then follow it. A casual turn or a user who opts out does not enter lead mode."}}'
