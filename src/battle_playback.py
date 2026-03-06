import streamlit as st
import time
import src.pokeapi_client as pokeapi
import src.sound_engine as sound

_TYPE_TO_THEME = {
    "water": "arena-water",
    "fire": "arena-volcano",
    "ice": "arena-snow",
    "ghost": "arena-night",
    "dark": "arena-night",
    "rock": "arena-cave",
    "ground": "arena-cave",
    "electric": "arena-electric",
    "dragon": "arena-sky",
    "flying": "arena-sky",
}


def _pick_theme(p1_data, p2_data):
    """Choose an arena theme based on both Pokémon's types."""
    all_types = [
        t.lower()
        for t in pokeapi.get_types(p1_data) + pokeapi.get_types(p2_data)
    ]
    for t in all_types:
        if t in _TYPE_TO_THEME:
            return _TYPE_TO_THEME[t]
    return "arena-grass"


def play_battle_animation(p1, p2, battle_log, max_hp1, max_hp2):
    """
    Animated battle playback with sound effects, Pokémon-game layout,
    and type-based arena themes.
    """
    p1_name = p1["name"].title()
    p2_name = p2["name"].title()
    p1_sprite = (
        pokeapi.get_back_sprite_url(p1) or pokeapi.get_sprite_url(p1)
    )
    p2_sprite = pokeapi.get_sprite_url(p2)
    theme = _pick_theme(p1, p2)

    hp1 = max_hp1
    hp2 = max_hp2

    placeholder = st.empty()
    sound_ph = st.empty()

    def _hp_cls(pct):
        if pct <= 20:
            return "hp-low"
        if pct <= 50:
            return "hp-med"
        return ""

    def render_frame(msg, anim1="", anim2=""):
        hp1_pct = max(0, min(100, int((hp1 / max_hp1) * 100)))
        hp2_pct = max(0, min(100, int((hp2 / max_hp2) * 100)))

        html = f"""
<div class="battle-arena-box {theme}">
<div class="arena-row-top">
<div class="hp-hud">
<div class="hp-hud-name">{p2_name}</div>
<div class="hp-hud-bar-row">
<span class="hp-hud-label">HP</span>
<div class="hp-bar-bg"><div class="hp-bar-fg {_hp_cls(hp2_pct)}" style="width:{hp2_pct}%"></div></div>
</div>
<div class="hp-hud-values">{hp2} / {max_hp2}</div>
</div>
<div class="battle-sprite {anim2}">
<img src="{p2_sprite}" alt="{p2_name}" />
<div class="ground-shadow"></div>
</div>
</div>
<div class="arena-row-bottom">
<div class="battle-sprite {anim1}">
<img src="{p1_sprite}" alt="{p1_name}" />
<div class="ground-shadow ground-shadow-lg"></div>
</div>
<div class="hp-hud">
<div class="hp-hud-name">{p1_name}</div>
<div class="hp-hud-bar-row">
<span class="hp-hud-label">HP</span>
<div class="hp-bar-bg"><div class="hp-bar-fg {_hp_cls(hp1_pct)}" style="width:{hp1_pct}%"></div></div>
</div>
<div class="hp-hud-values">{hp1} / {max_hp1}</div>
</div>
</div>
</div>
<div class="dialogue-box-battle">{msg}</div>
"""
        placeholder.markdown(html, unsafe_allow_html=True)

    # ── Intro ───────────────────────────────────────────────────────
    sound.play("battle_start", sound_ph)
    render_frame(
        f"The battle begins!<br/>Go, {p1_name}! Go, {p2_name}!"
    )
    time.sleep(1.5)

    # ── Turn loop ───────────────────────────────────────────────────
    for entry in battle_log:
        attacker = entry["Attacker"]
        move = entry["Move"]
        damage = entry["Damage"]
        msg = entry["Message"]
        is_p1 = entry.get("AttackerSlot", "p1") == "p1"

        atk_text = (
            f"{attacker.title()} used "
            f"{move.replace('-', ' ').title()}!"
        )
        a1 = "anim-lunge-right" if is_p1 else ""
        a2 = "anim-lunge-left" if not is_p1 else ""

        # Attack animation + sound
        sound.play("attack", sound_ph)
        render_frame(atk_text, a1, a2)
        time.sleep(0.7)

        # Damage / miss
        if is_p1:
            hp2 = max(0, hp2 - damage)
            shake = "anim-shake" if damage > 0 else ""
            if damage > 0:
                sound.play("hit", sound_ph)
            else:
                sound.play("miss", sound_ph)
            render_frame(atk_text + "<br/>" + msg, "", shake)
        else:
            hp1 = max(0, hp1 - damage)
            shake = "anim-shake" if damage > 0 else ""
            if damage > 0:
                sound.play("hit", sound_ph)
            else:
                sound.play("miss", sound_ph)
            render_frame(atk_text + "<br/>" + msg, shake, "")

        time.sleep(0.5)

        # Effectiveness sound
        msg_lower = msg.lower()
        if "super effective" in msg_lower:
            sound.play("super_effective", sound_ph)
            time.sleep(0.4)
        elif "not very effective" in msg_lower:
            sound.play("not_effective", sound_ph)
            time.sleep(0.3)
        elif "no effect" in msg_lower:
            sound.play("not_effective", sound_ph)
            time.sleep(0.3)

        time.sleep(0.5)

        # Faint check
        if hp1 <= 0 or hp2 <= 0:
            f1 = " anim-faint" if hp1 <= 0 else ""
            f2 = " anim-faint" if hp2 <= 0 else ""
            loser = p2_name if hp2 <= 0 else p1_name
            sound.play("faint", sound_ph)
            render_frame(f"{loser} fainted!", f1, f2)
            time.sleep(1.5)
            break

    time.sleep(0.5)
    placeholder.empty()
    sound_ph.empty()
