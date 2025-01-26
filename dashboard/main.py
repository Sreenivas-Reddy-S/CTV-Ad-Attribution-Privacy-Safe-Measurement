# dashboard/main.py

import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
import plotly.express as px

# Configuration
BACKEND_URL = os.getenv("BACKEND_API", "http://attribution-service:8081/api")
CACHE_TTL = 3600  # 1 hour cache

st.set_page_config(
    page_title="CTV Attribution Dashboard",
    layout="wide",
    page_icon="📊"
)

@st.cache_data(ttl=CACHE_TTL)
def fetch_attribution_data():
    """Fetch anonymized attribution data from backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/attribution-metrics")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

@st.cache_data(ttl=CACHE_TTL)
def get_campaign_performance():
    """Get GDPR-compliant campaign metrics"""
    try:
        response = requests.get(f"{BACKEND_URL}/campaign-performance")
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        st.error(f"Error loading campaign data: {str(e)}")
        return pd.DataFrame()

def display_kpis(metrics):
    """Display key performance indicators"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Daily Impressions", f"{metrics.get('daily_impressions', 0):,}")
    with col2:
        st.metric("Avg. CPA", f"${metrics.get('avg_cpa', 0):.2f}", 
                 delta=f"{metrics.get('cpa_change', 0):.2f}%")
    with col3:
        st.metric("ROI Accuracy", f"{metrics.get('roi_accuracy', 0):.2f}%",
                 delta="25% vs previous model")
    with col4:
        st.metric("Anonymized Users", f"{metrics.get('hashed_users', 0):,}")

def main():
    st.title("CTV Ad Attribution Dashboard")
    st.markdown("### Privacy-Safe Campaign Analytics")
    
    # Real-time metrics
    metrics = fetch_attribution_data()
    if metrics:
        display_kpis(metrics)
        
        # Campaign performance data
        st.divider()
        st.subheader("Campaign Performance")
        
        df = get_campaign_performance()
        if not df.empty:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                # Time-decay vs Last Touch comparison
                fig = px.bar(df, x='campaign_id', y=['time_decay_roi', 'last_touch_roi'],
                            barmode='group', title="ROI by Attribution Model")
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                # CPA distribution
                fig2 = px.pie(df, names='campaign_id', values='cpa',
                             title="Cost Per Acquisition Distribution")
                st.plotly_chart(fig2, use_container_width=True)
                
            # Raw data table
            st.dataframe(df.sort_values('time_decay_roi', ascending=False),
                        hide_index=True,
                        column_config={
                            "campaign_id": "Campaign ID",
                            "impressions": st.column_config.NumberColumn(format="%d"),
                            "cpa": st.column_config.NumberColumn(format="$%.2f")
                        })
        else:
            st.warning("No campaign data available")
    else:
        st.warning("Waiting for backend connection...")

if __name__ == "__main__":
    main()
