"""Streamlit wrapper for the 3D flame (frontend lives in ./frontend)."""
from pathlib import Path
import streamlit.components.v1 as components

_component = components.declare_component("flame3d", path=str(Path(__file__).parent / "frontend"))

def flame3d(rate, gravity, o2, flow, status="IN", reduce_motion=False, illustration=False, height=480):
    """Render the flame. Fixed key keeps the iframe (and the user's camera) alive across reruns.
    rate: mm/s or None when there is no prediction; gravity: 0 or 1; status: IN | SPARSE | OUT."""
    return _component(rate=None if rate is None else float(rate), gravity=float(gravity), o2=float(o2),
                      flow=float(flow), status=status, reduce_motion=bool(reduce_motion),
                      illustration=bool(illustration), height=int(height), key="sim", default=None)
