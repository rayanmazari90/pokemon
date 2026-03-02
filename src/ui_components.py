import streamlit as st
import pandas as pd
import src.pokeapi_client as pokeapi

def render_pokemon_info(pokemon_data: dict):
    """
    Renders the Pokémon's sprite, name, types, and stats in a clean UI.
    """
    if not pokemon_data:
        return
    
    # Sprite
    sprite_url = pokeapi.get_sprite_url(pokemon_data)
    if sprite_url:
        st.image(sprite_url, width=150)
    
    # Name & Types HTML
    name = pokemon_data.get("name", "Unknown").title()
    types = pokeapi.get_types(pokemon_data)
    
    badges_html = "".join([f'<span class="type-badge type-{t.lower()}">{t}</span>' for t in types])
    
    html_content = f"""
    <div class="pokemon-card">
        <h3 class="pkmn-text" style="margin-top:0;">{name}</h3>
        <div>{badges_html}</div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    
    # Stats Table
    stats_dict = pokeapi.get_stats(pokemon_data)
    if stats_dict:
        # Format stats for clean display in Streamlit
        st.markdown("**Base Stats:**")
        stats_df = pd.DataFrame(
            [stats_dict.values()],
            columns=[k.replace("-", " ").title() for k in stats_dict.keys()]
        )
        st.dataframe(stats_df, hide_index=True)


def render_move_selection(pokemon_data: dict, key_prefix: str) -> dict | None:
    """
    Renders move selection for the given Pokémon.
    Filters moves lazily (fetches only selected move) and blocks if move has no power.
    Returns the move details dict if valid, or None.
    """
    if not pokemon_data:
        return None
        
    move_names = pokeapi.get_move_names(pokemon_data)
    if not move_names:
        st.warning("No moves found for this Pokémon.")
        return None
        
    pokemon_name = pokemon_data.get("name", "unknown")
    with st.spinner(f"Loading valid damaging moves for {pokemon_name.title()}..."):
        valid_moves = pokeapi.get_valid_damaging_move_names(pokemon_name, tuple(move_names))
        
    if not valid_moves:
        st.warning("No damaging moves found for this Pokémon.")
        return None
        
    selected_move_name = st.selectbox(
        "Select a damaging move:",
        options=valid_moves,
        key=f"{key_prefix}_move_select"
    )
    
    if selected_move_name:
        with st.spinner(f"Fetching {selected_move_name} details..."):
            move_data = pokeapi.fetch_move(selected_move_name)
            
        if not move_data:
            st.error("Failed to load move data.")
            return None
            
        move_details = pokeapi.get_move_details(move_data)
        
        # Display valid move info
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Power", move_details.get("power"))
        col2.metric("Accuracy", move_details.get("accuracy", "N/A"))
        col3.metric("Type", move_details.get("type", "Unknown").title())
        col4.metric("Class", move_details.get("damage_class", "Unknown").title())
        
        # Return complete move data needed for engine
        return {
            "name": selected_move_name,
            "data": move_data,
            "details": move_details
        }
    
    return None

