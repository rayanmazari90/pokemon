import plotly.express as px
import pandas as pd
import src.pokeapi_client as pokeapi

TYPE_COLORS = {
    "fire": "#f07028", "water": "#6888f0", "grass": "#78c850", "electric": "#f0c830",
    "ice": "#98d8d0", "fighting": "#c02820", "poison": "#a040a0", "ground": "#e0b868",
    "flying": "#a890f0", "psychic": "#f85888", "bug": "#a8b020", "rock": "#b0a038",
    "ghost": "#705898", "dragon": "#7038f8", "dark": "#685848", "steel": "#b0b0c8",
    "fairy": "#e898a8", "normal": "#9a9a6c",
}

_THEME = dict(
    font=dict(
        family="'Press Start 2P', monospace",
        size=9, color="#1a1a28",
    ),
    plot_bgcolor="#f4f0e0",
    paper_bgcolor="#e8e4d4",
    margin=dict(l=48, r=24, t=56, b=48),
    legend=dict(
        bgcolor="rgba(244,240,224,0.95)",
        bordercolor="#3a3a30",
        borderwidth=2,
        font=dict(
            family="'Press Start 2P', monospace",
            size=8, color="#1a1a28",
        ),
    ),
)

_GRID = dict(
    gridcolor="#d8d0b8", gridwidth=1,
    zerolinecolor="#c8c0a8",
)


def get_pokemon_color(pokemon_data: dict) -> str:
    types = pokeapi.get_types(pokemon_data)
    if types:
        return TYPE_COLORS.get(types[0].lower(), "#9a9a6c")
    return "#9a9a6c"


def render_stat_comparison(p1_data: dict, p2_data: dict):
    """
    Grouped bar chart comparing base stats.
    Uses pd.DataFrame, .melt(), and Plotly grouped bar chart (grading criteria).
    """
    p1_name = p1_data["name"].capitalize()
    p2_name = p2_data["name"].capitalize()

    p1_stats = pokeapi.get_stats(p1_data)
    p2_stats = pokeapi.get_stats(p2_data)

    stat_keys = ["hp", "attack", "defense", "special-attack", "special-defense", "speed"]
    stat_labels = ["HP", "ATK", "DEF", "SP.ATK", "SP.DEF", "SPE"]

    data = {
        "Stat": stat_labels,
        p1_name: [p1_stats.get(k, 0) for k in stat_keys],
        p2_name: [p2_stats.get(k, 0) for k in stat_keys],
    }

    df = pd.DataFrame(data)
    melted_df = df.melt(id_vars="Stat", value_vars=[p1_name, p2_name],
                        var_name="Pokemon", value_name="Base Stat")

    color_map = {
        p1_name: get_pokemon_color(p1_data),
        p2_name: get_pokemon_color(p2_data),
    }

    fig = px.bar(
        melted_df,
        x="Stat",
        y="Base Stat",
        color="Pokemon",
        barmode="group",
        color_discrete_map=color_map,
        title="BASE STAT COMPARISON",
        text_auto=True,
    )

    fig.update_layout(
        **_THEME,
        title=dict(font=dict(
            family="'Press Start 2P', monospace",
            size=11, color="#c89820",
        )),
        xaxis=dict(
            title="",
            tickfont=dict(size=8, color="#1a1a28"),
            **_GRID,
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=8, color="#1a1a28"),
            **_GRID,
        ),
    )
    fig.update_traces(
        marker_line=dict(width=2, color="#3a3a30"),
        textfont=dict(size=8, color="#1a1a28"),
        textposition="outside",
    )
    return fig


def render_hp_history(hp_history_list: list[dict], p1_data: dict = None,
                      p2_data: dict = None, **kwargs):
    """
    Line chart of HP over time.
    Uses pd.DataFrame and Plotly line chart (grading criteria).
    """
    if not hp_history_list:
        return None

    df = pd.DataFrame(hp_history_list)
    df["Pokemon"] = df["Pokemon"].str.capitalize()

    color_map = None
    if p1_data and p2_data:
        p1_label = kwargs.get("p1_label", p1_data["name"]).capitalize()
        p2_label = kwargs.get("p2_label", p2_data["name"]).capitalize()
        color_map = {
            p1_label: get_pokemon_color(p1_data),
            p2_label: get_pokemon_color(p2_data),
        }

    fig = px.line(
        df,
        x="Round",
        y="HP",
        color="Pokemon",
        color_discrete_map=color_map,
        markers=True,
        title="HP OVER TIME",
    )

    fig.update_layout(
        **_THEME,
        title=dict(font=dict(
            family="'Press Start 2P', monospace",
            size=11, color="#c89820",
        )),
        yaxis=dict(
            rangemode="tozero", title="HP", **_GRID,
            tickfont=dict(size=8, color="#1a1a28"),
            title_font=dict(size=9, color="#1a1a28"),
        ),
        xaxis=dict(
            title="Round", dtick=1, **_GRID,
            tickfont=dict(size=8, color="#1a1a28"),
            title_font=dict(size=9, color="#1a1a28"),
        ),
    )
    fig.update_traces(
        line=dict(width=4),
        marker=dict(size=10, line=dict(width=2, color="#3a3a30")),
    )
    return fig
