import streamlit as st
import time
import src.pokeapi_client as pokeapi

def play_battle_animation(p1, p2, battle_log, max_hp1, max_hp2):
    """
    Plays an animated battle sequence using st.empty() and time.sleep().
    """
    p1_name = p1["name"].title()
    p2_name = p2["name"].title()
    p1_sprite = pokeapi.get_sprite_url(p1)
    p2_sprite = pokeapi.get_sprite_url(p2)
    
    hp1 = max_hp1
    hp2 = max_hp2
    
    placeholder = st.empty()
    
    def render_frame(msg, anim1="", anim2=""):
        hp1_pct = max(0, min(100, int((hp1 / max_hp1) * 100)))
        hp2_pct = max(0, min(100, int((hp2 / max_hp2) * 100)))
        
        hp1_class = "hp-low" if hp1_pct <= 20 else "hp-med" if hp1_pct <= 50 else ""
        hp2_class = "hp-low" if hp2_pct <= 20 else "hp-med" if hp2_pct <= 50 else ""
        
        # We remove all indentation and blank lines to prevent Streamlit's markdown parser from treating it as a code block.
        html = f"""
<div class="battle-stage">
<div class="pokemon-sprite-container {anim1}">
<div class="pkmn-text" style="font-size: 12px; margin-bottom: 5px;">{p1_name}</div>
<div class="hp-bar-bg"><div class="hp-bar-fg {hp1_class}" style="width: {hp1_pct}%;"></div></div>
<div class="pkmn-text" style="font-size: 10px; text-align: right; margin-bottom: 15px;">{hp1}/{max_hp1}</div>
<img src="{p1_sprite}" />
</div>
<div class="pokemon-sprite-container {anim2}">
<div class="pkmn-text" style="font-size: 12px; margin-bottom: 5px;">{p2_name}</div>
<div class="hp-bar-bg"><div class="hp-bar-fg {hp2_class}" style="width: {hp2_pct}%;"></div></div>
<div class="pkmn-text" style="font-size: 10px; text-align: right; margin-bottom: 15px;">{hp2}/{max_hp2}</div>
<img src="{p2_sprite}" />
</div>
</div>
<div class="gameboy-dialog" style="min-height: 80px;">{msg}</div>
"""
        placeholder.markdown(html, unsafe_allow_html=True)

    # Initial text
    render_frame(f"Ready to battle!<br/>Go {p1_name}! Go {p2_name}!")
    time.sleep(1.5)
    
    for log_entry in battle_log:
        attacker = log_entry["Attacker"]
        move = log_entry["Move"]
        damage = log_entry["Damage"]
        msg = log_entry["Message"]
        
        is_p1_attacking = (log_entry.get("AttackerSlot", "p1") == "p1")
        
        attack_msg = f"{attacker.title()} used {move.title()}!"
        anim1 = "anim-lunge-right" if is_p1_attacking else ""
        anim2 = "anim-lunge-left" if not is_p1_attacking else ""
        
        # 1. Attacker lunges
        render_frame(attack_msg, anim1, anim2)
        time.sleep(0.8)
        
        # Apply damage
        if is_p1_attacking:
            hp2 -= damage
            if hp2 < 0: hp2 = 0
            shake_anim = "anim-shake" if damage > 0 else ""
            # 2. Defender shakes and HP drops, while dialogue updates
            render_frame(attack_msg + "<br/>" + msg, "", shake_anim)
        else:
            hp1 -= damage
            if hp1 < 0: hp1 = 0
            shake_anim = "anim-shake" if damage > 0 else ""
            # 2. Defender shakes and HP drops, while dialogue updates
            render_frame(attack_msg + "<br/>" + msg, shake_anim, "")
            
        time.sleep(1.5)
        
        if hp1 <= 0 or hp2 <= 0:
            break
            
    time.sleep(0.5)
    placeholder.empty()
