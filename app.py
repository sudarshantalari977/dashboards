import pandas as pd
import plotly.express as px
import streamlit as st

# Set page configuration to wide layout
st.set_page_config(
    page_title="Cumulative Daily Avg. Occupancy Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for single-screen compactness
st.markdown(
    """
    <style>
    /* 1. Push everything up by reducing the top block padding */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* 2. Reduce spacing between elements */
    [data-testid="stVerticalBlock"] {
        gap: 0.4rem !important;
    }

    /* 3. Compact Headers */
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

    /* 4. Compact Metric Cards */
    [data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 5px 10px; /* Reduced padding */
        border-radius: 6px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricLabel"] {
        font-weight: 800 !important;
        font-size: 12px !important;
        color: #333 !important;
    }
    [data-testid="stMetricValue"] {
        font-weight: 800 !important;
        font-size: 22px !important; /* Slightly smaller text */
        color: #1f3b73 !important;
    }

    /* 5. Compact Table */
    thead tr th {
        background-color: #0b3273 !important;
        color: white !important;
        text-align: center !important;
        font-weight: bold !important;
        font-size: 12px !important;
        padding: 4px !important; /* Reduced padding */
    }
    tbody tr td {
        text-align: center !important;
        font-size: 12px !important;
        padding: 4px !important; /* Reduced padding */
    }

    /* 6. Compact Blue Headers */
    .blue-header {
        background-color: #0b3273;
        color: white;
        text-align: center;
        font-weight: bold;
        padding: 6px; 
        border-radius: 4px;
        font-size: 13px;
        margin-bottom: 15px !important; /* Increased to prevent overlapping */
        text-transform: uppercase;
    }
    </style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    data = {
        "location": ["PanjTarni", "Baltal", "Pantha Chowk", "Nunwan"],
        "total": [888, 8132, 13660, 19272],
        "occupied": [719, 6376, 9635, 12336],
        "occupancy_percentage": [80.97, 78.41, 70.53, 64.01],
        "daily_average_occupancy": [36, 319, 482, 617],
        "operating_days": [20, 20, 20, 20],
    }
    return pd.DataFrame(data)


df = load_data()

# --- CALCULATE SUMMARY METRICS ---
total_acc = df["total"].sum()
total_occ = df["occupied"].sum()
overall_occupancy = (total_occ / total_acc) * 100
total_days = df["operating_days"].iloc[0]
total_daily_avg = df["daily_average_occupancy"].sum()

# --- HEADER SECTION ---
st.markdown('<p class="main-title">Cumulative Daily Avg. Occupancy Dashboard</p>', unsafe_allow_html=True)
st.markdown(f'<p class="sub-title">Reporting Period: {total_days} Days</p>', unsafe_allow_html=True)

# --- TOP ROW: BOXED METRIC CARDS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="🏢 TOTAL ACCOMMODATION", value=f"{total_acc:,.0f}")
with col2:
    st.metric(label="👥 TOTAL OCCUPIED", value=f"{total_occ:,.0f}")
with col3:
    st.metric(label="🍩 OVERALL OCCUPANCY", value=f"{overall_occupancy:.2f}%")
with col4:
    st.metric(label="📅 OPERATIONAL DAYS", value=f"{total_days}")

# --- MIDDLE SECTION: TABLE & KEY INSIGHTS ---
mid_col1, mid_col2 = st.columns([2.5, 1])

with mid_col1:
    with st.container(border=True):
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

with mid_col2:
    with st.container(border=True):
        st.markdown('<div class="blue-header">💡 Key Insights</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="font-size: 13px; line-height: 1.5; padding-top: 5px;">
            <b>📈 Highest:</b> PanjTarni (80.97%)<br><br>
            <b>📉 Lowest:</b> Nunwan (64.01%)<br><br>
            <b>👥 High Avg:</b> Nunwan (617)<br><br>
            <b>🍩 Overall:</b> {overall_occupancy:.2f}%<br>
            </div>
            """, unsafe_allow_html=True
        )

# --- BOTTOM SECTION: PLOTLY CHARTS IN BOXES ---
chart_col1, chart_col2 = st.columns(2)


def apply_bold_chart_styling(fig, xaxis_title):
    fig.update_layout(
        height=220,  # FORCES CHART TO BE SHORT
        xaxis_title=xaxis_title,
        yaxis_title="",
        showlegend=False,
        margin=dict(l=5, r=5, t=5, b=25),  # TIGHT MARGINS
        font=dict(family="Arial", size=11, color="black"),
        xaxis=dict(showline=True, linewidth=1.5, linecolor="black", mirror=True,
                   tickfont=dict(size=11, color="black", weight="bold")),
        yaxis=dict(showline=True, linewidth=1.5, linecolor="black", mirror=True,
                   tickfont=dict(size=11, color="black", weight="bold")),
        plot_bgcolor="white",
        paper_bgcolor="white",
    )
    return fig


with chart_col1:
    with st.container(border=True):
        st.markdown('<div class="blue-header">Occupancy % by Location</div>', unsafe_allow_html=True)

        df_sorted_occ = df.sort_values(by="occupancy_percentage", ascending=True)
        fig_occ = px.bar(
            df_sorted_occ, x="occupancy_percentage", y="location", orientation="h",
            text="occupancy_percentage", color="location",
            color_discrete_sequence=["#4B0082", "#228B22", "#FF8C00", "#1E90FF"],
        )

        # REDUCED BAR WIDTH (width=0.5)
        fig_occ.update_traces(width=0.5, texttemplate="%{text:.2f}%", textposition="outside",
                              textfont=dict(weight="bold", color="black"))
        fig_occ = apply_bold_chart_styling(fig_occ, "Occupancy %")
        fig_occ.update_layout(xaxis=dict(range=[0, 110]))

        st.plotly_chart(fig_occ, use_container_width=True, config={'displayModeBar': False})

with chart_col2:
    with st.container(border=True):
        st.markdown('<div class="blue-header">Cumulative Daily Avg. Occupancy</div>', unsafe_allow_html=True)

        df_sorted_avg = df.sort_values(by="daily_average_occupancy", ascending=True)
        fig_avg = px.bar(
            df_sorted_avg, x="daily_average_occupancy", y="location", orientation="h",
            text="daily_average_occupancy", color="location",
            color_discrete_sequence=["#4B0082", "#228B22", "#FF8C00", "#1E90FF"],
        )

        # REDUCED BAR WIDTH (width=0.5)
        fig_avg.update_traces(width=0.5, texttemplate="%{text}", textposition="outside",
                              textfont=dict(weight="bold", color="black"))
        fig_avg = apply_bold_chart_styling(fig_avg, "Avg. Occupancy")
        fig_avg.update_layout(xaxis=dict(range=[0, 700]))

        st.plotly_chart(fig_avg, use_container_width=True, config={'displayModeBar': False})

# --- FOOTER BANNER ---
with st.container(border=True):
    st.markdown(
        f"""
        <div style="text-align: center; color: #1f3b73; font-weight: 600; font-size: 13px; padding: 4px; background-color: #f4f8ff; border-radius: 4px;">
        ⭐ Overall occupancy stands at {overall_occupancy:.2f}% over {total_days} operational days with a total of {total_occ:,.0f} occupied out of {total_acc:,.0f} accommodation.
        </div>
        """,
        unsafe_allow_html=True
    )