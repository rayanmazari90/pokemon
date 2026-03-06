import pandas as pd
import streamlit as st

import src.ui_components as ui
import src.battle_engine as battle
import src.pokeapi_client as pokeapi
import src.charts as charts
import src.battle_playback as playback
import src.intro_component as intro
import src.sound_engine as sound

DIALOGUE = {
    1: "Choose your Pokémon, trainers! Pick wisely...",
    2: "Select a battle move for each Pokémon!",
    3: "Study your opponent! Compare stats and plan your strategy.",
    4: "The arena is ready. Press FIGHT to begin!",
    5: "The battle is over! Review the results below.",
}


@st.cache_data(show_spinner=False)
def fetch_all_pokemon_names() -> list[str]:
    import requests
    try:
        resp = requests.get("https://pokeapi.co/api/v2/pokemon?limit=2000", timeout=10)
        resp.raise_for_status()
        return sorted([p["name"] for p in resp.json().get("results", [])])
    except Exception:
        return []


def load_css(path: str):
    try:
        with open(path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def _init():
    defaults = dict(
        current_step=1,
        p1_pokemon=None,
        p2_pokemon=None,
        p1_move=None,
        p2_move=None,
        battle_results=None,
        battle_played=False,
        show_playback=True,
        sound_enabled=True,
        _pending_sound=None,
    )
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _go(step: int, snd: str = "next"):
    st.session_state.current_step = step
    st.session_state._pending_sound = snd
    st.rerun()


def _play_pending_sound():
    """Play a queued navigation sound (set before a rerun)."""
    snd = st.session_state.get("_pending_sound")
    if snd:
        sound.play(snd)
        st.session_state._pending_sound = None


# ═══════════════════════════════════════════════════════════════════════════
#  STEP 1 — SELECT POKÉMON
# ═══════════════════════════════════════════════════════════════════════════

def _step_select():
    all_names = fetch_all_pokemon_names()

    col1, mid, col2 = st.columns([5, 1, 5])

    with col1:
        st.markdown(
            '<div class="player-header p1">PLAYER 1</div>',
            unsafe_allow_html=True,
        )
        default_p1 = (
            all_names.index("pikachu") if "pikachu" in all_names else 0
        )
        p1_name = st.selectbox(
            "P1 Pokémon", options=all_names, index=default_p1,
            key="p1_sel", label_visibility="collapsed",
        )
        if p1_name:
            with st.spinner(f"Loading {p1_name}..."):
                data = pokeapi.fetch_pokemon(p1_name)
            if data:
                st.session_state.p1_pokemon = data
                ui.render_trainer_card(data, "p1")
            else:
                st.error(f"Could not find '{p1_name}'")
                st.session_state.p1_pokemon = None

    with mid:
        st.markdown(
            '<div class="vs-badge">VS</div>', unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            '<div class="player-header p2">PLAYER 2</div>',
            unsafe_allow_html=True,
        )
        default_p2 = (
            all_names.index("bulbasaur") if "bulbasaur" in all_names
            else 0
        )
        p2_name = st.selectbox(
            "P2 Pokémon", options=all_names, index=default_p2,
            key="p2_sel", label_visibility="collapsed",
        )
        if p2_name:
            with st.spinner(f"Loading {p2_name}..."):
                data = pokeapi.fetch_pokemon(p2_name)
            if data:
                st.session_state.p2_pokemon = data
                ui.render_trainer_card(data, "p2")
            else:
                st.error(f"Could not find '{p2_name}'")
                st.session_state.p2_pokemon = None

    # Arena preview AFTER selections so it uses the freshly-updated state
    ui.render_arena_preview(
        st.session_state.p1_pokemon, st.session_state.p2_pokemon,
    )

    ready = (
        st.session_state.p1_pokemon is not None
        and st.session_state.p2_pokemon is not None
    )
    msg = (
        "Both Pokémon selected! Press NEXT to choose moves."
        if ready else DIALOGUE[1]
    )
    ui.render_dialogue(msg)
    _nav_buttons(1, can_next=ready)


# ═══════════════════════════════════════════════════════════════════════════
#  STEP 2 — CHOOSE MOVES
# ═══════════════════════════════════════════════════════════════════════════

def _step_moves():
    p1 = st.session_state.p1_pokemon
    p2 = st.session_state.p2_pokemon
    if not p1 or not p2:
        ui.render_dialogue("Please go back and select both Pokémon first.")
        _nav_buttons(2, can_next=False)
        return

    ui.render_arena_preview(p1, p2)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="player-header p1">P1 — MOVE</div>', unsafe_allow_html=True)
        ui.render_compact_card(p1, "p1")
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        p1_move = ui.render_move_selection(p1, key_prefix="p1")
        if p1_move:
            st.session_state.p1_move = p1_move

    with col2:
        st.markdown('<div class="player-header p2">P2 — MOVE</div>', unsafe_allow_html=True)
        ui.render_compact_card(p2, "p2")
        st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
        p2_move = ui.render_move_selection(p2, key_prefix="p2")
        if p2_move:
            st.session_state.p2_move = p2_move

    ready = st.session_state.p1_move is not None and st.session_state.p2_move is not None
    msg = "Both moves locked in! Press NEXT to compare." if ready else DIALOGUE[2]
    ui.render_dialogue(msg)
    _nav_buttons(2, can_next=ready)


# ═══════════════════════════════════════════════════════════════════════════
#  STEP 3 — COMPARE
# ═══════════════════════════════════════════════════════════════════════════

def _step_compare():
    p1 = st.session_state.p1_pokemon
    p2 = st.session_state.p2_pokemon
    p1m = st.session_state.p1_move
    p2m = st.session_state.p2_move
    if not all([p1, p2, p1m, p2m]):
        ui.render_dialogue("Go back and complete selection first.")
        _nav_buttons(3, can_next=False)
        return

    col1, col2 = st.columns(2)
    with col1:
        ui.render_compact_card(p1, "p1")
    with col2:
        ui.render_compact_card(p2, "p2")

    ui.render_section_title("Base Stat Comparison")
    fig = charts.render_stat_comparison(p1, p2)
    st.plotly_chart(fig, use_container_width=True)

    ui.render_type_matchup(p1, p2, p1m, p2m)

    ui.render_dialogue(DIALOGUE[3])
    _nav_buttons(3, can_next=True)


# ═══════════════════════════════════════════════════════════════════════════
#  STEP 4 — BATTLE
# ═══════════════════════════════════════════════════════════════════════════

def _step_battle():
    p1 = st.session_state.p1_pokemon
    p2 = st.session_state.p2_pokemon
    p1m = st.session_state.p1_move
    p2m = st.session_state.p2_move
    if not all([p1, p2, p1m, p2m]):
        ui.render_dialogue("Go back and complete selection first.")
        _nav_buttons(4, can_next=False)
        return

    ui.render_arena_preview(p1, p2)

    tog1, tog2 = st.columns(2)
    with tog1:
        st.session_state.show_playback = st.checkbox(
            "Show Battle Animation",
            value=st.session_state.show_playback,
            key="anim_toggle",
        )
    with tog2:
        st.session_state.sound_enabled = st.checkbox(
            "Sound Effects",
            value=st.session_state.sound_enabled,
            key="sound_toggle",
        )

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)

    st.markdown('<div class="fight-btn">', unsafe_allow_html=True)
    fight = st.button("⚔  FIGHT!  ⚔", type="primary", use_container_width=True, key="fight_btn")
    st.markdown('</div>', unsafe_allow_html=True)

    if fight:
        p1_combat = {
            "name": p1["name"],
            "stats": pokeapi.get_stats(p1),
            "types": pokeapi.get_types(p1),
            "move": {"name": p1m["name"], **p1m.get("details", {})},
        }
        p2_combat = {
            "name": p2["name"],
            "stats": pokeapi.get_stats(p2),
            "types": pokeapi.get_types(p2),
            "move": {"name": p2m["name"], **p2m.get("details", {})},
        }
        engine = battle.BattleEngine(p1_combat, p2_combat, pokeapi.effectiveness_multiplier)

        with st.spinner("Simulating battle..."):
            results = engine.run_battle()

        if st.session_state.show_playback:
            playback.play_battle_animation(
                p1, p2, results["battle_log"],
                p1_combat["stats"]["hp"], p2_combat["stats"]["hp"],
            )

        st.session_state.battle_results = results
        st.session_state.battle_played = True
        _go(5)

    if not st.session_state.battle_played:
        ui.render_dialogue(DIALOGUE[4])

    _nav_buttons(4, can_next=False, hide_next=True)


# ═══════════════════════════════════════════════════════════════════════════
#  STEP 5 — RESULTS
# ═══════════════════════════════════════════════════════════════════════════

def _step_results():
    p1 = st.session_state.p1_pokemon
    p2 = st.session_state.p2_pokemon
    results = st.session_state.battle_results

    if not results:
        ui.render_dialogue("No battle results yet. Go back and fight!")
        _nav_buttons(5, can_next=False, hide_next=True)
        return

    if results.get("winner", "Draw") == "Draw":
        sound.play("draw")
    else:
        sound.play("victory")

    ui.render_winner_banner(results, p1, p2)

    ui.render_section_title("HP Over Time")
    hp_fig = charts.render_hp_history(
        results["hp_history"], p1, p2,
        p1_label=results.get("p1_label", p1["name"]),
        p2_label=results.get("p2_label", p2["name"]),
    )
    if hp_fig:
        st.plotly_chart(hp_fig, use_container_width=True)

    ui.render_section_title("Battle Log")
    log_df = pd.DataFrame(results["battle_log"])
    if not log_df.empty:
        log_df["Round"] = "Round " + log_df["Round"].astype(str)
        display_cols = ["Round", "Attacker", "Move", "Defender", "Damage", "Message"]
        log_df = log_df[[c for c in display_cols if c in log_df.columns]]
    st.dataframe(log_df, use_container_width=True, hide_index=True)

    ui.render_dialogue(DIALOGUE[5])

    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 3, 2])
    with c1:
        if st.button("⚔ REMATCH", use_container_width=True, type="primary", key="rematch"):
            st.session_state.battle_results = None
            st.session_state.battle_played = False
            _go(4, snd="select")
    with c2:
        if st.button("🔄 SWAP SIDES", use_container_width=True, key="swap"):
            st.session_state.p1_pokemon, st.session_state.p2_pokemon = (
                st.session_state.p2_pokemon, st.session_state.p1_pokemon)
            st.session_state.p1_move, st.session_state.p2_move = (
                st.session_state.p2_move, st.session_state.p1_move)
            st.session_state.battle_results = None
            st.session_state.battle_played = False
            _go(4, snd="select")
    with c3:
        if st.button("🏠 NEW BATTLE", use_container_width=True, key="newbattle"):
            for k in ("p1_pokemon", "p2_pokemon", "p1_move", "p2_move",
                       "battle_results", "battle_played"):
                st.session_state[k] = (
                    None if "pokemon" in k or "move" in k
                    or "results" in k else False
                )
            _go(1, snd="back")


# ═══════════════════════════════════════════════════════════════════════════
#  NAVIGATION HELPERS
# ═══════════════════════════════════════════════════════════════════════════

def _nav_buttons(step: int, can_next: bool = True, hide_next: bool = False):
    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    left, _, right = st.columns([2, 6, 2])
    with left:
        if step > 1:
            if st.button("◂ BACK", key=f"back_{step}", use_container_width=True):
                _go(step - 1, snd="back")
    with right:
        if not hide_next and step < 5:
            if st.button("NEXT ▸", key=f"next_{step}", type="primary",
                         disabled=not can_next, use_container_width=True):
                _go(step + 1, snd="next")


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════

STEP_FN = {1: _step_select, 2: _step_moves, 3: _step_compare, 4: _step_battle, 5: _step_results}


def main():
    st.set_page_config(
        page_title="Pokémon Combat Simulator",
        page_icon="⚔",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    load_css("ui.css")
    intro.show_intro_screen()
    _init()

    ui.render_top_bar()
    step = st.session_state.current_step
    ui.render_step_indicator(step)

    _play_pending_sound()

    STEP_FN[step]()


if __name__ == "__main__":
    main()
