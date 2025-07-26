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
                        val1 = result['data1'][key]
                        val2 = result['data2'][key]
                        
                        if is_currency and val1 != 'N/A' and isinstance(val1, (int, float)):
                            val1 = f"{prefix}{val1:,.2f}"
                            val2 = f"{prefix}{val2:,.2f}"
                        
                        delta = self._calculate_delta(result['data1'][key], result['data2'][key]) if key != 'market_cap' else None
                        
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
                except Exception as e:
                    st.warning(f"Could not load historical data: {str(e)}")
                
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
                        val1 = result['data1'][key]
                        val2 = result['data2'][key]
                        
                        if key == 'enterprise_value' and val1 != 'N/A':
                            val1 = f"₹{val1/1e12:.2f}T" if result['is_indian'] else f"${val1/1e12:.2f}T"
                            val2 = f"₹{val2/1e12:.2f}T" if result['is_indian'] else f"${val2/1e12:.2f}T"
                        
                        st.metric(
                            label=name,
                            value=val1 if val1 else 'N/A',
                            delta=self._calculate_delta(result['data1'][key], result['data2'][key]) if key not in ['enterprise_value', 'ebitda'] else None
                        )
                        st.caption(f"{ticker2}: {val2 if val2 else 'N/A'}")

with tab2:
    # [Previous comparative analysis content]
    pass

with tab3:
    # [Previous news content]
    pass

# Footer
st.markdown("---")
st.caption("""
**Data Sources:** Yahoo Finance | Moneycontrol Pro  
**Disclaimer:** This tool is for informational purposes only. Please consult a financial advisor before making investment decisions.
""")

def _calculate_delta(self, val1, val2):
    """Helper method to calculate delta between two values"""
    try:
        if val1 is None or val2 is None or val1 == 'N/A' or val2 == 'N/A':
            return None
        diff = float(val1) - float(val2)
        return f"{abs(diff):.2f} {'higher' if diff > 0 else 'lower'}"
    except:
        return None
