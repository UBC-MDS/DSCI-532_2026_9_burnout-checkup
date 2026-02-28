# src/constants/theme.py
import altair as alt

COLORS = {
    "bg_sidebar": "#E6C9AD",
    "card_bg": "#D9B896",
    "dark_brown": "#5A2D0C",
    "medium_brown": "#8B4513",
    "light_orange": "#E6A96B",
    "soft_gold": "#F1C978",
    "deep_maroon": "#7A0C0C",
    "alert_red": "#D61E1E",
}

def deadline_scale():
    return alt.Scale(
        domain=["Low", "Medium", "High"],
        range=[COLORS["light_orange"], COLORS["medium_brown"], COLORS["dark_brown"]],
    )

def ai_band_scale():
    return alt.Scale(
        domain=["Low", "Medium", "High"],
        range=[COLORS["light_orange"], COLORS["medium_brown"], COLORS["dark_brown"]],
    )

def hours_breakdown_scale():
    return alt.Scale(
        domain=["Meetings", "Collaboration", "Deep work", "Manual work"],
        range=[
            COLORS["medium_brown"],
            COLORS["light_orange"],
            COLORS["deep_maroon"],
            COLORS["soft_gold"],
        ],
    )