
from __future__ import annotations

# Minimal stub for a future Dash-based live dashboard.
# This avoids requiring Dash at import time unless explicitly used.

def launch_dashboard():
    try:
        import dash
        from dash import dcc, html
        import dash_bootstrap_components as dbc  # optional
    except Exception as e:
        raise RuntimeError(
            "Dash-based visualization requires the 'viz' extra: "
            "pip install entropy_ecology_sim[viz]"
        ) from e

    app = dash.Dash(__name__)
    app.layout = html.Div(
        [
            html.H3("Entropy Ecology Simulator – Live Dashboard (stub)"),
            html.P("Replace this with real-time RSVP field visualizations."),
        ]
    )
    app.run_server(debug=True)
