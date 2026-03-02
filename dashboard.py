import pandas as pd
import streamlit as st
import src.ui_components as ui
import src.battle_engine as battle
import src.pokeapi_client as pokeapi
import src.charts as charts
import src.battle_playback as playback

@st.cache_data(show_spinner=False)
def fetch_all_pokemon_names() -> list[str]:
    """Fetches up to 2000 pokemon names from PokeAPI for the searchable dropdown."""
    import requests
    try:
        response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=2000", timeout=10)
        response.raise_for_status()
        return sorted([p["name"] for p in response.json().get("results", [])])
    except Exception:
        return []

def load_css(file_name: str):
    """Loads a CSS file and injects it into the Streamlit app."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def main():
    st.set_page_config(page_title="Pokemon Combat Simulator", layout="wide")
    load_css("ui.css")
    
    st.title("Pokemon Combat Simulator")
    st.markdown("Select two Pokémon and their moves to simulate a battle!")

    # Pre-fetch list of pokemon for the searchable dropdowns
    all_pokemon_names = fetch_all_pokemon_names()

    # State variables for Agent 5 and 3 to use later
    # We will store them in session state or as local variables depending on execution flow,
    # but for Streamlit, simple variables are fine since everything reruns.
    p1_pokemon = None
    p2_pokemon = None
    p1_move = None
    p2_move = None

    col1, col2 = st.columns(2)

    with col1:
        st.header("Player 1")
        p1_selection_method = st.radio("Selection Method:", ["Type name", "Search dropdown"], key="p1_method", horizontal=True)
        
        if p1_selection_method == "Type name":
            p1_name = st.text_input("Enter Pokémon Name:", value="pikachu", key="p1_input")
        else:
            default_idx = all_pokemon_names.index("pikachu") if "pikachu" in all_pokemon_names else 0
            p1_name = st.selectbox("Search Pokémon:", options=all_pokemon_names, index=default_idx, key="p1_select")
            
        if p1_name:
            with st.spinner(f"Fetching {p1_name}..."):
                p1_pokemon_data = pokeapi.fetch_pokemon(p1_name)
            
            if p1_pokemon_data:
                p1_pokemon = p1_pokemon_data
                ui.render_pokemon_info(p1_pokemon_data)
                
                st.markdown("### Move Selection")
                p1_move_data = ui.render_move_selection(p1_pokemon_data, key_prefix="p1")
                if p1_move_data:
                    p1_move = p1_move_data
            else:
                st.error(f"Could not find Pokémon '{p1_name}'. Please check the spelling.")

    with col2:
        st.header("Player 2")
        p2_selection_method = st.radio("Selection Method:", ["Type name", "Search dropdown"], key="p2_method", horizontal=True)
        
        if p2_selection_method == "Type name":
            p2_name = st.text_input("Enter Pokémon Name:", value="bulbasaur", key="p2_input")
        else:
            default_idx = all_pokemon_names.index("bulbasaur") if "bulbasaur" in all_pokemon_names else 0
            p2_name = st.selectbox("Search Pokémon:", options=all_pokemon_names, index=default_idx, key="p2_select")
            
        if p2_name:
            with st.spinner(f"Fetching {p2_name}..."):
                p2_pokemon_data = pokeapi.fetch_pokemon(p2_name)
            
            if p2_pokemon_data:
                p2_pokemon = p2_pokemon_data
                ui.render_pokemon_info(p2_pokemon_data)
                
                st.markdown("### Move Selection")
                p2_move_data = ui.render_move_selection(p2_pokemon_data, key_prefix="p2")
                if p2_move_data:
                    p2_move = p2_move_data
            else:
                st.error(f"Could not find Pokémon '{p2_name}'. Please check the spelling.")

    st.markdown("---")
    
    # ----------------------------------------------------
    # PLACEHOLDER for Agent 5 (Charts) and Agent 3 (Battle)
    # ----------------------------------------------------
    # Both Pokemon and their moves are valid if the condition below is met:
    if p1_pokemon and p2_pokemon and p1_move and p2_move:
        
        # Stat Comparison Chart
        st.markdown("### Base Stat Comparison")
        stat_fig = charts.render_stat_comparison(p1_pokemon, p2_pokemon)
        st.plotly_chart(stat_fig, use_container_width=True)

        st.markdown("---")

        show_playback = st.checkbox("Show Battle Playback (Animations)", value=False)

        # Battle Button
        if st.button("Battle!", type="primary", use_container_width=True):
            # Prep data for engine
            p1_combat_data = {
                "name": p1_pokemon["name"],
                "stats": pokeapi.get_stats(p1_pokemon),
                "types": pokeapi.get_types(p1_pokemon),
                "move": {"name": p1_move["name"], **p1_move.get("details", {})}
            }
            p2_combat_data = {
                "name": p2_pokemon["name"],
                "stats": pokeapi.get_stats(p2_pokemon),
                "types": pokeapi.get_types(p2_pokemon),
                "move": {"name": p2_move["name"], **p2_move.get("details", {})}
            }
            
            engine = battle.BattleEngine(p1_combat_data, p2_combat_data, pokeapi.effectiveness_multiplier)
            
            with st.spinner("Simulating Battle..."):
                results = engine.run_battle()
                
            if show_playback:
                playback.play_battle_animation(
                    p1_pokemon, 
                    p2_pokemon, 
                    results["battle_log"], 
                    p1_combat_data["stats"]["hp"], 
                    p2_combat_data["stats"]["hp"]
                )
                
            # Announce winner
            st.markdown("### Results")
            if results["winner"] == "Draw":
                msg = "The battle ended in a Draw!"
            else:
                msg = f"{results['winner'].capitalize()} wins the battle!"
                
            st.markdown(f'<div class="gameboy-dialog">{msg}</div>', unsafe_allow_html=True)
                
            # Display HP History Chart
            hp_fig = charts.render_hp_history(results["hp_history"])
            if hp_fig:
                st.plotly_chart(hp_fig, use_container_width=True)
                
            # Display Battle Log DataFrame
            st.markdown("### Battle Log")
            log_df = pd.DataFrame(results["battle_log"])
            
            # Formatting the Log DataFrame
            if not log_df.empty:
                log_df["Round"] = "Round " + log_df["Round"].astype(str)
                log_df = log_df[["Round", "Attacker", "Move", "Defender", "Damage", "Message"]]
            
            st.dataframe(log_df, use_container_width=True, hide_index=True)
            
    else:
        st.warning("Please select valid Pokémon and a damaging move for both players to proceed.")

if __name__ == "__main__":
    main()

