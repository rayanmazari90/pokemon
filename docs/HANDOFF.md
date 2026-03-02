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
  - **Stat comparison chart:** Uses `pd.DataFrame`, reshapes via `.melt()`, and renders with `px.bar(..., barmode='group')`. Applied custom theming using `fig.update_layout` to map the `Press Start 2P` font, thick borders, and `#f8f8f8` background matching the surrounding UI cards.
  - **Battle Log:** Wrapped `results["battle_log"]` in `pd.DataFrame()` and presented using `st.dataframe(hide_index=True)`. Pre-processed the 'Round' column string and re-ordered the columns for readability.
  - **HP History chart:** Wrapped `results["hp_history"]` in `pd.DataFrame()` and mapped using `px.line(..., markers=True)`. Applied custom Pokemon-esque theming with `fig.update_layout()`. Schema includes `Round`, `Pokemon`, `HP` in tidy format.

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

**Theming & UX Agent Edits:**
- **Files Changed:** `ui.css`, `dashboard.py`, `src/ui_components.py`
- **What was added/removed:** 
  - Added new `ui.css` applying the 'Press Start 2P' font and defining classes for `.pokemon-card`, `.type-badge`, and `.gameboy-dialog`.
  - Injected CSS via `st.markdown(unsafe_allow_html=True)` inside `dashboard.py`.
  - Added `fetch_all_pokemon_names()` in `dashboard.py` to populate a cached list of 2000 Pokemon options.
  - Added a UI UX toggle inside Player 1 and Player 2 allowing users to switch between typing a name and picking from a pre-loaded dropdown.
  - Wrapped `render_pokemon_info` inside native HTML applying the CSS cards and colored type badges.
  - Wrapped the Battle Results into a native `.gameboy-dialog`.
- **How to run/test:** `streamlit run dashboard.py`. Select the 'Search dropdown' on the UI radio options. Check styles across the UI. Wait for the battle to execute and see the GameBoy styled log section.
- **Open Issues:** None.

**Battle Playback Agent Edits:**
- **Files Changed:** `ui.css`, `dashboard.py`, `src/battle_playback.py`
- **What was added/removed:**
  - Added CSS animations for lunging (`.anim-lunge-right`, `.anim-lunge-left`) and shaking (`.anim-shake`).
  - Created custom HP bars (`.hp-bar-bg`, `.hp-bar-fg`) and an HTML flexbox layout for the battle stage placeholder.
  - Created `play_battle_animation(...)` inside `src/battle_playback.py` using `st.empty()` and string templates.
  - Added a toggle checkbox in `dashboard.py` to optionally play the animation before rendering grading rubrics.
- **How to run/test:** `streamlit run dashboard.py`. Select two valid Pokémon and actions. Ensure "Show Battle Playback" is checked. Click "Battle!". Ensure the GameBoy dialogue and HP bars update through each attacking round with small visual animations via CSS keyframes. Once it finishes, the grading rubric charts and dataframe should appear.
- **Open Issues:** None.

## How To Run Placeholder App
```bash
streamlit run dashboard.py
```
