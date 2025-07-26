# -*- coding: utf-8 -*-
"""
Stock Comparison Agent with Moneycontrol Pro Integration

Features:
- Financial metrics comparison
- Direct Moneycontrol Pro links for Indian stocks
- Enhanced visualization
- Better error handling
"""

import streamlit as st
from stock_agent import StockAnalysisAgent
import pandas as pd
from datetime import datetime

# Set up the app
st.set_page_config(
    page_title="Stock Comparison Agent Pro",
    page_icon="📈",
    layout="wide",
    menu_items={
        'About': "Stock Comparison Agent with Moneycontrol Pro integration"
    }
)

# Initialize the agent
agent = StockAnalysisAgent()

# App title and description
st.title("📈 Stock Comparison Agent Pro")
st.markdown("""
Compare financial metrics with **direct Moneycontrol Pro links** for Indian stocks.
""")

# Sidebar for user input
with st.sidebar:
    st.header("🔧 Input Parameters")
    col1, col2 = st.columns(2)
    with col1:
        ticker1 = st.text_input("First Stock", "TATAMOTORS.NS").upper()
    with col2:
        ticker2 = st.text_input("Second Stock", "M&M.BO").upper()
    
    st.markdown("""
    **Ticker Formats:**
    - Indian: `TATAMOTORS.NS` (NSE), `M&M.BO` (BSE)
    - US: `AAPL`, `TSLA`
    - Add exchange suffix for non-US stocks
    """)
    
    st.markdown("---")
    st.caption("💡 Pro Tip: Login to Moneycontrol for full access to news and analysis")

# Main content area
tab1, tab2 = st.tabs(["📊 Financial Comparison", "📰 News & Research"])

with tab1:
    st.header("Financial Metrics Comparison")
    if st.button("🔍 Compare Stocks", type="primary"):
        with st.spinner("Fetching latest market data..."):
            result = agent.generate_comparison(ticker1, ticker2)
            
            if result:
                # Display comparison table with conditional formatting
                st.dataframe(
                    result['table'].style.apply(
                        lambda x: ['background: #f7f7f7' if i%2==0 else '' for i in range(len(x))],
                        axis=0
                    ),
                    use_container_width=True,
                    hide_index=True,
                    height=(len(result['table'])*35 + 38),
                    column_config={
                        "Metric": st.column_config.Column(width="medium"),
                        ticker1: ticker1,
                        ticker2: ticker2
                    }
                )
                
                # Key metrics comparison
                st.subheader("💡 Key Insights")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    try:
                        pe1 = float(result['table'].loc[2, ticker1])
                        pe2 = float(result['table'].loc[2, ticker2])
                        pe_diff = pe1 - pe2
                        st.metric(
                            label="P/E Ratio Comparison",
                            value=f"{pe1:.1f} vs {pe2:.1f}",
                            delta=f"{abs(pe_diff):.1f} {'lower' if pe_diff < 0 else 'higher'}",
                            delta_color="inverse"
                        )
                    except:
                        pass
                
                with col2:
                    try:
                        reco1 = result['table'].loc[8, ticker1]
                        reco2 = result['table'].loc[8, ticker2]
                        st.metric(
                            label="Analyst Consensus",
                            value=f"{reco1} vs {reco2}",
                            help="Strong Buy < Buy < Hold < Sell < Strong Sell"
                        )
                    except:
                        pass
                
                with col3:
                    try:
                        perf1 = result['table'].loc[9, ticker1]
                        perf2 = result['table'].loc[9, ticker2]
                        st.metric(
                            label="1Y Performance",
                            value=f"{perf1} vs {perf2}",
                            help="Year-over-year price change"
                        )
                    except:
                        pass
                
                st.caption(f"🔄 Last updated: {result['last_update']}")

with tab2:
    st.header("News & Research")
    if st.button("🔄 Fetch Latest Updates", type="primary"):
        with st.spinner("Gathering latest market news..."):
            result = agent.generate_comparison(ticker1, ticker2)
            
            if result:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(f"📌 {ticker1}")
                    if result['news'][ticker1]:
                        for item in result['news'][ticker1]:
                            st.markdown(f"""
                            <div style="
                                padding: 12px;
                                margin-bottom: 12px;
                                border-radius: 8px;
                                background-color: #f8f9fa;
                                border-left: 4px solid {'#2e86de' if item['is_moneycontrol'] else '#10ac84'};
                            ">
                                <a href="{item['link']}" target="_blank" style="color: inherit; text-decoration: none;">
                                    <b>{item['title']}</b><br>
                                    <small style="color: {'#2e86de' if item['is_moneycontrol'] else '#10ac84'}">
                                        🔗 {item['publisher']} {'(Moneycontrol Pro)' if item['is_moneycontrol'] else ''}
                                    </small>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("No recent news found", icon="⚠️")
                
                with col2:
                    st.subheader(f"📌 {ticker2}")
                    if result['news'][ticker2]:
                        for item in result['news'][ticker2]:
                            st.markdown(f"""
                            <div style="
                                padding: 12px;
                                margin-bottom: 12px;
                                border-radius: 8px;
                                background-color: #f8f9fa;
                                border-left: 4px solid {'#2e86de' if item['is_moneycontrol'] else '#10ac84'};
                            ">
                                <a href="{item['link']}" target="_blank" style="color: inherit; text-decoration: none;">
                                    <b>{item['title']}</b><br>
                                    <small style="color: {'#2e86de' if item['is_moneycontrol'] else '#10ac84'}">
                                        🔗 {item['publisher']} {'(Moneycontrol Pro)' if item['is_moneycontrol'] else ''}
                                    </small>
                                </a>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.warning("No recent news found", icon="⚠️")
                
                if result.get('is_indian', False):
                    st.info("ℹ️ You're viewing Moneycontrol Pro links. Login to your Pro account for full research reports.", icon="💎")
                
                st.caption(f"🔄 Last updated: {result['last_update']}")

# Footer
st.markdown("---")
st.caption("""
**Data Sources:**  
• Stock data from Yahoo Finance (yfinance)  
• News links direct to Moneycontrol Pro for Indian stocks  
• Global stocks show original sources when available  
""")
