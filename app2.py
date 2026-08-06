import pandas as pd
import plotly.express as px
import streamlit as st
import datetime
from sqlalchemy import create_engine

# --- 1. PAGE CONFIG & COMPACT CSS ---
st.set_page_config(
    page_title="Cumulative Daily Avg. Occupancy Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    /* --- GLOBAL BACKGROUND COLOR --- */
/* --- GLOBAL BACKGROUND (OPERATIONAL DOT GRID) --- */
/* --- GLOBAL BACKGROUND (SUBTLE DIAGONAL LINES) --- */
    .stApp {
        background-color: #A7C7E7 !important;
        background-image: repeating-linear-gradient(
            -45deg,
            transparent,
            transparent 10px,
            rgba(255, 255, 255, 0.2) 10px,
            rgba(255, 255, 255, 0.2) 11px
        ) !important;
    }

    /* Make the top padding area transparent so it blends */
    [data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* Compact spacing to fit on a single screen */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    [data-testid="stVerticalBlock"] {
        gap: 0.4rem !important;
    }
    .main-title {
        font-size: 22px !important;;
        font-weight: 800;
        color: #1f3b73;
        text-align: left;
        margin-bottom: -5px;
    }

    /* --- BULLETPROOF BLACK BORDER FOR CONTAINERS --- */
    /* Target the main wrapper directly to overwrite Streamlit's default gray border */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 6px !important;
        background-color: #BBDEFB !important; /* Soft blue */
        box-shadow: none !important; /* Force remove any default gray shadows */
        overflow: hidden !important; 
    }
    /* Ensure absolutely no inner borders are drawn to prevent double lines */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* --- METRIC CARDS --- */
    [data-testid="stMetric"] {
        background-color: #BBDEFB !important; /* Soft blue */
        padding: 2px 5px;
        border-radius: 6px;
        box-shadow: none !important;
    }
    [data-testid="stMetricLabel"] { font-weight: 800 !important; font-size: 12px !important; color: #333 !important; }
    [data-testid="stMetricValue"] { font-weight: 800 !important; font-size: 22px !important; color: #1f3b73 !important; }

    /* --- TABLE BORDERS & BACKGROUND --- */
    table {
        background-color: #BBDEFB !important; /* Soft blue */
        margin-bottom: 0px !important;
    }
    thead tr th {
        background-color: #0b3273 !important; 
        color: white !important;
        text-align: center !important; 
        font-weight: bold !important;
        font-size: 10px !important; 
        padding: 1px !important;
    }
    tbody tr td { 
        text-align: center !important; 
        font-size: 10px !important; 
        padding: 1px !important; 
        font-weight: 600 !important;
        color: black !important; 
    }

    /* --- RADIO BUTTONS & INPUT CONTROLS --- */
    [data-testid="stWidgetLabel"] p {
        font-weight: 800 !important;
        color: #0b3273 !important;
        font-size: 13px !important;
    }
    [data-testid="stRadio"] label p {
        font-weight: 800 !important;
        color: #1f3b73 !important;
        font-size: 12px !important;
    }
    div[role="radiogroup"] {
        border: 1px solid black !important;
        padding: 4px 10px !important;
        border-radius: 6px !important;
        background-color: #BBDEFB !important; /* Soft blue */
    }
    [data-testid="stDateInput"] > div {
        border-radius: 6px !important;
        background-color: #BBDEFB !important; /* Soft blue */
    }

    /* --- BLUE CHART HEADERS --- */
    .blue-header {
        background-color: #0b3273; 
        color: white; 
        font-weight: bold; 
        padding: 2px; 
        border-radius: 4px;
        font-size: 13px; 
        margin-bottom: 2px; 
        text-transform: uppercase;
        display: flex;
        align-items: center; 
        justify-content: center;
        min-height: 28px; 
        padding: 4px 10px;
        line-height: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
left_half, right_half = st.columns(2)

with left_half:
        # --- 2. HEADER & FILTERS ---
    st.markdown('<p class="main-title">Cumulative Daily Avg. Occupancy Dashboard</p>', unsafe_allow_html=True)

with right_half:
    filter_col1, filter_col2 = st.columns([1, 3])
    with filter_col1:
        selected_date = st.date_input("📅 Reporting Date", datetime.date.today())

# --- 3. LIVE DATA CONNECTION (60-Second Refresh) ---
@st.cache_data(ttl=60)
def get_data(target_date):
    """Fetches data from AWS RDS. Caches it for 60 seconds to prevent DB overload."""
    try:
        DB_USER = st.secrets["DB_USER"]
        DB_PASSWORD = st.secrets["DB_PASSWORD"]
        DB_HOST = st.secrets["DB_HOST"]
        DB_PORT = st.secrets["DB_PORT"]
        DB_NAME = st.secrets["DB_NAME"]

        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

        query = "SELECT location, total, occupied, occupancy_percentage, daily_average_occupancy, operating_days FROM your_table"
        df = pd.read_sql(query, engine)
        return df

    except Exception as e:
        return pd.DataFrame({
            "location": ["PanjTarni", "Baltal", "Pantha Chowk", "Nunwan"],
            "total": [888, 8132, 13660, 19272],
            "occupied": [719, 6376, 9635, 12336],
            "occupancy_percentage": [80.97, 78.41, 70.53, 64.01],
            "daily_average_occupancy": [36, 319, 482, 617],
            "operating_days": [20, 20, 20, 20],
        })


raw_df = get_data(selected_date)

# FILTER


with filter_col2:
    location_options = ["All Locations"] + list(raw_df["location"].unique())
    selected_location = st.selectbox("📍 Filter by Location", options=location_options)

# Apply Filter
if selected_location == "All Locations":
    df = raw_df
else:
    df = raw_df[raw_df["location"] == selected_location]
# --- 4. CALCULATE DYNAMIC METRICS ---
if not df.empty:
    total_acc = df["total"].sum()
    total_occ = df["occupied"].sum()
    overall_occupancy = (total_occ / total_acc) * 100 if total_acc > 0 else 0
    total_days = df["operating_days"].max()
    total_daily_avg = df["daily_average_occupancy"].sum()
else:
    total_acc = total_occ = overall_occupancy = total_days = total_daily_avg = 0

# --- 5. TOP ROW: BOXED METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="🏢 TOTAL ACCOMMODATION", value=f"{total_acc:,.0f}")
with col2:
    st.metric(label="👥 TOTAL OCCUPIED", value=f"{total_occ:,.0f}")
with col3:
    st.metric(label="🍩 OVERALL OCCUPANCY", value=f"{overall_occupancy:.2f}%")
with col4:
    st.metric(label="📅 OPERATIONAL DAYS", value=f"{total_days}")

# --- 6. MIDDLE SECTION: TABLE & KEY INSIGHTS ---
mid_col1, mid_col2 = st.columns([2.5, 1])

with mid_col1:
    with st.container():
        if not df.empty:
            display_df = df.copy()
            display_df["occupancy_percentage"] = display_df["occupancy_percentage"].apply(lambda x: f"{x:.2f}%")

            display_df.columns = [
                "📍 Location", "🏢 Total Accommodation", "👥 Total Occupied",
                "⏱ Occupancy %", "📈 Cumulative Daily Avg.", "📅 Days"
            ]

            total_row = pd.DataFrame([{
                "📍 Location": "TOTAL", "🏢 Total Accommodation": f"{total_acc:,.0f}",
                "👥 Total Occupied": f"{total_occ:,.0f}", "⏱ Occupancy %": f"{overall_occupancy:.2f}%",
                "📈 Cumulative Daily Avg.": total_daily_avg, "📅 Days": total_days
            }])
            display_df = pd.concat([display_df, total_row], ignore_index=True)
            st.table(display_df)
        else:
            st.warning("No data available for the selected filters.")

with mid_col2:
    if not df.empty:
        highest_loc = df.loc[df["occupancy_percentage"].idxmax()]
        lowest_loc = df.loc[df["occupancy_percentage"].idxmin()]
        high_avg_loc = df.loc[df["daily_average_occupancy"].idxmax()]

        insights_html = f"""
        <div style=" border-radius: 6px; background-color: #BBDEFB; height: 100%; box-sizing: border-box;">
            <div style="background-color: #0b3273; color: white; text-align: center; font-weight: bold; padding: 1px; border-radius: 4px; font-size: 13px; text-transform: uppercase; overflow: hidden;">
                💡 Key Insights
            </div>
            <div style="font-size: 13.5px; color: black; padding: 5px 15px; line-height: 2.2;">
                <b>📈 Highest:</b> {highest_loc['location']} ({highest_loc['occupancy_percentage']:.2f}%)<br>
                <b>📉 Lowest:</b> {lowest_loc['location']} ({lowest_loc['occupancy_percentage']:.2f}%)<br>
                <b>👥 High Avg:</b> {high_avg_loc['location']} ({high_avg_loc['daily_average_occupancy']})<br>
                <b>🍩 Overall:</b> {overall_occupancy:.2f}%
            </div>
        </div>
        """
        st.markdown(insights_html, unsafe_allow_html=True)
    else:
        st.write("Insufficient data.")
# --- 7. BOTTOM SECTION: PLOTLY CHARTS IN BOXES ---
chart_col1, chart_col2 = st.columns(2)

def apply_bold_chart_styling(fig, xaxis_title):
    fig.update_layout(
        height=150,
        xaxis_title=xaxis_title, yaxis_title="", showlegend=False,
        margin=dict(l=1, r=1, t=1, b=1),
        font=dict(family="Arial", size=11, color="black"),
        xaxis=dict(showline=True, linewidth=2, linecolor="black", mirror=True,
                   tickfont=dict(size=11, color="black", weight="bold")),
        yaxis=dict(showline=True, linewidth=2, linecolor="black", mirror=True,
                   tickfont=dict(size=11, color="black", weight="bold")),
        plot_bgcolor="#BBDEFB",
        paper_bgcolor="#BBDEFB",
    )
    return fig


with chart_col1:
    with st.container():
        st.markdown('<div class="blue-header">Occupancy % by Location</div>', unsafe_allow_html=True)
        if not df.empty:
            df_sorted_occ = df.sort_values(by="occupancy_percentage", ascending=True)
            fig_occ = px.bar(
                df_sorted_occ, x="occupancy_percentage", y="location", orientation="h",
                text="occupancy_percentage", color="location",
                color_discrete_sequence=["#4B0082", "#228B22", "#FF8C00", "#1E90FF"]
            )
            fig_occ.update_traces(width=0.5, texttemplate="%{text:.2f}%", textposition="outside",
                                  textfont=dict(weight="bold", color="black"))
            fig_occ = apply_bold_chart_styling(fig_occ, "Occupancy %")
            fig_occ.update_layout(xaxis=dict(range=[0, 100]))
            st.plotly_chart(fig_occ, use_container_width=True, config={'displayModeBar': False})

with chart_col2:
    with st.container():
        st.markdown('<div class="blue-header">Cumulative Daily Avg. Occupancy</div>', unsafe_allow_html=True)
        if not df.empty:
            df_sorted_avg = df.sort_values(by="daily_average_occupancy", ascending=True)
            fig_avg = px.bar(
                df_sorted_avg, x="daily_average_occupancy", y="location", orientation="h",
                text="daily_average_occupancy", color="location",
                color_discrete_sequence=["#4B0082", "#228B22", "#FF8C00", "#1E90FF"]
            )
            fig_avg.update_traces(width=0.5, texttemplate="%{text}", textposition="outside",
                                  textfont=dict(weight="bold", color="black"))

            max_val = df_sorted_avg["daily_average_occupancy"].max()
            x_range = max_val + (max_val * 0.2) if max_val > 0 else 700

            fig_avg = apply_bold_chart_styling(fig_avg, "Avg. Occupancy")
            fig_avg.update_layout(xaxis=dict(range=[0, x_range]))
            st.plotly_chart(fig_avg, use_container_width=True, config={'displayModeBar': False})

# --- 8. FOOTER BANNER ---
footer_html = f"""
<div style="border: 1px solid black; border-radius: 6px; background-color: #BBDEFB; padding: 2px; text-align: center; color: #1f3b73; font-weight: 700; font-size: 13px; margin-top: 1px;">
    ⭐ Overall occupancy stands at {overall_occupancy:.2f}% over {total_days} operational days with a total of {total_occ:,.0f} occupied out of {total_acc:,.0f} accommodation.
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
