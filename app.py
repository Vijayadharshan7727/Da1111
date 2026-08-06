import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Farm Equipment Utilization & Cost Analytics",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR HIGH-END DARK AESTHETIC ---
st.markdown("""
<style>
    /* Dark glassmorphism cards */
    .stApp {
        background-color: #0e1117;
        color: #e0e6ed;
    }
    .metric-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.01));
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease-in-out;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border: 1px solid rgba(0, 210, 255, 0.4);
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #8b9bb4;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
        margin-top: 6px;
    }
    .metric-delta {
        font-size: 0.85rem;
        font-weight: 500;
        margin-top: 4px;
    }
    .text-green { color: #10b981; }
    .text-red { color: #ef4444; }
    .text-cyan { color: #06b6d4; }
    .text-amber { color: #f59e0b; }

    /* Custom headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        color: #f8fafc;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }
</style>
""", unsafe_allow_html=True)

# --- LOAD CLEANED DATASETS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "cleaned_data")


@st.cache_data
def load_data():
    df_eq = pd.read_csv(f"{DATA_DIR}/equipment.csv")
    df_op = pd.read_csv(f"{DATA_DIR}/operator.csv")
    df_fld = pd.read_csv(f"{DATA_DIR}/field.csv")
    df_usg = pd.read_csv(f"{DATA_DIR}/usage_log.csv")
    df_fuel = pd.read_csv(f"{DATA_DIR}/fuel_consumption.csv")
    df_mnt = pd.read_csv(f"{DATA_DIR}/maintenance_log.csv")
    df_lse = pd.read_csv(f"{DATA_DIR}/rental_lease.csv")
    df_rpr = pd.read_csv(f"{DATA_DIR}/repair_log.csv")
    df_rsk = pd.read_csv(f"{DATA_DIR}/breakdown_risk.csv")

    # Convert date columns
    df_usg['Usage_Date'] = pd.to_datetime(df_usg['Usage_Date'])
    df_fuel['Usage_Date'] = pd.to_datetime(df_fuel['Usage_Date'])
    df_mnt['Maintenance_Date'] = pd.to_datetime(df_mnt['Maintenance_Date'])
    df_rsk['Score_Date'] = pd.to_datetime(df_rsk['Score_Date'])
    
    return df_eq, df_op, df_fld, df_usg, df_fuel, df_mnt, df_lse, df_rpr, df_rsk

df_eq, df_op, df_fld, df_usg, df_fuel, df_mnt, df_lse, df_rpr, df_rsk = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.image("https://img.icons8.com/color/96/tractor.png", width=70)
st.sidebar.title("Farm Analytics Filters")
st.sidebar.markdown("---")

# Equipment Type Filter
eq_types = ["All Types"] + sorted(list(df_eq['Equipment_Type'].unique()))
selected_type = st.sidebar.selectbox("Select Equipment Type", eq_types)

# Date Range Filter
min_date = df_usg['Usage_Date'].min().date()
max_date = df_usg['Usage_Date'].max().date()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Risk Category Filter
risk_cats = ["All Categories"] + sorted(list(df_rsk['Risk_Category'].unique()))
selected_risk = st.sidebar.selectbox("Select Risk Tier", risk_cats)

# Filter Datasets based on Sidebar inputs
filtered_eq = df_eq.copy()
if selected_type != "All Types":
    filtered_eq = filtered_eq[filtered_eq['Equipment_Type'] == selected_type]

valid_eq_set = set(filtered_eq['Equipment_ID'])

filtered_usg = df_usg[df_usg['Equipment_ID'].isin(valid_eq_set)]
if len(date_range) == 2:
    start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_usg = filtered_usg[(filtered_usg['Usage_Date'] >= start_d) & (filtered_usg['Usage_Date'] <= end_d)]

filtered_fuel = df_fuel[df_fuel['Equipment_ID'].isin(valid_eq_set)]
filtered_mnt = df_mnt[df_mnt['Equipment_ID'].isin(valid_eq_set)]
filtered_rsk = df_rsk[df_rsk['Equipment_ID'].isin(valid_eq_set)]
if selected_risk != "All Categories":
    filtered_rsk = filtered_rsk[filtered_rsk['Risk_Category'] == selected_risk]

# --- MAIN TITLE HEADER ---
st.title("🚜 Farm Equipment Utilization & Cost Analytics")
st.markdown("<p class='sub-title'>Unified multi-table intelligence system for agricultural machinery, field usage logs, fuel efficiency, and maintenance planning.</p>", unsafe_allow_html=True)

# --- TOP KPI METRIC CARDS ---
col1, col2, col3, col4, col5 = st.columns(5)

total_fleet = len(filtered_eq)
total_hours = filtered_usg['Hours_Used'].sum()
total_fuel = filtered_fuel['Fuel_Liters'].sum()
total_mnt_cost = filtered_mnt['Cost'].sum()
avg_breakdown_prob = filtered_rsk['Breakdown_Probability'].mean() * 100

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Fleet Size</div>
        <div class="metric-value">{total_fleet:,}</div>
        <div class="metric-delta text-cyan">Active Machines</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Operating Hours</div>
        <div class="metric-value">{total_hours:,.1f} h</div>
        <div class="metric-delta text-green">Field Runtime</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Fuel Consumed</div>
        <div class="metric-value">{total_fuel:,.0f} L</div>
        <div class="metric-delta text-amber">Diesel Fuel</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Maintenance Spend</div>
        <div class="metric-value">${total_mnt_cost:,.2f}</div>
        <div class="metric-delta text-red">Total Repairs</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Breakdown Risk</div>
        <div class="metric-value">{avg_breakdown_prob:.1f}%</div>
        <div class="metric-delta text-amber">Avg Fleet Risk</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- TABS FOR MULTI-DIMENSIONAL ANALYSIS ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Executive Overview", 
    "🚜 Utilization & Fleet Performance", 
    "⛽ Fuel Efficiency & Anomalies", 
    "🔧 Maintenance & Risk Score", 
    "👨‍🌾 Operator Analytics",
    "📑 Data Explorer & Export"
])

# --- TAB 1: EXECUTIVE OVERVIEW ---
with tab1:
    st.subheader("Monthly Usage Hours & Fuel Consumption Trend")
    
    # Monthly Aggregation
    usg_monthly = filtered_usg.set_index('Usage_Date').resample('M')['Hours_Used'].sum().reset_index()
    fuel_monthly = filtered_fuel.set_index('Usage_Date').resample('M')['Fuel_Liters'].sum().reset_index()
    monthly_trend = pd.merge(usg_monthly, fuel_monthly, left_on='Usage_Date', right_on='Usage_Date', how='outer').fillna(0)
    monthly_trend['Month_Str'] = monthly_trend['Usage_Date'].dt.strftime('%b %Y')

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Bar(
        x=monthly_trend['Month_Str'], y=monthly_trend['Hours_Used'],
        name="Hours Used (hrs)", marker_color="#00d2ff", opacity=0.85
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly_trend['Month_Str'], y=monthly_trend['Fuel_Liters'],
        name="Fuel Consumed (L)", yaxis="y2", mode="lines+markers",
        line=dict(color="#f59e0b", width=3), marker=dict(size=8)
    ))

    fig_trend.update_layout(
        template="plotly_dark",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20),
        yaxis=dict(title="Usage Hours"),
        yaxis2=dict(title="Fuel Liters", overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Fleet Distribution by Equipment Type")
        eq_dist = filtered_eq['Equipment_Type'].value_counts().reset_index()
        eq_dist.columns = ['Equipment_Type', 'Count']
        fig_pie = px.pie(eq_dist, names='Equipment_Type', values='Count', hole=0.4,
                         color_discrete_sequence=px.colors.sequential.Cyan)
        fig_pie.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig_pie, use_container_width=True)

    with c2:
        st.subheader("Breakdown Risk Severity Distribution")
        risk_dist = filtered_rsk['Risk_Category'].value_counts().reset_index()
        risk_dist.columns = ['Risk_Category', 'Count']
        color_map = {'Low': '#10b981', 'Medium': '#3b82f6', 'High': '#f59e0b', 'Critical': '#ef4444'}
        fig_risk = px.bar(risk_dist, x='Risk_Category', y='Count', color='Risk_Category',
                          color_discrete_map=color_map, text='Count')
        fig_risk.update_layout(template="plotly_dark", height=350, showlegend=False)
        st.plotly_chart(fig_risk, use_container_width=True)

# --- TAB 2: UTILIZATION & FLEET PERFORMANCE ---
with tab2:
    st.subheader("Total Usage Hours by Equipment Type")
    usg_by_type = filtered_usg.merge(filtered_eq[['Equipment_ID', 'Equipment_Type']], on='Equipment_ID')
    usg_type_agg = usg_by_type.groupby('Equipment_Type')['Hours_Used'].agg(['sum', 'mean', 'count']).reset_index()
    usg_type_agg.columns = ['Equipment_Type', 'Total_Hours', 'Avg_Hours_Per_Session', 'Total_Sessions']
    usg_type_agg = usg_type_agg.sort_values(by='Total_Hours', ascending=False)

    fig_usg = px.bar(usg_type_agg, x='Equipment_Type', y='Total_Hours',
                     color='Avg_Hours_Per_Session', color_continuous_scale='Blues',
                     labels={'Total_Hours': 'Total Operating Hours', 'Equipment_Type': 'Equipment Category'},
                     text_auto='.0f')
    fig_usg.update_layout(template="plotly_dark", height=420)
    st.plotly_chart(fig_usg, use_container_width=True)

    st.subheader("Top 15 Most Utilized Machines (Hours Used)")
    top_eq_usg = filtered_usg.groupby('Equipment_ID')['Hours_Used'].sum().reset_index()
    top_eq_usg = top_eq_usg.merge(filtered_eq[['Equipment_ID', 'Equipment_Type', 'Owner_Farm_ID']], on='Equipment_ID')
    top_eq_usg = top_eq_usg.sort_values(by='Hours_Used', ascending=False).head(15)

    fig_top_eq = px.bar(top_eq_usg, x='Hours_Used', y='Equipment_ID', color='Equipment_Type',
                        orientation='h', text_auto='.1f',
                        color_discrete_sequence=px.colors.qualitative.Plotly)
    fig_top_eq.update_layout(template="plotly_dark", height=450, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top_eq, use_container_width=True)

# --- TAB 3: FUEL EFFICIENCY & ANOMALY DETECTION ---
with tab3:
    st.subheader("Fuel Burn Rate (Liters / Hour) Analysis by Machinery Category")
    
    # Merge usage and fuel aggregated by equipment
    eq_usg_agg = filtered_usg.groupby('Equipment_ID')['Hours_Used'].sum().reset_index()
    eq_fuel_agg = filtered_fuel.groupby('Equipment_ID')['Fuel_Liters'].sum().reset_index()
    eq_efficiency = pd.merge(eq_usg_agg, eq_fuel_agg, on='Equipment_ID')
    eq_efficiency = pd.merge(eq_efficiency, filtered_eq[['Equipment_ID', 'Equipment_Type', 'Owner_Farm_ID']], on='Equipment_ID')
    
    eq_efficiency['Burn_Rate_LperH'] = eq_efficiency['Fuel_Liters'] / eq_efficiency['Hours_Used']

    fig_scatter = px.scatter(
        eq_efficiency, x='Hours_Used', y='Fuel_Liters', color='Equipment_Type',
        size='Burn_Rate_LperH', hover_data=['Equipment_ID', 'Owner_Farm_ID', 'Burn_Rate_LperH'],
        title="Fuel Consumption vs. Operating Hours Correlation",
        labels={'Hours_Used': 'Total Field Hours', 'Fuel_Liters': 'Total Fuel Consumed (L)'}
    )
    fig_scatter.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("⚠️ High Fuel Burn Rate Anomaly Alerts")
    burn_threshold = eq_efficiency['Burn_Rate_LperH'].quantile(0.90)
    anomalies = eq_efficiency[eq_efficiency['Burn_Rate_LperH'] >= burn_threshold].sort_values(by='Burn_Rate_LperH', ascending=False)
    
    st.warning(f"Identified {len(anomalies)} machines operating in the top 10% highest fuel burn rate (> {burn_threshold:.2f} Liters/Hour). Potential fuel theft, injector clogging, or severe engine wear.")
    st.dataframe(anomalies[['Equipment_ID', 'Equipment_Type', 'Owner_Farm_ID', 'Hours_Used', 'Fuel_Liters', 'Burn_Rate_LperH']], use_container_width=True)

# --- TAB 4: MAINTENANCE & BREAKDOWN RISK ---
with tab4:
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Maintenance Spend by Service Type")
        mnt_type_agg = filtered_mnt.groupby('Type')['Cost'].sum().reset_index()
        fig_mnt_pie = px.pie(mnt_type_agg, names='Type', values='Cost', hole=0.4,
                             color_discrete_sequence=px.colors.sequential.RdBu)
        fig_mnt_pie.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig_mnt_pie, use_container_width=True)

    with col_m2:
        st.subheader("Most Frequently Replaced Repair Parts")
        part_counts = df_rpr['Part_Replaced'].value_counts().reset_index()
        part_counts.columns = ['Part_Replaced', 'Replacement_Count']
        fig_parts = px.bar(part_counts, x='Replacement_Count', y='Part_Replaced', orientation='h',
                           color='Replacement_Count', color_continuous_scale='Reds')
        fig_parts.update_layout(template="plotly_dark", height=380, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_parts, use_container_width=True)

    st.subheader("🔥 High & Critical Breakdown Risk Equipment Radar")
    critical_rsk = filtered_rsk[filtered_rsk['Risk_Category'].isin(['High', 'Critical'])].sort_values(by='Breakdown_Probability', ascending=False)
    critical_rsk = critical_rsk.merge(filtered_eq[['Equipment_ID', 'Equipment_Type', 'Owner_Farm_ID']], on='Equipment_ID')
    
    st.dataframe(critical_rsk[['Risk_ID', 'Equipment_ID', 'Equipment_Type', 'Owner_Farm_ID', 'Score_Date', 'Breakdown_Probability', 'Risk_Category']], use_container_width=True)

# --- TAB 5: OPERATOR ANALYTICS ---
with tab5:
    st.subheader("Operator Field Hours Logging Leaderboard")
    op_usg = filtered_usg.groupby('Operator_ID')['Hours_Used'].sum().reset_index()
    op_usg = op_usg.merge(df_op[['Operator_ID', 'Operator_Name', 'Experience_Years']], on='Operator_ID')
    op_usg = op_usg.sort_values(by='Hours_Used', ascending=False)

    fig_op = px.bar(op_usg.head(20), x='Operator_Name', y='Hours_Used', color='Experience_Years',
                    labels={'Operator_Name': 'Operator Name', 'Hours_Used': 'Logged Field Hours'},
                    color_continuous_scale='Viridis', text_auto='.0f')
    fig_op.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_op, use_container_width=True)

    c_op1, c_op2 = st.columns(2)
    with c_op1:
        st.subheader("Experience Level vs. Total Hours Operated")
        fig_exp_scatter = px.scatter(op_usg, x='Experience_Years', y='Hours_Used', size='Hours_Used',
                                     hover_data=['Operator_Name'], color='Experience_Years')
        fig_exp_scatter.update_layout(template="plotly_dark", height=360)
        st.plotly_chart(fig_exp_scatter, use_container_width=True)

    with c_op2:
        st.subheader("Top Operators Summary Table")
        st.dataframe(op_usg[['Operator_ID', 'Operator_Name', 'Experience_Years', 'Hours_Used']], use_container_width=True)

# --- TAB 6: DATA EXPLORER & CSV EXPORT ---
with tab6:
    st.subheader("📥 Interactive Data Table Explorer & Download Center")
    
    dataset_choice = st.selectbox(
        "Select Table to Preview & Download",
        ["Usage_Log (Cleaned)", "Fuel_Consumption (Cleaned)", "Maintenance_Log (Cleaned)",
         "Equipment (Cleaned)", "Operator (Cleaned)", "Field (Cleaned)", 
         "Rental_Lease (Cleaned)", "Repair_Log (Cleaned)", "Breakdown_Risk (Cleaned)"]
    )

    tbl_map = {
        "Usage_Log (Cleaned)": df_usg,
        "Fuel_Consumption (Cleaned)": df_fuel,
        "Maintenance_Log (Cleaned)": df_mnt,
        "Equipment (Cleaned)": df_eq,
        "Operator (Cleaned)": df_op,
        "Field (Cleaned)": df_fld,
        "Rental_Lease (Cleaned)": df_lse,
        "Repair_Log (Cleaned)": df_rpr,
        "Breakdown_Risk (Cleaned)": df_rsk
    }

    selected_df = tbl_map[dataset_choice]
    
    st.markdown(f"**Showing {len(selected_df):,} records for `{dataset_choice}`**")
    st.dataframe(selected_df, use_container_width=True)

    csv_data = selected_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"⬇️ Download {dataset_choice} CSV",
        data=csv_data,
        file_name=f"{dataset_choice.split()[0].lower()}.csv",
        mime="text/csv"
    )

st.markdown("---")
st.markdown("<p style='text-align: center; color: #64748b;'>Farm Equipment Utilization & Cost Analytics System • Day 1 ETL & Interactive Streamlit Platform</p>", unsafe_allow_html=True)
