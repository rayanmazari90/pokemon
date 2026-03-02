import requests
import streamlit as st
import logging
import concurrent.futures

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "https://pokeapi.co/api/v2"

@st.cache_data(show_spinner=False)
def fetch_pokemon(name: str) -> dict | None:
    """Fetches Pokemon data from the API."""
    if not name:
        return None
    try:
        response = requests.get(f"{BASE_URL}/pokemon/{name.lower().strip()}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching pokemon {name}: {e}")
        return None

@st.cache_data(show_spinner=False)
def fetch_move(name: str) -> dict | None:
    """Fetches move data from the API."""
    if not name:
        return None
    try:
        response = requests.get(f"{BASE_URL}/move/{name.lower().strip()}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching move {name}: {e}")
        return None

@st.cache_data(show_spinner=False)
def fetch_type(name: str) -> dict | None:
    """Fetches type data from the API."""
    if not name:
        return None
    try:
        response = requests.get(f"{BASE_URL}/type/{name.lower().strip()}", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching type {name}: {e}")
        return None

def get_sprite_url(pokemon_json: dict) -> str | None:
    """Extracts the animated sprite URL or falls back to front_default."""
    if not pokemon_json:
        return None
    sprites = pokemon_json.get("sprites", {})
    # Try to find the Black/White animated sprite
    try:
        animated_sprite = sprites.get("versions", {}).get("generation-v", {}).get("black-white", {}).get("animated", {}).get("front_default")
        if animated_sprite:
            return animated_sprite
    except Exception:
        pass
    
    # Fallback to standard front_default
    return sprites.get("front_default")

def get_stats(pokemon_json: dict) -> dict:
    """Extracts a dictionary of base stats."""
    if not pokemon_json:
        return {}
    stats = {}
    for stat_info in pokemon_json.get("stats", []):
        stat_name = stat_info.get("stat", {}).get("name")
        base_stat = stat_info.get("base_stat")
        if stat_name and base_stat is not None:
            stats[stat_name] = base_stat
    return stats

def get_types(pokemon_json: dict) -> list[str]:
    """Extracts a list of type names for the pokemon."""
    if not pokemon_json:
        return []
    return [t.get("type", {}).get("name") for t in pokemon_json.get("types", []) if t.get("type", {}).get("name")]

def get_move_names(pokemon_json: dict) -> list[str]:
    """Extracts a list of all move names available to the pokemon."""
    if not pokemon_json:
        return []
    return [m.get("move", {}).get("name") for m in pokemon_json.get("moves", []) if m.get("move", {}).get("name")]

def get_move_details(move_json: dict) -> dict:
    """Extracts relevant details about a move."""
    if not move_json:
        return {}
    return {
        "power": move_json.get("power"),
        "accuracy": move_json.get("accuracy"),
        "type": move_json.get("type", {}).get("name"),
        "damage_class": move_json.get("damage_class", {}).get("name")
    }

@st.cache_data(show_spinner=False)
def get_valid_damaging_move_names(pokemon_name: str, move_names: tuple) -> list[str]:
    """
    Given a list of move names, concurrently fetches their details and 
    returns only those that are damaging (power > 0).
    """
    valid_moves = []
    
    # Use ThreadPoolExecutor for concurrent fetching
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # submit all fetch_move requests
        future_to_name = {executor.submit(fetch_move, name): name for name in move_names}
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            try:
                move_data = future.result()
                if move_data:
                    power = move_data.get("power")
                    if power is not None and power > 0:
                        valid_moves.append(name)
            except Exception as e:
                logger.error(f"Error checking move {name}: {e}")
                
    return sorted(valid_moves)

def effectiveness_multiplier(move_type: str, defender_types: list[str]) -> float:
    """
    Calculates the type effectiveness multiplier for a move type against a list of defender types.
    Multiplies the effect across dual types.
    """
    if not move_type or not defender_types:
        return 1.0
        
    type_data = fetch_type(move_type)
    if not type_data:
        return 1.0 # Fallback in case of API error
        
    damage_relations = type_data.get("damage_relations", {})
    
    double_damage_to = {t["name"] for t in damage_relations.get("double_damage_to", [])}
    half_damage_to = {t["name"] for t in damage_relations.get("half_damage_to", [])}
    no_damage_to = {t["name"] for t in damage_relations.get("no_damage_to", [])}
    
    multiplier = 1.0
    for defender_type in defender_types:
        if defender_type in double_damage_to:
            multiplier *= 2.0
        elif defender_type in half_damage_to:
            multiplier *= 0.5
        elif defender_type in no_damage_to:
            multiplier *= 0.0
            
    return multiplier
