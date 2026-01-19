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
    malls_path = 'dim_malls_v1.csv'

    # Safe path resolution
    if not os.path.exists(file_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, 'urw_dashboard_data.csv')
        malls_path = os.path.join(script_dir, 'dim_malls_v1.csv')
    
    df = pd.read_csv(file_path)
    
    # Merge Mall Names
    if os.path.exists(malls_path):
        try:
             # Try reading with fallback encoding for special chars
             try:
                 malls = pd.read_csv(malls_path, encoding='utf-8')
             except:
                 malls = pd.read_csv(malls_path, encoding='latin1')
             
             malls['id'] = pd.to_numeric(malls['id'], errors='coerce')
             df = df.merge(malls[['id', 'mall_name']], left_on='Mall_ID', right_on='id', how='left')
             
             df['Mall_Display'] = df.apply(
                 lambda x: x['mall_name'] if pd.notna(x['mall_name']) else f"Mall {int(x['Mall_ID'])}",
                 axis=1
             )
        except:
             df['Mall_Display'] = "Mall " + df['Mall_ID'].astype(str)
    else:
        df['Mall_Display'] = "Mall " + df['Mall_ID'].astype(str)
        
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("Data file `urw_dashboard_data.csv` not found. Please run the `Model.ipynb` final section first.")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("📍 Location Filter")

# Create Mapping
mall_options = df[['Mall_ID', 'Mall_Display']].drop_duplicates().sort_values('Mall_Display')
mall_map = dict(zip(mall_options['Mall_Display'], mall_options['Mall_ID']))

selected_mall_name = st.sidebar.selectbox("Select Shopping Centre", mall_options['Mall_Display'])
selected_mall_id = mall_map[selected_mall_name]

# Filter Data
top_n = st.sidebar.slider("Show Top Opportunities", 5, 200, 50)
mall_data = df[df['Mall_ID'] == selected_mall_id].copy()
mall_data = mall_data.sort_values('Revenue_Uplift', ascending=False).head(top_n)

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
st.subheader(f"Optimization Targets: {selected_mall_name}")

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
        
        with st.expander("🔄 See Alternative Strategies"):
             if 'Rec_2_SubCat' in store_row and pd.notna(store_row['Rec_2_SubCat']):
                 st.write("**Top 3 AI Recommendations:**")
                 st.markdown(f"1. 🥇 **{store_row['Rec_SubCat']}** (+€{store_row['Revenue_Uplift']:,.0f})")
                 st.markdown(f"2. 🥈 **{store_row.get('Rec_2_SubCat')}** (+€{store_row.get('Rec_2_Uplift', 0):,.0f})")
                 st.markdown(f"3. 🥉 **{store_row.get('Rec_3_SubCat')}** (+€{store_row.get('Rec_3_Uplift', 0):,.0f})")
             else:
                 st.write("No alternative strategies available.")

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

