# -*- coding: utf-8 -*-
"""
Enhanced Stock Comparison Dashboard with Visualizations
"""

import streamlit as st
from stock_agent import StockAnalysisAgent
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set up the app
st.set_page_config(
    page_title="StockInsight Pro",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the agent
agent = StockAnalysisAgent()

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .positive {
        background-color: #e6f7e6;
        border-left: 5px solid #2ecc71;
    }
    .negative {
        background-color: #ffebee;
        border-left: 5px solid #e74c3c;
    }
    .neutral {
        background-color: #e3f2fd;
        border-left: 5px solid #3498db;
    }
    .header-text {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
    }
    .delta-positive {
        color: #27ae60;
    }
    .delta-negative {
        color: #e74c3c;
    }
</style>
""", unsafe_allow_html=True)

# App header
st.title("💹 StockInsight Pro")
st.markdown("""
**Advanced stock comparison tool** with Moneycontrol Pro integration, financial metrics, and interactive visualizations.
""")

# Sidebar
with st.sidebar:
    st.header("🔍 Stock Selection")
    col1, col2 = st.columns(2)
    with col1:
        ticker1 = st.text_input("Stock 1", "TATAMOTORS.NS").upper()
    with col2:
        ticker2 = st.text_input("Stock 2", "M&M.BO").upper()
    
    st.markdown("""
    **Ticker Formats:**
    - Indian: `TATAMOTORS.NS` (NSE), `M&M.BO` (BSE)
    - US: `AAPL`, `TSLA`
    - Add exchange suffix for non-US stocks
    """)
    
    st.markdown("---")
    st.markdown("**📊 Display Options**")
    chart_days = st.slider("Chart Period (Days)", 30, 365, 90)
    st.caption("💡 Pro Tip: Compare stocks from the same sector for better insights")

# Main tabs
tab1, tab2, tab3 = st.tabs(["📈 Financial Dashboard", "📊 Comparative Analysis", "📰 News & Research"])

with tab1:
    if st.button("🔄 Analyze Stocks", type="primary", use_container_width=True):
        with st.spinner("Crunching the latest market data..."):
            result = agent.generate_comparison(ticker1, ticker2)
            
            if result:
                # Header with basic info
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader(f"{ticker1} - {result['data1']['company_name']}")
                    st.caption(f"Sector: {result['data1']['sector']} | Industry: {result['data1']['industry']}")
                with col2:
                    st.subheader(f"{ticker2} - {result['data2']['company_name']}")
                    st.caption(f"Sector: {result['data2']['sector']} | Industry: {result['data2']['industry']}")
                
                st.markdown("---")
                
                # Key Metrics Row 1
                st.subheader("📌 Key Metrics Comparison")
                cols = st.columns(4)
                metrics = [
                    ('Current Price', 'current_price', True, '₹' if result['is_indian'] else '$'),
                    ('Market Cap', 'market_cap', True, ''),
                    ('P/E Ratio', 'pe_ratio', False, ''),
                    ('PEG Ratio', 'peg_ratio', False, ''),
                ]
                
                for i, (name, key, is_currency, prefix) in enumerate(metrics):
                    with cols[i]:
                        val1 = result['data1'].get(key, 'N/A')
                        val2 = result['data2'].get(key, 'N/A')
                        
                        if is_currency and val1 != 'N/A' and isinstance(val1, (int, float)):
                            val1 = f"{prefix}{val1:,.2f}" if prefix else val1
                            val2 = f"{prefix}{val2:,.2f}" if prefix else val2
                        
                        delta = agent.calculate_delta(result['data1'].get(key), result['data2'].get(key)) if key != 'market_cap' else None
                        
                        st.metric(
                            label=name,
                            value=val1 if val1 else 'N/A',
                            delta=delta,
                            delta_color="inverse" if name in ['P/E Ratio', 'PEG Ratio'] else "normal"
                        )
                        st.caption(f"{ticker2}: {val2 if val2 else 'N/A'}")
                
                # Price Performance Visualization
                st.markdown("---")
                st.subheader("📈 Price Performance")
                
                try:
                    hist1 = agent.get_historical_data(ticker1, f"{chart_days}d")
                    hist2 = agent.get_historical_data(ticker2, f"{chart_days}d")
                    
                    if hist1 is not None and hist2 is not None:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=hist1['Date'], y=hist1['Close'],
                            name=ticker1, line=dict(color='#3498db')))
                        fig.add_trace(go.Scatter(
                            x=hist2['Date'], y=hist2['Close'],
                            name=ticker2, line=dict(color='#e74c3c')))
                        
                        fig.update_layout(
                            hovermode="x unified",
                            showlegend=True,
                            xaxis_title="Date",
                            yaxis_title="Price",
                            template="plotly_white",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.warning("Could not load historical price data for one or both stocks")
                except Exception as e:
                    st.warning(f"Could not generate price chart: {str(e)}")
                
                # Valuation Metrics
                st.markdown("---")
                st.subheader("🏦 Valuation Metrics")
                
                valuation_metrics = [
                    ('Forward P/E', 'forward_pe'),
                    ('Price/Book', 'price_to_book'),
                    ('Enterprise Value', 'enterprise_value'),
                    ('EBITDA', 'ebitda')
                ]
                
                cols = st.columns(len(valuation_metrics))
                for i, (name, key) in enumerate(valuation_metrics):
                    with cols[i]:
                        val1 = result['data1'].get(key, 'N/A')
                        val2 = result['data2'].get(key, 'N/A')
                        
                        if key == 'enterprise_value' and val1 != 'N/A':
                            val1 = f"₹{val1/1e12:.2f}T" if result['is_indian'] else f"${val1/1e12:.2f}T"
                            val2 = f"₹{val2/1e12:.2f}T" if result['is_indian'] else f"${val2/1e12:.2f}T"
                        
                        st.metric(
                            label=name,
                            value=val1 if val1 else 'N/A',
                            delta=agent.calculate_delta(result['data1'].get(key), result['data2'].get(key)) if key not in ['enterprise_value', 'ebitda'] else None
                        )
                        st.caption(f"{ticker2}: {val2 if val2 else 'N/A'}")

with tab2:
    if st.button("🔄 Generate Comparison", key="compare_btn", type="primary"):
        result = agent.generate_comparison(ticker1, ticker2)
        if result:
            st.subheader("📊 Side-by-Side Comparison")
            
            # Create styled dataframe
            df = result['table']
            st.dataframe(
                df.style.apply(
                    lambda x: ['background: #f7f7f7' if i%2==0 else '' for i in range(len(x))],
                    axis=0
                ),
                use_container_width=True,
                height=(len(df)*35 + 38)
            )

with tab3:
    if st.button("🔄 Get Latest News", key="news_btn", type="primary"):
        result = agent.generate_comparison(ticker1, ticker2)
        if result:
            st.subheader("📰 Latest News & Research")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### {ticker1} News")
                if result['data1']['news']:
                    for item in result['data1']['news']:
                        st.markdown(f"""
                        <div class="metric-card {'positive' if item['is_moneycontrol'] else 'neutral'}">
                            <a href="{item['link']}" target="_blank" style="color: inherit; text-decoration: none;">
                                <b>{item['title']}</b><br>
                                <small>{item['publisher']}</small>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No recent news found")
            
            with col2:
                st.markdown(f"### {ticker2} News")
                if result['data2']['news']:
                    for item in result['data2']['news']:
                        st.markdown(f"""
                        <div class="metric-card {'positive' if item['is_moneycontrol'] else 'neutral'}">
                            <a href="{item['link']}" target="_blank" style="color: inherit; text-decoration: none;">
                                <b>{item['title']}</b><br>
                                <small>{item['publisher']}</small>
                            </a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No recent news found")

            if result['is_indian']:
                st.info("ℹ️ You're viewing Moneycontrol Pro links. Login to your Pro account for full research reports.")

# Footer
st.markdown("---")
st.caption("""
**Data Sources:** Yahoo Finance | Moneycontrol Pro  
**Disclaimer:** This tool is for informational purposes only. Please consult a financial advisor before making investment decisions.
""")
