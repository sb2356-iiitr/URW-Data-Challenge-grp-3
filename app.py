import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

# --- Page Config ---
st.set_page_config(
    page_title="URW Retail Mix Optimizer",
    page_icon="🛍️",
    layout="wide"
)

# --- Header ---
col1, col2 = st.columns([1, 4])
with col1:
    # Use a placeholder icon or local image if URL fails (generic retail icon)
    st.write("## 🛍️ URW") 
with col2:
    st.title("AI-Driven Tenant Mix Optimizer")
    st.markdown("### *Recovering Asset Value through Graph-Based Site Selection*")

st.markdown("---")

import os

# --- Load Data ---
@st.cache_data
def load_data():
    file_path = 'urw_dashboard_data.csv'
    if not os.path.exists(file_path):
        # Try relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'urw_dashboard_data.csv')
    return pd.read_csv(file_path)

try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file `urw_dashboard_data.csv` not found. Please run the `Model.ipynb` final section first.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("📍 Location Filter")
all_malls = sorted(df['Mall_ID'].unique().tolist())
selected_mall = st.sidebar.selectbox("Select Shopping Centre", all_malls)

# Filter Data
mall_data = df[df['Mall_ID'] == selected_mall].copy()
mall_data = mall_data.sort_values('Revenue_Uplift', ascending=False)

# --- Top Level KPIs ---
# Assuming 150 m2 avg store size for impact calc if not in data. 
# We have Density (€/m2). Let's show Density Uplift and Total Potential assuming avg store size of 200m2 for estimation.
avg_store_size = 200 
total_opportunity = mall_data['Revenue_Uplift'].sum() * avg_store_size 
avg_uplift = mall_data['Revenue_Uplift'].mean()

kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Identified Opportunities", f"{len(mall_data)} Stores", "Underperforming Assets")
kpi2.metric("Avg. Density Uplift", f"+€{avg_uplift:,.0f} /m²", "Per Optimized Unit")
kpi3.metric("Total Est. Revenue Unlock", f"€{total_opportunity/1000000:.1f}M", "Annual Potential (est. @ 200m² avg)")

# --- Main Interface ---
st.subheader(f"Optimization Targets: Mall {selected_mall}")

# Display Table
st.dataframe(
    mall_data[['Store_Code', 'Current_SubCat', 'Rec_SubCat', 'Current_Sales_Density', 'Rec_Projected_Sales', 'Revenue_Uplift']],
    column_config={
        "Current_Sales_Density": st.column_config.NumberColumn("Current Sales (€/m²)", format="€%.0f"),
        "Rec_Projected_Sales": st.column_config.NumberColumn("Potential Sales (€/m²)", format="€%.0f"),
        "Revenue_Uplift": st.column_config.NumberColumn("Uplift (€/m²)", format="€%.0f"),
    },
    use_container_width=True,
    hide_index=True
)

# --- Deep Dive Section ---
st.markdown("---")
st.subheader("💡 Scenario Simulator")

if not mall_data.empty:
    col_left, col_right = st.columns([1, 2])

    with col_left:
        target_store = st.selectbox("Select a Store to Analyze:", mall_data['Store_Code'])
        store_row = mall_data[mall_data['Store_Code'] == target_store].iloc[0]
        
        st.info(f"**Current Tenant:** {store_row['Current_SubCat']}")
        st.success(f"**AI Recommendation:** {store_row['Rec_SubCat']}")
        st.write(f"The model detects this location has structural/network characteristics usage suitable for **{store_row['Rec_Category']}** (specifically **{store_row['Rec_SubCat']}**).")
        st.metric("Projected Density Increase", f"+€{store_row['Revenue_Uplift']:,.0f}")

    with col_right:
        # Bar Chart
        chart_data = pd.DataFrame({
            'Scenario': ['Current Performance', 'Location Potential (Fair Value)', 'Optimized Tenant (AI)'],
            'Sales Density (€)': [
                store_row['Current_Sales_Density'], 
                store_row['Model_Location_Potential'], 
                store_row['Rec_Projected_Sales']
            ],
            'Color': ['#FF4B4B', '#808080', '#2ECC71'] # Red, Grey, Green
        })
        
        c = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('Scenario', sort=None, axis=alt.Axis(labelAngle=0)),
            y=alt.Y('Sales Density (€)', axis=alt.Axis(format='€s')),
            color=alt.Color('Color', scale=None, legend=None),
            tooltip=['Scenario', 'Sales Density (€)']
        ).properties(
            title=f"Optimization Analysis: Store {store_row['Store_Code']}",
            height=350
        )
        
        # Add text labels on bars
        text = c.mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            fontWeight='bold'
        ).encode(
            text=alt.Text('Sales Density (€)', format='€,.0f')
        )
        
        st.altair_chart(c + text, use_container_width=True)
else:
    st.warning("No opportunities found for this mall with the current filter settings.")

