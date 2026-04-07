import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------
# PAGE CONFIG
# -----------------------------------
st.set_page_config(page_title="Occupancy Dashboard", layout="wide")

st.title("Building Occupancy Dashboard")

# -----------------------------------
# DESCRIPTION
# -----------------------------------
st.markdown("""
This dashboard provides a unified view of building occupancy using a confidence-based model
that integrates multiple sensor types to improve accuracy and reliability.
""")

st.markdown("""
### Key Insights
- Peak occupancy occurs during weekday afternoons  
- Some buildings exceed safe occupancy thresholds  
- Traffic strongly correlates with occupancy in high-density areas  
- Sensor confidence varies significantly by type  
""")

# -----------------------------------
# LOAD DATA
# -----------------------------------
df = pd.read_parquet("occupancy_cof.parquet")

# -----------------------------------
# PROCESS DATA
# -----------------------------------
df['date_time'] = pd.to_datetime(df['date_time'])
df['occupancy'] = pd.to_numeric(df['occupancy'], errors='coerce')
df['capacity'] = pd.to_numeric(df['capacity'], errors='coerce')

df = df.fillna(0)

# COF metric (FINAL)
df['cof_rate'] = df['final_occupancy_normalized'] * 100

# Optional deeper metric
df['cof_score'] = df['confidence'] * df['final_occupancy_normalized']

# Time features
df['hour'] = df['date_time'].dt.hour
df['day'] = df['date_time'].dt.day_name()

# -----------------------------------
# OCCUPANCY CATEGORY
# -----------------------------------
def categorize(rate):
    if rate < 40:
        return "Low"
    elif rate < 70:
        return "Medium"
    elif rate < 90:
        return "High"
    else:
        return "Critical"

df['occupancy_level'] = df['cof_rate'].apply(categorize)

# -----------------------------------
# SIDEBAR FILTERS
# -----------------------------------
st.sidebar.header("Filters")

selected_city = st.sidebar.selectbox(
    "Select City",
    options=["All Cities"] + sorted(df['city'].unique())
)

# Dynamic building filter based on city
if selected_city == "All Cities":
    building_options = sorted(df['building_name'].unique())
else:
    building_options = sorted(
        df[df['city'] == selected_city]['building_name'].unique()
    )

selected_building = st.sidebar.selectbox(
    "Select Building",
    options=["All"] + building_options
)

# Dynamic space filter based on building + city
if selected_building == "All":
    if selected_city == "All Cities":
        space_options = sorted(df['space_name'].unique())
    else:
        space_options = sorted(
            df[df['city'] == selected_city]['space_name'].unique()
        )
else:
    space_options = sorted(
        df[df['building_name'] == selected_building]['space_name'].unique()
    )

selected_space = st.sidebar.selectbox(
    "Select Space",
    options=["All"] + space_options
)

# Apply filters
if selected_city == "All Cities":
    filtered_df = df.copy()
else:
    filtered_df = df[df['city'] == selected_city]

if selected_building != "All":
    filtered_df = filtered_df[
        filtered_df['building_name'] == selected_building
    ]

if selected_space != "All":
    filtered_df = filtered_df[
        filtered_df['space_name'] == selected_space
    ]

if filtered_df.empty:
    st.warning("No data available for selected filters")
    st.stop()
    
st.sidebar.markdown("###  Current Selection")
st.sidebar.write(f"City: {selected_city}")
st.sidebar.write(f"Building: {selected_building}")
st.sidebar.write(f"Space: {selected_space}")

# -----------------------------------
# KPI METRICS
# -----------------------------------
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

avg_occ = filtered_df['cof_rate'].mean()
max_occ = filtered_df['occupancy'].max()
total_traffic = filtered_df['traffic'].sum()
avg_conf = filtered_df['confidence'].mean()

col1.metric("Avg COF Occupancy", f"{avg_occ:.2f}%")
col2.metric("Max Occupancy", int(max_occ))
col3.metric("Total Traffic", int(total_traffic))
col4.metric("Avg Confidence", f"{avg_conf:.2f}")

# Confidence interpretation
if avg_conf < 0.3:
    st.error("Very low confidence — data may be unreliable")
elif avg_conf < 0.5:
    st.warning("Moderate confidence — interpret with caution")
else:
    st.success("High confidence in occupancy estimates")

# -----------------------------------
# OCCUPANCY TREND
# -----------------------------------
st.subheader(" Occupancy Trend")

time_df = (
    filtered_df.groupby('date_time')['cof_rate']
    .mean()
    .reset_index()
)

fig = px.line(
    time_df,
    x='date_time',
    y='cof_rate',
    title='COF Occupancy Over Time'
)

st.plotly_chart(fig, use_container_width=True)

st.write("Insight: Identify peak hours and long-term occupancy trends.")

# -----------------------------------
# TRAFFIC VS OCCUPANCY
# -----------------------------------
st.subheader("Traffic vs Occupancy")

fig_corr = px.scatter(
    filtered_df,
    x='traffic',
    y='cof_rate',
    title='Traffic vs Occupancy'
)

st.plotly_chart(fig_corr, use_container_width=True)

# Correlation insight
corr = filtered_df[['traffic', 'cof_rate']].corr().iloc[0, 1]

st.write(f"Correlation: {corr:.2f}")

if corr > 0.7:
    st.success("Strong positive correlation")
elif corr > 0.4:
    st.info("Moderate correlation")
else:
    st.warning("Weak correlation")

# -----------------------------------
# HEATMAP
# -----------------------------------
st.subheader("Occupancy Heatmap (Day vs Hour)")

heatmap_df = (
    filtered_df.groupby(['day', 'hour'])['cof_rate']
    .mean()
    .reset_index()
)

fig_heatmap = px.density_heatmap(
    heatmap_df,
    x='hour',
    y='day',
    z='cof_rate',
    title="Occupancy Patterns"
)

st.plotly_chart(fig_heatmap, use_container_width=True)

# -----------------------------------
# COF VS RAW
# -----------------------------------
st.subheader("COF vs Raw Occupancy")

compare_df = (
    filtered_df.groupby('date_time')[['occupancy', 'cof_rate']]
    .mean()
    .reset_index()
)

fig_compare = px.line(
    compare_df,
    x='date_time',
    y=['occupancy', 'cof_rate'],
    title="Raw vs COF Occupancy"
)

st.plotly_chart(fig_compare, use_container_width=True)

# -----------------------------------
# PEAK USAGE
# -----------------------------------
st.subheader("Peak Usage")

peak = filtered_df.loc[filtered_df['cof_rate'].idxmax()]

st.write(
    f"Peak occupancy occurred at **{peak['date_time']}** "
    f"in **{peak['building_name']}** "
    f"with **{peak['cof_rate']:.2f}%** occupancy."
)

# -----------------------------------
# CITY COMPARISON
# -----------------------------------
st.subheader("City Comparison")

# ----------------------------
# City Insight Panel 
# ----------------------------
st.markdown("### City Insights")

# If ALL cities selected → show general insight
if selected_city == "All Cities":

    overall_avg = df['cof_rate'].mean()
    overall_conf = df['confidence'].mean()

    st.markdown(f"""
    ### Overall Portfolio Summary

    - **Avg Occupancy:** {overall_avg:.2f}%  
    - **Avg Confidence:** {overall_conf:.2f}

    This view represents **all cities combined**, giving a macro-level
    understanding of occupancy patterns and system reliability.
    """)

else:
    # City-specific insights
    city_avg = filtered_df['cof_rate'].mean()
    city_traffic = filtered_df['traffic'].sum()
    city_conf = filtered_df['confidence'].mean()

    global_avg = df['cof_rate'].mean()
    global_traffic = df.groupby('city')['traffic'].sum().mean()

    # Insight logic
    occupancy_msg = "Higher than average occupancy" if city_avg > global_avg else "📉 Lower than average occupancy"
    traffic_msg = "🚶 High traffic activity" if city_traffic > global_traffic else "🚶 Low traffic activity"

    corr = filtered_df[['traffic', 'cof_rate']].corr().iloc[0, 1]

    if corr > 0.5:
        corr_msg = "Strong correlation between traffic and occupancy"
    elif corr > 0:
        corr_msg = "Weak positive correlation"
    elif corr > -0.2:
        corr_msg = "No meaningful correlation"
    else:
        corr_msg = "Negative correlation"

    st.markdown(f"""
    ###  {selected_city} Summary

    - **Occupancy:** {occupancy_msg}  
    - **Traffic:** {traffic_msg}  
    - **Correlation:** {corr_msg}  
    - **Avg Confidence:** {city_conf:.2f}
    """)

# ----------------------------
# ALWAYS show full comparison chart
# ----------------------------
city_df = (
    df.groupby('city')['cof_rate']
    .mean()
    .reset_index()
)

# Highlight selected city
city_df['selected'] = city_df['city'] == selected_city

fig2 = px.bar(
    city_df,
    x='city',
    y='cof_rate',
    color='selected',
    color_discrete_map={True: '#1f77b4', False: '#d3d3d3'},
    title='Average COF Occupancy by City'
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------------
# SENSOR ANALYSIS
# -----------------------------------
st.subheader("Sensor Type Distribution")

sensor_dist = filtered_df['sensor_type'].value_counts().reset_index()
sensor_dist.columns = ['sensor_type', 'count']

fig_sensor = px.pie(
    sensor_dist,
    names='sensor_type',
    values='count'
)

st.plotly_chart(fig_sensor, use_container_width=True)

# Confidence by type
st.subheader("Sensor Confidence by Type")

sensor_conf = (
    df.groupby('sensor_type')['confidence']
    .mean()
    .reset_index()
)

fig_sensor_conf = px.bar(
    sensor_conf,
    x='sensor_type',
    y='confidence'
)

st.plotly_chart(fig_sensor_conf, use_container_width=True)

# Reliability insight
st.subheader("Sensor Reliability Insight")

high_conf = filtered_df[filtered_df['confidence'] > 0.7].shape[0]
low_conf = filtered_df[filtered_df['confidence'] < 0.3].shape[0]

st.write(f"High confidence readings: {high_conf}")
st.write(f"Low confidence readings: {low_conf}")

# -----------------------------------
# TOP BUILDINGS
# -----------------------------------
st.subheader("Top Buildings")

top_buildings = (
    filtered_df.groupby('building_name')['cof_rate']
    .mean()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig3 = px.bar(top_buildings, x='building_name', y='cof_rate')

st.plotly_chart(fig3, use_container_width=True)

# -----------------------------------
# ALERTS
# -----------------------------------
st.subheader("High Occupancy Alerts")

anomalies = filtered_df[
    (filtered_df['cof_rate'] > 90) &
    (filtered_df['confidence'] > 0.7)
]

st.error(f"{anomalies.shape[0]} alerts detected")

st.dataframe(
    anomalies[['building_name', 'date_time', 'cof_rate']]
)

# -----------------------------------
# ANOMALY TIMELINE
# -----------------------------------
st.subheader("Anomaly Timeline")

fig_anomaly = px.scatter(
    anomalies,
    x='date_time',
    y='cof_rate',
    color='building_name'
)

st.plotly_chart(fig_anomaly, use_container_width=True)

# -----------------------------------
# COF EXPLANATION
# -----------------------------------
st.markdown("""
### What is COF?

COF (Confidence-weighted Occupancy Fusion) integrates:
- Entry/Exit sensors (flow-based)
- Binary sensors (presence)
- Direct sensors (counts)

It combines:
- Kalman filtering (smoothing)
- Confidence scoring (reliability)
- Weighted fusion (final occupancy)
Result: a robust and reliable occupancy metric.
""")