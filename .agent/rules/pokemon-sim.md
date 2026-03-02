---
trigger: always_on
---

# Pokemon Combat Simulator — Workspace Rules (Always On)

## Single source of truth
- Treat @docs/SPEC.md as the grading contract.
- Treat @docs/SCOPE_PLUS.md as optional “nice-to-haves”.
- After any change, update @docs/HANDOFF.md with:
  - files changed
  - what was added/removed
  - how to run/test (exact commands)
  - any known issues

## Safety & hygiene
- Do NOT run destructive terminal commands (rm -rf, del, format, disk ops).
- Prefer minimal terminal usage; when needed, only run:
  - pip install -r requirements.txt
  - streamlit run dashboard.py
  - python -m py_compile ...
- Never touch files outside the workspace.

## Coding constraints
- No hardcoded Pokémon data (everything from PokeAPI at runtime).
- All API fetch functions must use @st.cache_data and must handle errors.
- Must use all 3 endpoints: /pokemon/{name}, /move/{name}, /type/{name}.
- Type effectiveness must multiply across defender dual-types.

## Integration discipline
- Only modify files you are assigned to in the current task.
- If you need another file changed, write a note in @docs/HANDOFF.md instead of editing it.