#!/usr/bin/env python3
"""
GovAI Budget Dashboard - Streamlit Interface
Government expenditure analytics and visualization
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

API_BASE_URL = "http://localhost:8080"

def main():
    st.set_page_config(
        page_title="GovAI Budget Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 GovAI Budget Dashboard")
    st.markdown("**Government Expenditure Analytics & Transparency**")
    
    # Load data
    with st.spinner("Loading analytics data..."):
        analytics_data = load_analytics_data()
    
    if not analytics_data:
        st.error("Could not load analytics data. Please ensure the backend is running.")
        return
    
    # Overview metrics
    display_overview_metrics(analytics_data)
    
    # Charts and visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        display_risk_distribution(analytics_data)
        display_monthly_trends(analytics_data)
    
    with col2:
        display_top_suppliers(analytics_data)
        display_bill_statistics(analytics_data)
    
    # Detailed tables
    display_contract_explorer()
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def load_analytics_data():
    """Load analytics data from API"""
    try:
        response = requests.get(f"{API_BASE_URL}/analytics/dashboard", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Connection error: {e}")
        return None

def display_overview_metrics(data):
    """Display key metrics"""
    st.subheader("📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    contracts = data.get('contracts', {})
    bills = data.get('bills', {})
    
    with col1:
        st.metric(
            "Total Contracts",
            f"{contracts.get('total_contracts', 0):,}",
            "Active contracts"
        )
    
    with col2:
        st.metric(
            "Contract Value",
            f"${contracts.get('total_value', 0):,.0f}",
            "Total USD"
        )
    
    with col3:
        st.metric(
            "Total Bills",
            f"{bills.get('total_bills', 0):,}",
            "Citizen bills"
        )
    
    with col4:
        st.metric(
            "Bill Amount",
            f"Rs. {bills.get('total_amount', 0):,.0f}",
            "Total PKR"
        )

def display_risk_distribution(data):
    """Display contract risk distribution"""
    st.subheader("🚨 Contract Risk Distribution")
    
    risk_data = data.get('contracts', {}).get('risk_distribution', {})
    
    if risk_data:
        # Create pie chart
        labels = list(risk_data.keys())
        values = list(risk_data.values())
        
        colors = {
            'LOW': '#28a745',
            'MEDIUM': '#ffc107', 
            'HIGH': '#fd7e14',
            'CRITICAL': '#dc3545'
        }
        
        fig = px.pie(
            values=values,
            names=labels,
            title="Risk Level Distribution",
            color=labels,
            color_discrete_map=colors
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
        
        # Risk summary
        total_contracts = sum(values)
        high_risk = risk_data.get('HIGH', 0) + risk_data.get('CRITICAL', 0)
        risk_percentage = (high_risk / total_contracts * 100) if total_contracts > 0 else 0
        
        if risk_percentage > 20:
            st.warning(f"⚠️ {risk_percentage:.1f}% of contracts are high/critical risk")
        else:
            st.success(f"✅ Only {risk_percentage:.1f}% of contracts are high/critical risk")
    else:
        st.info("No risk data available")

def display_top_suppliers(data):
    """Display top suppliers by contract value"""
    st.subheader("🏢 Top Suppliers")
    
    suppliers_data = data.get('contracts', {}).get('top_suppliers', {})
    
    if suppliers_data:
        # Convert to DataFrame for plotting
        df = pd.DataFrame(list(suppliers_data.items()), columns=['Supplier', 'Value'])
        df = df.sort_values('Value', ascending=True).tail(10)
        
        # Create horizontal bar chart
        fig = px.bar(
            df,
            x='Value',
            y='Supplier',
            orientation='h',
            title="Top Suppliers by Contract Value",
            labels={'Value': 'Contract Value (USD)', 'Supplier': 'Supplier'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        # Top supplier insight
        if len(df) > 0:
            top_supplier = df.iloc[-1]
            st.info(f"💡 **{top_supplier['Supplier']}** has the highest contract value: ${top_supplier['Value']:,.0f}")
    else:
        st.info("No supplier data available")

def display_monthly_trends(data):
    """Display monthly contract trends"""
    st.subheader("📅 Monthly Contract Trends")
    
    trends_data = data.get('contracts', {}).get('monthly_trends', {})
    
    if trends_data:
        # Convert to DataFrame
        df = pd.DataFrame(list(trends_data.items()), columns=['Month', 'Value'])
        df['Month'] = pd.to_datetime(df['Month'])
        df = df.sort_values('Month')
        
        # Create line chart
        fig = px.line(
            df,
            x='Month',
            y='Value',
            title="Monthly Contract Values",
            labels={'Value': 'Contract Value (USD)', 'Month': 'Month'},
            markers=True
        )
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Trend analysis
        if len(df) > 1:
            latest_value = df.iloc[-1]['Value']
            previous_value = df.iloc[-2]['Value']
            change = ((latest_value - previous_value) / previous_value * 100) if previous_value > 0 else 0
            
            if change > 0:
                st.success(f"📈 Contract values increased by {change:.1f}% last month")
            else:
                st.info(f"📉 Contract values decreased by {abs(change):.1f}% last month")
    else:
        st.info("No trend data available")

def display_bill_statistics(data):
    """Display bill type statistics"""
    st.subheader("🧾 Bill Statistics")
    
    bill_types = data.get('bills', {}).get('by_type', {})
    
    if bill_types:
        # Create donut chart
        labels = list(bill_types.keys())
        values = list(bill_types.values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            title="Bills by Type"
        )])
        
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Bill insights
        total_bills = sum(values)
        avg_amount = data.get('bills', {}).get('avg_amount', 0)
        st.metric("Average Bill Amount", f"Rs. {avg_amount:,.2f}")
    else:
        st.info("No bill data available")

def display_contract_explorer():
    """Contract explorer with filtering"""
    st.subheader("🔍 Contract Explorer")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        risk_filter = st.selectbox(
            "Filter by Risk Level",
            ["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
        )
    
    with col2:
        limit = st.slider("Number of contracts", 10, 500, 100)
    
    with col3:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Load contracts
    contracts_data = load_contracts_data(limit, risk_filter)
    
    if contracts_data and contracts_data.get('contracts'):
        df = pd.DataFrame(contracts_data['contracts'])
        
        # Display table
        st.dataframe(
            df[['contract_number', 'description', 'amount', 'supplier', 'country', 'risk_level', 'risk_score']],
            use_container_width=True
        )
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Contracts Shown", len(df))
        
        with col2:
            st.metric("Total Value", f"${df['amount'].sum():,.0f}")
        
        with col3:
            avg_risk = df['risk_score'].mean()
            st.metric("Average Risk Score", f"{avg_risk:.3f}")
    else:
        st.info("No contracts found matching criteria")

def load_contracts_data(limit=100, risk_level=None):
    """Load contracts data with filters"""
    try:
        params = {"limit": limit}
        if risk_level and risk_level != "All":
            params["risk_level"] = risk_level
        
        response = requests.get(f"{API_BASE_URL}/contracts", params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None

if __name__ == "__main__":
    main()