# -*- coding: utf-8 -*-
"""
Stock Analysis Agent with Moneycontrol Pro Integration

Features:
- Financial data comparison using yfinance
- Direct links to Moneycontrol Pro for news
- Robust error handling
- Indian market optimized (.NS, .BO tickers)
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from urllib.parse import quote
import streamlit as st

class StockAnalysisAgent:
    def __init__(self):
        """Initialize the agent with Moneycontrol Pro integration"""
        self.last_update = None
        self.moneycontrol_base = "https://www.moneycontrol.com/stocks/cptmarket/compsearchnew.php"
        self.indian_ticker_suffixes = ['.NS', '.BO']
        
    def _is_indian_stock(self, ticker):
        """Check if the ticker is for an Indian stock"""
        return any(ticker.upper().endswith(suffix) for suffix in self.indian_ticker_suffixes)
    
    def _get_moneycontrol_url(self, ticker, company_name):
        """Generate Moneycontrol Pro search URL for a stock"""
        search_query = quote(company_name)
        return f"{self.moneycontrol_base}?search_data={search_query}&topsearch_type=1&search_str={search_query}"
    
    def _get_company_name(self, info, ticker):
        """Extract company name from info or ticker"""
        return info.get('shortName', ticker.split('.')[0].replace('-', ' ').title())

    def get_stock_data(self, ticker):
        """Fetch comprehensive stock data from yfinance with Moneycontrol links"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history = stock.history(period='1y')
            
            company_name = self._get_company_name(info, ticker)
            is_indian = self._is_indian_stock(ticker)
            
            # Generate Moneycontrol URL for Indian stocks
            moneycontrol_url = self._get_moneycontrol_url(ticker, company_name) if is_indian else None
            
            # Process news items
            news = []
            try:
                if hasattr(stock, 'news') and stock.news:
                    for n in stock.news[:3]:  # Get top 3 news items
                        title = str(n.get('title', f"{company_name} News"))
                        publisher = str(n.get('publisher', "Moneycontrol" if is_indian else "Market News"))
                        
                        # Use Moneycontrol link for Indian stocks, otherwise original link
                        link = moneycontrol_url if is_indian else str(n.get('link', ''))
                        
                        # Fallback to Google search if no valid link
                        if not link or not self._is_valid_url(link):
                            link = f"https://www.google.com/search?q={quote(title)}"
                            
                        news.append({
                            'title': title,
                            'link': link,
                            'publisher': publisher,
                            'is_moneycontrol': is_indian
                        })
            except Exception as e:
                st.warning(f"News parsing error for {ticker}: {str(e)}")
                news = []
            
            # Ensure at least one news item for Indian stocks
            if is_indian and not news:
                news.append({
                    'title': f"Latest {company_name} News on Moneycontrol",
                    'link': moneycontrol_url,
                    'publisher': "Moneycontrol",
                    'is_moneycontrol': True
                })

            data = {
                'current_price': stock.history(period='1d')['Close'].iloc[-1],
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                '52w_high': info.get('fiftyTwoWeekHigh'),
                '52w_low': info.get('fiftyTwoWeekLow'),
                'avg_volume': info.get('averageVolume'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'recommendation': self._get_recommendation(info.get('recommendationMean')),
                'performance': self._calculate_performance(history),
                'news': news,
                'company_name': company_name,
                'is_indian': is_indian
            }
            self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return data
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return None

    def _is_valid_url(self, url):
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and not result.netloc.startswith('localhost')
        except:
            return False

    def _format_number(self, num):
        """Format large numbers for readability"""
        if num is None:
            return 'N/A'
        try:
            num = float(num)
            if num >= 1e12:
                return f"₹{num/1e12:.2f}T"  # Rupee symbol for Indian context
            if num >= 1e9:
                return f"₹{num/1e9:.2f}B"
            if num >= 1e6:
                return f"₹{num/1e6:.2f}M"
            return f"₹{num:,.2f}"
        except:
            return 'N/A'

    def _get_recommendation(self, score):
        """Convert numeric recommendation to text"""
        if score is None:
            return "N/A"
        try:
            score = float(score)
            if score <= 1.5:
                return "Strong Buy"
            elif score <= 2.5:
                return "Buy"
            elif score <= 3.5:
                return "Hold"
            elif score <= 4.5:
                return "Sell"
            else:
                return "Strong Sell"
        except:
            return "N/A"

    def _calculate_performance(self, history):
        """Calculate yearly performance percentage"""
        if len(history) < 2:
            return "N/A"
        start = history['Close'].iloc[0]
        end = history['Close'].iloc[-1]
        change = ((end - start) / start) * 100
        return f"{change:.2f}%"

    def generate_comparison(self, ticker1, ticker2):
        """Generate comparison report with Moneycontrol integration"""
        data1 = self.get_stock_data(ticker1)
        data2 = self.get_stock_data(ticker2)

        if not data1 or not data2:
            return None

        # Prepare comparison data
        metrics = [
            ('Current Price', 'current_price', lambda x: f"₹{x:,.2f}" if data1['is_indian'] else f"${x:,.2f}"),
            ('Market Cap', 'market_cap', self._format_number),
            ('P/E Ratio', 'pe_ratio', lambda x: f"{x:.2f}" if x else 'N/A'),
            ('52W High', '52w_high', lambda x: f"₹{x:,.2f}" if data1['is_indian'] else f"${x:,.2f}"),
            ('52W Low', '52w_low', lambda x: f"₹{x:,.2f}" if data1['is_indian'] else f"${x:,.2f}"),
            ('Avg Volume', 'avg_volume', self._format_number),
            ('Dividend Yield', 'dividend_yield', lambda x: f"{x*100:.2f}%" if x else 'N/A'),
            ('Beta', 'beta', lambda x: f"{x:.2f}" if x else 'N/A'),
            ('Analyst Recommendation', 'recommendation', str),
            ('1Y Performance', 'performance', str)
        ]

        comparison = {
            'Metric': [m[0] for m in metrics],
            ticker1: [m[2](data1[m[1]]) for m in metrics],
            ticker2: [m[2](data2[m[1]]) for m in metrics]
        }

        return {
            'table': pd.DataFrame(comparison),
            'news': {
                ticker1: data1['news'],
                ticker2: data2['news']
            },
            'last_update': self.last_update,
            'is_indian': data1['is_indian'] or data2['is_indian']
        }
