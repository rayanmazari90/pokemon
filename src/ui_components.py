import streamlit as st
import src.pokeapi_client as pokeapi

STAT_KEYS = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
STAT_SHORT = {"hp": "HP", "attack": "ATK", "defense": "DEF",
              "special-attack": "SPA", "special-defense": "SPD", "speed": "SPE"}
STAT_CSS = {"hp": "stat-hp", "attack": "stat-atk", "defense": "stat-def",
            "special-attack": "stat-spa", "special-defense": "stat-spd", "speed": "stat-spe"}


def render_trainer_card(pokemon_data: dict, player: str):
    """Full trainer card with sprite, name, types, and stat bars."""
    if not pokemon_data:
        return

    name = pokemon_data.get("name", "???").upper()
    sprite_url = pokeapi.get_sprite_url(pokemon_data) or ""
    types = pokeapi.get_types(pokemon_data)
    stats = pokeapi.get_stats(pokemon_data)

    badges = "".join(
        f'<span class="type-badge type-{t.lower()}">{t.upper()}</span>' for t in types
    )

    stat_rows = ""
    for key in STAT_KEYS:
        val = stats.get(key, 0)
        pct = min(100, int(val / 255 * 100))
        css = STAT_CSS.get(key, "")
        short = STAT_SHORT.get(key, key[:3].upper())
        stat_rows += f"""
        <div class="stat-row {css}">
            <span class="stat-label">{short}</span>
            <div class="stat-bar-bg"><div class="stat-bar-fg" style="width:{pct}%"></div></div>
            <span class="stat-value">{val}</span>
        </div>"""

    header_cls = "tc-p1" if player == "p1" else "tc-p2"
    player_label = "PLAYER 1" if player == "p1" else "PLAYER 2"

    html = f"""
    <div class="trainer-card anim-enter">
        <div class="trainer-card-header {header_cls}"><span>{player_label}</span></div>
        <div class="trainer-card-body">
            <div class="trainer-card-sprite">
                <img src="{sprite_url}" alt="{name}" />
            </div>
            <div>
                <div class="trainer-card-name">{name}</div>
                <div class="trainer-card-types">{badges}</div>
            </div>
        </div>
        <div class="trainer-card-stats">{stat_rows}</div>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_compact_card(pokemon_data: dict, player: str):
    """Small card showing sprite + name + type badges inline."""
    if not pokemon_data:
        return

    name = pokemon_data.get("name", "???").upper()
    sprite_url = pokeapi.get_sprite_url(pokemon_data) or ""
    types = pokeapi.get_types(pokemon_data)
    badges = "".join(
        f'<span class="type-badge type-{t.lower()}">{t.upper()}</span>' for t in types
    )

    html = f"""
    <div class="compact-card">
        <img src="{sprite_url}" alt="{name}" />
        <div>
            <div class="compact-card-name">{name}</div>
            <div style="margin-top:4px">{badges}</div>
        </div>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_move_panel(move_data: dict):
    """Styled move detail panel with type-colored header."""
    if not move_data:
        return

    details = move_data.get("details", {})
    name = move_data.get("name", "???").replace("-", " ").upper()
    move_type = details.get("type", "normal").lower()
    power = details.get("power", "—")
    accuracy = details.get("accuracy", "—")
    dmg_class = details.get("damage_class", "—").upper()

    html = f"""
    <div class="move-panel anim-enter">
        <div class="move-panel-header type-{move_type}" style="background:inherit">
            <span class="move-name">{name}</span>
            <span class="type-badge type-{move_type}" style="font-size:7px">{move_type.upper()}</span>
        </div>
        <div class="move-panel-body">
            <div class="move-stat">
                <div class="move-stat-label">Power</div>
                <div class="move-stat-value">{power}</div>
            </div>
            <div class="move-stat">
                <div class="move-stat-label">Accuracy</div>
                <div class="move-stat-value">{accuracy}</div>
            </div>
            <div class="move-stat">
                <div class="move-stat-label">Type</div>
                <div class="move-stat-value">{move_type.upper()}</div>
            </div>
            <div class="move-stat">
                <div class="move-stat-label">Class</div>
                <div class="move-stat-value">{dmg_class}</div>
            </div>
        </div>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_move_selection(pokemon_data: dict, key_prefix: str) -> dict | None:
    """Move selectbox with styled detail panel below. Returns move dict or None."""
    if not pokemon_data:
        return None

    move_names = pokeapi.get_move_names(pokemon_data)
    if not move_names:
        st.warning("No moves found for this Pokémon.")
        return None

    pokemon_name = pokemon_data.get("name", "unknown")
    with st.spinner(f"Loading moves for {pokemon_name.title()}..."):
        valid_moves = pokeapi.get_valid_damaging_move_names(pokemon_name, tuple(move_names))

    if not valid_moves:
        st.warning("No damaging moves found.")
        return None

    selected = st.selectbox(
        "Select Move:",
        options=valid_moves,
        key=f"{key_prefix}_move_select",
        format_func=lambda m: m.replace("-", " ").title(),
    )

    if selected:
        with st.spinner(f"Loading {selected}..."):
            move_raw = pokeapi.fetch_move(selected)

        if not move_raw:
            st.error("Failed to load move data.")
            return None

        details = pokeapi.get_move_details(move_raw)
        result = {"name": selected, "data": move_raw, "details": details}
        render_move_panel(result)
        return result

    return None


def render_arena_preview(p1_data: dict | None, p2_data: dict | None):
    """Battle arena preview showing selected sprites (or placeholders)."""
    p1_html = _sprite_or_placeholder(p1_data, "P1")
    p2_html = _sprite_or_placeholder(p2_data, "P2")

    html = f"""
    <div class="arena-preview">
        {p1_html}
        <div class="arena-preview-vs">VS</div>
        {p2_html}
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


def _sprite_or_placeholder(pdata: dict | None, label: str) -> str:
    if pdata:
        url = pokeapi.get_sprite_url(pdata) or ""
        name = pdata.get("name", "").upper()
        return f'<div style="text-align:center"><img src="{url}" alt="{name}" class="arena-preview" style="border:none;box-shadow:none;min-height:auto;padding:0;margin:0;display:inline;width:96px;height:96px" /><div style="font-family:var(--font-pixel);font-size:8px;color:rgba(255,255,255,0.7);margin-top:4px">{name}</div></div>'
    return f'<div class="arena-preview-placeholder">{label}</div>'


def render_type_matchup(p1_data: dict, p2_data: dict, p1_move: dict, p2_move: dict):
    """Show type effectiveness for each player's move vs the opponent."""
    st.markdown('<div class="section-title">Type Matchup Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        _render_single_matchup(p1_data, p2_data, p1_move, "P1")
    with col2:
        _render_single_matchup(p2_data, p1_data, p2_move, "P2")


def _render_single_matchup(attacker: dict, defender: dict, move: dict, label: str):
    move_type = move.get("details", {}).get("type", "normal")
    defender_types = pokeapi.get_types(defender)
    mult = pokeapi.effectiveness_multiplier(move_type, defender_types)

    atk_name = attacker.get("name", "???").title()
    def_name = defender.get("name", "???").title()
    move_name = move.get("name", "???").replace("-", " ").title()

    if mult >= 2.0:
        css, text = "mult-super", f"×{mult:.0f} SUPER EFFECTIVE!"
    elif mult == 0:
        css, text = "mult-immune", "×0 NO EFFECT"
    elif mult < 1.0:
        css, text = "mult-resist", f"×{mult:.1f} Not very effective"
    else:
        css, text = "mult-normal", f"×{mult:.0f} Normal"

    html = f"""
    <div class="matchup-row">
        <span class="matchup-label">{atk_name}'s {move_name} → {def_name}</span>
        <span class="matchup-mult {css}">{text}</span>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


def render_winner_banner(results: dict, p1_data: dict, p2_data: dict):
    """Celebratory winner banner or draw announcement."""
    winner = results.get("winner", "Draw")
    is_draw = winner == "Draw"

    if is_draw:
        html = """
        <div class="winner-banner draw-banner">
            <div class="winner-banner-content">
                <div class="winner-title">BATTLE RESULT</div>
                <div class="winner-name" style="color:var(--pkmn-text-muted)">DRAW!</div>
                <div class="winner-subtitle">Neither Pokémon could finish the other.</div>
            </div>
        </div>"""
    else:
        winner_slot = results.get("winner_slot")
        if winner_slot == "p1":
            winner_pokemon = p1_data
        elif winner_slot == "p2":
            winner_pokemon = p2_data
        else:
            winner_pokemon = p1_data if winner.casefold() == p1_data["name"].casefold() else p2_data

        sprite_url = pokeapi.get_sprite_url(winner_pokemon) or ""
        display_name = winner.upper()

        html = f"""
        <div class="winner-banner">
            <div class="winner-banner-content">
                <div class="winner-title">★ WINNER ★</div>
                <div class="winner-sprite"><img src="{sprite_url}" alt="{display_name}" /></div>
                <div class="winner-name">{display_name}</div>
                <div class="winner-subtitle">wins the battle!</div>
            </div>
        </div>"""

    st.markdown(html, unsafe_allow_html=True)


def render_step_indicator(current_step: int):
    """5-step progress indicator styled as pixel game tabs."""
    names = ["SELECT", "MOVES", "COMPARE", "BATTLE!", "RESULTS"]
    icons = ["①", "②", "③", "④", "⑤"]

    items = ""
    for i, (icon, name) in enumerate(zip(icons, names), 1):
        if i == current_step:
            cls = "step-active"
        elif i < current_step:
            cls = "step-done"
        else:
            cls = "step-pending"
        items += f'<div class="step-item {cls}"><span>{icon}</span> <span>{name}</span></div>'
        if i < 5:
            conn_cls = "connector-done" if i < current_step else "connector-pending"
            items += f'<div class="step-connector {conn_cls}"></div>'

    st.markdown(f'<div class="step-indicator">{items}</div>', unsafe_allow_html=True)


def render_top_bar():
    """Title bar matching the game aesthetic."""
    st.markdown("""
    <div class="top-bar">
        <div class="top-bar-title">⚔ POKÉMON COMBAT SIMULATOR</div>
        <div class="top-bar-subtitle">GROUP 8 — MASTER DATA</div>
    </div>""", unsafe_allow_html=True)


def render_dialogue(message: str):
    """Bottom dialogue box like Pokémon's text panel."""
    st.markdown(
        f'<div class="dialogue-box"><span class="dialogue-text">{message}</span></div>',
        unsafe_allow_html=True,
    )


def render_section_title(text: str):
    """Section heading with pixel accent."""
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def render_pokemon_info(pokemon_data: dict):
    """Legacy renderer kept for backwards compatibility."""
    render_trainer_card(pokemon_data, "p1")
