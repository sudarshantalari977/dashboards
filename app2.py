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
        font-size: 24px;
        font-weight: 800;
        color: #1f3b73;
        text-align: center;
        margin-bottom: -5px;
    }
    .sub-title {
        font-size: 13px;
        font-weight: 600;
        color: #555;
        text-align: center;
        margin-bottom: 5px;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 5px 10px;
        border-radius: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] { font-weight: 800 !important; font-size: 12px !important; color: #333 !important; }
    [data-testid="stMetricValue"] { font-weight: 800 !important; font-size: 22px !important; color: #1f3b73 !important; }
    thead tr th {
        background-color: #0b3273 !important; color: white !important;
        text-align: center !important; font-weight: bold !important;
        font-size: 12px !important; padding: 4px !important;
    }
    tbody tr td { text-align: center !important; font-size: 12px !important; padding: 4px !important; }
    .blue-header {
        background-color: #0b3273; color: white; text-align: center;
        font-weight: bold; padding: 4px; border-radius: 4px;
        font-size: 13px; margin-bottom: 2px; text-transform: uppercase;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- 2. HEADER & FILTERS ---
st.markdown('<p class="main-title">Cumulative Daily Avg. Occupancy Dashboard</p>', unsafe_allow_html=True)

# Create a clean row for the interactive filters
filter_col1, filter_col2 = st.columns([1, 3])
with filter_col1:
    selected_date = st.date_input("📅 Reporting Date", datetime.date.today())


# --- 3. LIVE DATA CONNECTION (60-Second Refresh) ---
@st.cache_data(ttl=60)
def get_data(target_date):
    """Fetches data from AWS RDS. Caches it for 60 seconds to prevent DB overload."""
    try:
        # Tries to connect using Streamlit secrets
        DB_USER = st.secrets["DB_USER"]
        DB_PASSWORD = st.secrets["DB_PASSWORD"]
        DB_HOST = st.secrets["DB_HOST"]
        DB_PORT = st.secrets["DB_PORT"]
        DB_NAME = st.secrets["DB_NAME"]

        engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

        # Modify this query to match your actual database function/table structure
        # Example using the date filter: f"SELECT * FROM your_table WHERE report_date = '{target_date}'"
        query = "SELECT location, total, occupied, occupancy_percentage, daily_average_occupancy, operating_days FROM your_table"
        df = pd.read_sql(query, engine)
        return df

    except Exception as e:
        # Fallback to mock data if DB isn't connected yet
        return pd.DataFrame({
            "location": ["PanjTarni", "Baltal", "Pantha Chowk", "Nunwan"],
            "total": [888, 8132, 13660, 19272],
            "occupied": [719, 6376, 9635, 12336],
            "occupancy_percentage": [80.97, 78.41, 70.53, 64.01],
            "daily_average_occupancy": [36, 319, 482, 617],
            "operating_days": [20, 20, 20, 20],
        })


# Load the data
raw_df = get_data(selected_date)

# Complete the filter section by dynamically generating location options based on the DB data
with filter_col2:
    location_options = ["All Locations"] + list(raw_df["location"].unique())
    selected_location = st.radio("📍 Filter by Location", options=location_options, horizontal=True)

# Apply the filter
if selected_location == "All Locations":
    df = raw_df
else:
    df = raw_df[raw_df["location"] == selected_location]

# --- 4. CALCULATE DYNAMIC METRICS ---
# If data is empty after filtering, default to 0 to prevent errors
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
    with st.container(border=True):
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
    with st.container(border=True):
        st.markdown('<div class="blue-header">💡 Key Insights</div>', unsafe_allow_html=True)
        if not df.empty:
            highest_loc = df.loc[df["occupancy_percentage"].idxmax()]
            lowest_loc = df.loc[df["occupancy_percentage"].idxmin()]
            high_avg_loc = df.loc[df["daily_average_occupancy"].idxmax()]

            st.markdown(
                f"""
                <div style="font-size: 13px; line-height: 1.5; padding-top: 5px;">
                <b>📈 Highest:</b> {highest_loc['location']} ({highest_loc['occupancy_percentage']:.2f}%)<br><br>
                <b>📉 Lowest:</b> {lowest_loc['location']} ({lowest_loc['occupancy_percentage']:.2f}%)<br><br>
                <b>👥 High Avg:</b> {high_avg_loc['location']} ({high_avg_loc['daily_average_occupancy']})<br><br>
                <b>🍩 Overall:</b> {overall_occupancy:.2f}%<br>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.write("Insufficient data.")

# --- 7. BOTTOM SECTION: PLOTLY CHARTS IN BOXES ---
chart_col1, chart_col2 = st.columns(2)


def apply_bold_chart_styling(fig, xaxis_title):
    fig.update_layout(
        height=220,
        xaxis_title=xaxis_title, yaxis_title="", showlegend=False,
        margin=dict(l=5, r=5, t=5, b=25),
        font=dict(family="Arial", size=11, color="black"),
        xaxis=dict(showline=True, linewidth=1.5, linecolor="black", mirror=True,
                   tickfont=dict(size=11, color="black", weight="bold")),
        yaxis=dict(showline=True, linewidth=1.5, linecolor="black", mirror=True,
                   tickfont=dict(size=11, color="black", weight="bold")),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    return fig


with chart_col1:
    with st.container(border=True):
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
            fig_occ.update_layout(xaxis=dict(range=[0, 110]))
            st.plotly_chart(fig_occ, use_container_width=True, config={'displayModeBar': False})

with chart_col2:
    with st.container(border=True):
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

            # Dynamically set the x-axis range based on max value to ensure text fits
            max_val = df_sorted_avg["daily_average_occupancy"].max()
            x_range = max_val + (max_val * 0.2) if max_val > 0 else 700

            fig_avg = apply_bold_chart_styling(fig_avg, "Avg. Occupancy")
            fig_avg.update_layout(xaxis=dict(range=[0, x_range]))
            st.plotly_chart(fig_avg, use_container_width=True, config={'displayModeBar': False})

# --- 8. FOOTER BANNER ---
with st.container(border=True):
    st.markdown(
        f"""
        <div style="text-align: center; color: #1f3b73; font-weight: 600; font-size: 13px; padding: 4px; background-color: #f4f8ff; border-radius: 4px;">
        ⭐ Overall occupancy stands at {overall_occupancy:.2f}% over {total_days} operational days with a total of {total_occ:,.0f} occupied out of {total_acc:,.0f} accommodation.
        </div>
        """,
        unsafe_allow_html=True
    )