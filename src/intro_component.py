"""
src/intro_component.py
───────────────────────
Full-screen video intro component for the Pokémon Combat Simulator.

Design rationale
────────────────
Why not st.components.v1.html()?
  Streamlit sandboxes components.html() iframes with
  sandbox="allow-scripts allow-same-origin" — the flag allow-top-navigation
  is intentionally absent.  Any attempt to set window.parent.location.href
  inside the iframe raises a browser SecurityError and the button does nothing.

Why not a floating Streamlit button via position:fixed CSS?
  CSS injected from st.markdown cannot reliably move native Streamlit widgets
  (they live in a separate stacking context).  The button may render underneath
  the overlay or not at all depending on Streamlit's internal render order.

Chosen approach — st.markdown overlay + st.form
  1. st.markdown injects a full-screen position:fixed black overlay (video).
     Because this runs in the top document (not an iframe) the CSS applies.
  2. A native st.form with a single submit button is rendered *after* the
     overlay in the document flow.  CSS positions the form over the overlay
     (z-index > overlay) so it is visible and clickable.
  3. st.form batches the submit atomically — Streamlit guarantees the widget
     state is committed before the next rerun, so intro_done is always set
     before st.rerun() fires.  No stuck-spinner race condition.
"""

import base64
import streamlit as st

VIDEO_PATH = "assets/Pokemon_loading_screen_group_8_delpmaspu_-2.mp4"


@st.cache_data(show_spinner=False)
def _load_video_b64() -> str:
    """Read and base64-encode the intro video once (cached across reruns)."""
    with open(VIDEO_PATH, "rb") as f:
        return base64.b64encode(f.read()).decode()


def show_intro_screen() -> None:
    """
    Render a full-screen video intro and block until the user dismisses it.

    Call this at the very top of main(), before any other st.* calls.
    """
    # Already dismissed — nothing to do
    if st.session_state.get("intro_done", False):
        return

    # ── Load video ─────────────────────────────────────────────────────────
    try:
        video_b64 = _load_video_b64()
        video_src = f"data:video/mp4;base64,{video_b64}"
    except FileNotFoundError:
        st.session_state["intro_done"] = True
        return

    # ── Inject the overlay + CSS for the form button ────────────────────────
    # The form is rendered as a normal DOM element after the overlay div.
    # We position it fixed over the overlay using a CSS rule that targets
    # the Streamlit form wrapper by its data-testid.
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');

/* ── Full-screen overlay ────────────────────────────────────────────── */
#intro-overlay {{
    position: fixed;
    inset: 0;
    z-index: 9000;
    background: #000;
    display: flex;
    align-items: center;
    justify-content: center;
    pointer-events: none;   /* let clicks pass through to the form below */
}}
#intro-overlay video {{
    width: 100%;
    height: 100%;
    object-fit: contain;
}}

/* ── Hide all Streamlit chrome during intro ─────────────────────────── */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stSidebar"] {{
    display: none !important;
}}

/* ── Hide the default form border/background ─────────────────────────── */
[data-testid="stForm"] {{
    border: none !important;
    background: transparent !important;
    padding: 0 !important;
}}

/* ── Float the ENTIRE form block over the video ─────────────────────── */
/* Use attribute-only selector — Streamlit renders stMain as <section> */
[data-testid="stMain"] [data-testid="stForm"],
[data-testid="stMain"] [data-testid="stFormSubmitButton"] {{
    position: fixed !important;
    bottom: 60px !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    z-index: 9999 !important;
    pointer-events: all !important;
    width: auto !important;
}}

/* ── Style the submit button — always visible ───────────────────────── */
[data-testid="stFormSubmitButton"] > button,
[data-testid="stForm"] button {{
    background: rgba(0, 0, 0, 0.55) !important;
    border: 2px solid rgba(255, 255, 255, 0.9) !important;
    color: #fff !important;
    font-family: 'Press Start 2P', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 3px !important;
    padding: 16px 36px !important;
    min-width: 320px !important;
    border-radius: 3px !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    opacity: 1 !important;
    visibility: visible !important;
    box-shadow: 0 0 24px rgba(255, 255, 255, 0.25), 0 0 60px rgba(255, 255, 255, 0.08) !important;
    animation: ps-blink 1.2s step-end infinite !important;
    transition: background 0.15s, box-shadow 0.15s !important;
}}
[data-testid="stFormSubmitButton"] > button:hover,
[data-testid="stForm"] button:hover {{
    background: rgba(255, 255, 255, 0.18) !important;
    box-shadow: 0 0 32px rgba(255, 255, 255, 0.45) !important;
    animation: none !important;
    opacity: 1 !important;
}}
/* Blink between full opacity and 0.35 so it's always readable */
@keyframes ps-blink {{ 50% {{ opacity: 0.35; }} }}
</style>

<div id="intro-overlay">
  <video autoplay muted playsinline>
    <source src="{video_src}" type="video/mp4">
  </video>
</div>
""", unsafe_allow_html=True)

    # ── Native Streamlit form — atomic submit, no race conditions ───────────
    # clear_on_submit=True ensures the button state is flushed before rerun.
    with st.form("intro_form", clear_on_submit=True, border=False):
        submitted = st.form_submit_button(
            "▶   PRESS START   ◀",
            use_container_width=False,
            type="primary",
        )

    if submitted:
        st.session_state["intro_done"] = True
        st.rerun()

    # Block the rest of the dashboard from rendering
    st.stop()
