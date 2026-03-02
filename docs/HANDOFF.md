# Handoff Document

This document tracks state, current working context, API usage patterns, and open tasks for each agent.

## Agents

### API Agent
- **Description:** Responsible for `pokeapi_client.py` and interacting with the PokeAPI.
- **Current Status:** Completed core API wrappers and helper parsing functions.
- **Files Touched/Added:** `src/pokeapi_client.py`, `src/__init__.py`.
- **Open Tasks:** None.
- **Available Functions for Dashboard:**
  - `fetch_pokemon(name)`, `fetch_move(name)`, `fetch_type(name)`
  - `get_sprite_url(pokemon_data)` -> str
  - `get_stats(pokemon_data)` -> dict
  - `get_types(pokemon_data)` -> list[str]
  - `get_move_names(pokemon_data)` -> list[str]
  - `get_move_details(move_data)` -> dict
  - `effectiveness_multiplier(move_type, defender_types)` -> float

### Battle Engine Agent
- **Description:** Responsible for core OOP logic in `battle_engine.py`.
- **Current Status:** Completed `BattleEngine` class matching grading SPEC.
- **Files Touched/Added:** `src/battle_engine.py`
- **Open Tasks:** None.
- **Usage Example:**
  ```python
  from src.battle_engine import BattleEngine
  # 'type_effectiveness_func' must take (move_type, defender_types_list) -> float
  engine = BattleEngine(p1_data, p2_data, effectiveness_multiplier_func)
  results = engine.run_battle()
  ```
- **Output Dict Keys (`results`)**:
  - `winner` (str): Name of winning pokemon or `"Draw"`
  - `battle_log` (list[dict]): Keys are `Round` (int), `Attacker` (str), `Defender` (str), `Move` (str), `Damage` (int), `Message` (str)
  - `hp_history` (list[dict]): Tidy format. Keys are `Round` (int), `Pokemon` (str), `HP` (int)

### Dashboard UI Agent
- **Description:** Responsible for Streamlit components and user interface setup.
- **Current Status:** Completed sections 1-3. 2-column layout built, Pokemon search and data display wired. Damaging move selection with lazy API fetching and validation works.
- **Files Touched/Added:** `dashboard.py`, `src/ui_components.py`
- **Open Tasks:** None.
- **Integration Notes for Agent 5 & 3:**
  - Open `dashboard.py` and search for `# PLACEHOLDER`.
  - When both valid Pokemon and damaging moves are selected, the variables `p1_pokemon`, `p2_pokemon`, `p1_move`, and `p2_move` are guaranteed to contain valid data dictionaries.
  - **Agent 5 (Charts):** Add your `st.plotly_chart` right above the battle button. Use `p1_pokemon` and `p2_pokemon` stats dicts. Note: wait for Agent 3 results to plot the HP history chart.
  - **Agent 3 (Battle Engine):** Implement the `BattleEngine` run logic underneath `if st.button("Battle!", ...):`. Then pass `results` to Agent 5's line chart function.

### Charts & Pandas Agent
- **Description:** Responsible for data visualization and pandas data frame manipulations.
- **Current Status:** Completed stat comparison, HP history, and battle log integrations.
- **Files Touched/Added:** `src/charts.py`, `dashboard.py`
- **Open Tasks:** None.
- **Implementation Details:**
  - **Stat comparison chart:** Uses `pd.DataFrame`, reshapes via `.melt()`, and renders with `px.bar(..., barmode='group')`.
  - **Battle Log:** Wrapped `results["battle_log"]` in `pd.DataFrame()` and presented using `st.dataframe()`. Schema includes `Round`, `Attacker`, `Defender`, `Move`, `Damage`, `Message`.
  - **HP History chart:** Wrapped `results["hp_history"]` in `pd.DataFrame()` and mapped using `px.line(..., markers=True)`. Schema includes `Round`, `Pokemon`, `HP` in tidy format.

### Repo/Deploy Agent
- **Description:** Responsible for deployment, repository management, and environment.
- **Current Status:**
- **Files Touched/Added:**
- **Open Tasks:**

---

## Recent Workspace Edits

**Architect Agent Setup:**
- Created `docs/SPEC.md` for grading rubric.
- Created `docs/SCOPE_PLUS.md` for optional features.
- Created this `docs/HANDOFF.md` template.
- Created `dashboard.py` and `src/` directory with `pokeapi_client.py`, `battle_engine.py`, `ui_components.py`, and `charts.py` placeholders.

**Bug Fix Agent Edits:**
- **Files Changed:** `src/charts.py`, `dashboard.py`
- **What was added/removed:** 
  - Fixed `AttributeError` in `charts.py` by importing `pokeapi_client` and parsing raw JSON into a dictionary using `get_stats()`.
  - Updated data preparation in `dashboard.py` `Battle!` button callback so `BattleEngine` receives correctly structured dictionaries for `stats`, `types`, and `move`.
- **How to run/test:** `streamlit run dashboard.py` and execute a battle. 
- **Open Issues:** None.

## How To Run Placeholder App
```bash
streamlit run dashboard.py
```
