# Grading Rubric and Requirements

# Pokémon Combat Simulator — Grading Rubric and Requirements

This document is the **single source of truth** for what must be implemented to earn full points.

---

## Grading Rubric (Total: 10 points)

**All grading is done from the submitted GitHub repository**:
- Code review of `.py` files
- Checking `requirements.txt`
- Reading `README.md` for the deployed URL + contributions
- Visiting the Streamlit URL

Each criterion is **2.5 points** (4 criteria).

---

## Criterion 1: API Usage (2.5 pts)

### What to check in code
Search for:
- `requests.get`
- `@st.cache_data`
- `try/except` or status code checks
- the three endpoint URLs:
  - `/pokemon/`
  - `/move/`
  - `/type/`

### Scoring
**2.5**
- All three endpoints used correctly:
  - `/pokemon/{name}`
  - `/move/{name}`
  - `/type/{name}`
- API functions decorated with `@st.cache_data`
- Error handling for invalid Pokémon names or failed requests (try/except or status checks)
- Type effectiveness calculated correctly for **dual-type defenders** (multiplying per defender type)

**2.0**
- Pokémon + move endpoints used correctly with proper JSON navigation
- Type effectiveness missing OR only handles single-type defenders
- Caching present

**1.5**
- Pokémon endpoint works and data extracted correctly
- Move endpoint has issues (e.g., doesn’t filter `power: None` moves, or move data incomplete)
- No type effectiveness
- Some caching

**1.0**
- Makes API calls with `requests.get()` and parses `.json()`, but extraction incomplete
  - e.g., only name + sprite, misses stats or moves
**0.5**
- Attempts `requests.get()` but response not properly parsed/used
  - e.g., prints raw response, doesn’t call `.json()`, or hardcodes alongside API
**0.0**
- No API usage / data hardcoded

### Key requirements (must-have)
- All 3 endpoints used
- `@st.cache_data` on API fetch functions
- Error handling
- Dual-type effectiveness (multiply across defender types)

---

## Criterion 2: Pandas Usage (2.5 pts)

### What to check in code
Search for:
- `pd.DataFrame`
- `.melt(`
- DataFrames used in charts and `st.dataframe` / `st.table`

### Scoring
**2.5**
All three required DataFrames implemented:
1) Stat comparison DataFrame reshaped with `.melt()` for grouped bar chart  
2) Battle log DataFrame built via `pd.DataFrame(battle_log)` from list of dicts  
3) HP over time DataFrame in tidy format for line chart

**2.0**
- 2 of 3 DataFrames correct; the third missing or uses non-DataFrame approach

**1.5**
- 1 DataFrame correctly used (often battle log)
- Other two use plain dicts/lists or are improperly structured

**1.0**
- `pd.DataFrame()` called but wrong structure OR never used

**0.0**
- No pandas usage

### Key requirements (must-have)
- `.melt()` for stat comparison chart
- `pd.DataFrame(battle_log)` for log table
- tidy HP history DataFrame for line chart

---

## Criterion 3: Dashboard Quality (2.5 pts)

### What to check in code
Look for 6 required sections via Streamlit calls:
- `st.selectbox` / `st.text_input` (selection)
- `st.image` (sprites)
- `st.plotly_chart` (charts)
- `st.button` (battle)
- `st.dataframe` / `st.table` (log table)
- `st.columns` (layout)

### Scoring
**2.5**
All 6 required sections present:
1) Pokémon selection widgets  
2) Pokémon display: `st.image` sprites + name/types/stats  
3) Move selection widgets filtering to damaging moves  
4) Stat comparison Plotly chart  
5) Battle button + battle log table + winner announcement  
6) HP over time Plotly chart  

Plus:
- Good layout using `st.columns` for side-by-side Pokémon panels
- Error states handled gracefully

**2.0**
- 5 of 6 sections present (often HP chart missing)
- Layout uses columns
- Sprites displayed
- Winner announced

**1.5**
- 3–4 sections present
- Basic layout (single column)
- Some charts/simulation incomplete

**1.0**
- Pokémon selection + basic display only
- Minimal interactivity

**0.5**
- Code exists but would crash on interaction (undefined variables, missing imports)

**0.0**
- No working app code

### Key requirements (must-have)
- All 6 sections
- Two-column layout
- Sprites
- Battle log table + HP chart in results

### Positive indicators (not required)
- Effectiveness messages (“Super effective!”)
- Additional visualizations (radar chart)
- PP tracking
- Rematch button
- Move descriptions

---

## Criterion 4: Repo Structure & Deployment (2.5 pts)

### What to check
- `requirements.txt` in repo root with correct dependencies
- `README.md` includes:
  1) working Streamlit URL
  2) contributions section listing each member
- App loads and functions at the deployed URL

### Scoring
**2.5**
- Public repo, clean structure
- Correct `requirements.txt`
- README has working Streamlit URL + contributions
- Code well-organized (reasonable file/function structure)

**2.0**
- Structure correct + requirements + README
- URL works but minor issue (missing dependency, slow but works)
- Contributions present

**1.5**
- Complete code + requirements
- BUT missing Streamlit URL OR URL broken/expired OR contributions missing

**1.0**
- Repo incomplete: missing requirements or wrong dependencies, no README, or disorganized code

**0.0**
- No repository submitted

### Key requirements (must-have)
- `requirements.txt` at root
- `README.md` includes working Streamlit URL + contributions
- Clean repo structure

---

## Grading Summary Table

| Criterion | Max | What to Check |
|---|---:|---|
| API Usage | 2.5 | `requests.get`, `@st.cache_data`, error handling, 3 endpoints |
| Pandas Usage | 2.5 | `pd.DataFrame`, `.melt()`, DataFrames used in charts/tables |
| Dashboard Quality | 2.5 | 6 sections, columns layout, charts, battle, log table |
| Repo & Deployment | 2.5 | requirements + README URL + contributions + working app |

---

## General Deductions (applied after per-criterion scoring)
- **-0.2 per criterion**: hardcoded API data instead of fetching dynamically, significant dead/commented-out code
- **-0.1 per criterion**: obvious crash bugs on valid interactions (undefined vars, wrong signatures)

---

# Assignment Requirements (Full Spec)

## Overview
Build a **Pokémon combat simulator** as an interactive Streamlit dashboard.

This ties together:
- APIs (sessions 7–8)
- pandas
- OOP (sessions 9–12)
- Streamlit (session 14)

No skeleton file is provided — build from scratch.

Estimated time: **10–15 hours** shared across the group.

---

## Deliverable
Submit **one public GitHub repo link** containing:
- Streamlit app `.py` file (e.g., `dashboard.py`)
- `requirements.txt` (root)
- `README.md` including:
  - deployed Streamlit app URL
  - contributions section listing each member's work
- Optional: `.streamlit/config.toml` theme

---

## The PokeAPI
Base URL: `https://pokeapi.co/api/v2/`

You must use 3 endpoints:

### 1) `GET /pokemon/{name}`
Provides stats, types, moves list, sprites.

Example keys:
- `data["name"]`
- `data["sprites"]["front_default"]`
- `types = [t["type"]["name"] for t in data["types"]]`
- `stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}`
- `move_names = [m["move"]["name"] for m in data["moves"]]`

### 2) `GET /move/{name}`
Move details:
- `move["power"]` (some are `None`)
- `move["accuracy"]`
- `move["type"]["name"]`
- `move["damage_class"]["name"]` (`physical` or `special`)

Filter out moves with `power: None`.

### 3) `GET /type/{name}`
Type effectiveness:
- `double_damage_to`, `half_damage_to`, `no_damage_to` inside `damage_relations`

You must compute a type multiplier **against each defender type** and multiply them (dual-type defenders).

---

## Dashboard Requirements (6 sections)

### 1) Pokémon selection
Two Pokémon chosen via `st.selectbox`, `st.text_input`, etc.

### 2) Pokémon display
For each:
- sprite (`st.image`)
- name + types
- base stats: hp, attack, defense, special-attack, special-defense, speed

### 3) Move selection
For each Pokémon pick **one damaging move** (`power > 0`), display:
- power, accuracy, type, damage class

### 4) Stat comparison chart
Plotly grouped bar chart comparing both Pokémon stats side-by-side.

### 5) Combat simulation
A **"Battle!"** button that runs turn-based simulation, display:
- battle log table
- winner announcement

### 6) HP over time chart
Plotly line chart showing both Pokémon HP decreasing over rounds.

---

## Combat Mechanics (must match exactly)

Damage formula (level fixed = 50):

- Choose stats based on move `damage_class`
  - physical: Attack vs Defense
  - special: Special-Attack vs Special-Defense
- Compute effectiveness multiplier using move type vs EACH defender type (multiply)
- Accuracy check (miss = 0 damage)

Reference formula:

```python
import random

level = 50

if move_damage_class == "physical":
    attack_stat = attacker_stats["attack"]
    defense_stat = defender_stats["defense"]
else:
    attack_stat = attacker_stats["special-attack"]
    defense_stat = defender_stats["special-defense"]

effectiveness = 1.0
for defender_type in defender_types:
    if defender_type in double_damage_to:
        effectiveness *= 2.0
    elif defender_type in half_damage_to:
        effectiveness *= 0.5
    elif defender_type in no_damage_to:
        effectiveness *= 0.0

if random.random() < (move_accuracy / 100):
    damage = int(
        ((2 * level / 5 + 2) * move_power * (attack_stat / defense_stat) / 50 + 2)
        * effectiveness
    )
else:
    damage = 0