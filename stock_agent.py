# -*- coding: utf-8 -*-
"""
Enhanced Stock Analysis Agent with Moneycontrol Pro Integration
"""

import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from urllib.parse import urlparse, quote
import streamlit as st

class StockAnalysisAgent:
    def __init__(self):
        """Initialize the agent with enhanced metrics"""
        self.last_update = None
        self.moneycontrol_base = "https://www.moneycontrol.com/stocks/cptmarket/compsearchnew.php"
        self.indian_ticker_suffixes = ['.NS', '.BO']
        
    def _is_indian_stock(self, ticker):
        """Check if the ticker is for an Indian stock"""
        return any(ticker.upper().endswith(suffix) for suffix in self.indian_ticker_suffixes)
    
    def _get_moneycontrol_url(self, ticker, company_name):
        """Generate Moneycontrol Pro search URL"""
        search_query = quote(company_name)
        return f"{self.moneycontrol_base}?search_data={search_query}&topsearch_type=1&search_str={search_query}"
    
    def _get_company_name(self, info, ticker):
        """Extract company name from info or ticker"""
        return info.get('shortName', ticker.split('.')[0].replace('-', ' ').title())

    def get_historical_data(self, ticker, period="1y"):
        """Get historical data for visualization"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            if hist.empty:
                return None
            return hist[['Close']].reset_index()
        except Exception as e:
            st.warning(f"Could not fetch historical data for {ticker}: {str(e)}")
            return None

    def _is_valid_url(self, url):
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and not result.netloc.startswith('localhost')
        except:
            return False

    def _format_number(self, num, is_currency=True, is_indian=False):
        """Format large numbers for readability"""
        if num is None or num == 'N/A':
            return 'N/A'
        try:
            num = float(num)
            prefix = '₹' if is_indian else '$'
            
            if not is_currency:
                return f"{num:,.2f}"
                
            if num >= 1e12:
                return f"{prefix}{num/1e12:.2f}T"
            if num >= 1e9:
                return f"{prefix}{num/1e9:.2f}B"
            if num >= 1e6:
                return f"{prefix}{num/1e6:.2f}M"
            return f"{prefix}{num:,.2f}"
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
        """Calculate performance percentage"""
        if history is None or len(history) < 2:
            return "N/A"
        try:
            start = history['Close'].iloc[0]
            end = history['Close'].iloc[-1]
            change = ((end - start) / start) * 100
            return f"{change:.2f}%"
        except:
            return "N/A"

    def calculate_delta(self, val1, val2):
        """Calculate delta between two values (public method)"""
        try:
            if val1 is None or val2 is None or val1 == 'N/A' or val2 == 'N/A':
                return None
            diff = float(val1) - float(val2)
            pct_diff = (diff / float(val2)) * 100
            return f"{pct_diff:.1f}% {'above' if diff > 0 else 'below'}"
        except:
            return None

    def get_stock_data(self, ticker):
        """Fetch comprehensive stock data with additional metrics"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            history_1y = stock.history(period='1y')
            history_1m = stock.history(period='1mo')
            history_5d = stock.history(period='5d')
            
            company_name = self._get_company_name(info, ticker)
            is_indian = self._is_indian_stock(ticker)
            
            # Generate Moneycontrol URL
            moneycontrol_url = self._get_moneycontrol_url(ticker, company_name) if is_indian else None
            
            # Process news items
            news = []
            try:
                if hasattr(stock, 'news') and stock.news:
                    for n in stock.news[:3]:  # Get top 3 news items
                        title = str(n.get('title', f"{company_name} News"))
                        publisher = str(n.get('publisher', "Moneycontrol" if is_indian else "Market News"))
                        link = moneycontrol_url if is_indian else str(n.get('link', ''))
                        
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
            
            # Calculate price changes
            current_price = stock.history(period='1d')['Close'].iloc[-1]
            prev_close = info.get('previousClose', current_price)
            day_change_pct = ((current_price - prev_close) / prev_close) * 100
            day_change_abs = current_price - prev_close
            
            # Prepare data dictionary
            data = {
                'current_price': current_price,
                'prev_close': prev_close,
                'day_change_pct': day_change_pct,
                'day_change_abs': day_change_abs,
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'peg_ratio': info.get('pegRatio'),
                'forward_pe': info.get('forwardPE'),
                'price_to_book': info.get('priceToBook'),
                'enterprise_value': info.get('enterpriseValue'),
                'ebitda': info.get('ebitda'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'return_on_equity': info.get('returnOnEquity'),
                '52w_high': info.get('fiftyTwoWeekHigh'),
                '52w_low': info.get('fiftyTwoWeekLow'),
                'avg_volume': info.get('averageVolume'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'recommendation': self._get_recommendation(info.get('recommendationMean')),
                'performance_1y': self._calculate_performance(history_1y),
                'performance_1m': self._calculate_performance(history_1m),
                'performance_5d': self._calculate_performance(history_5d),
                'news': news,
                'company_name': company_name,
                'is_indian': is_indian,
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'employees': info.get('fullTimeEmployees', 'N/A'),
                'historical_data': {
                    '1y': history_1y,
                    '1m': history_1m,
                    '5d': history_5d
                }
            }
            self.last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return data
        except Exception as e:
            st.error(f"Error fetching data for {ticker}: {str(e)}")
            return None

    def generate_comparison(self, ticker1, ticker2):
        """Generate comprehensive comparison report"""
        data1 = self.get_stock_data(ticker1)
        data2 = self.get_stock_data(ticker2)

        if not data1 or not data2:
            return None

        # Prepare comparison metrics
        metrics = [
            ('Current Price', 'current_price', True, True),
            ('Previous Close', 'prev_close', True, True),
            ('Day Change (%)', 'day_change_pct', False, False),
            ('Market Cap', 'market_cap', True, True),
            ('P/E Ratio', 'pe_ratio', False, False),
            ('PEG Ratio', 'peg_ratio', False, False),
            ('Forward P/E', 'forward_pe', False, False),
            ('Price/Book', 'price_to_book', False, False),
            ('Enterprise Value', 'enterprise_value', True, True),
            ('EBITDA', 'ebitda', True, True),
            ('Debt/Equity', 'debt_to_equity', False, False),
            ('Current Ratio', 'current_ratio', False, False),
            ('ROE', 'return_on_equity', False, False),
            ('52W High', '52w_high', True, True),
            ('52W Low', '52w_low', True, True),
            ('Avg Volume', 'avg_volume', True, True),
            ('Dividend Yield', 'dividend_yield', False, False),
            ('Beta', 'beta', False, False),
            ('Analyst Rec', 'recommendation', False, False),
            ('1Y Performance', 'performance_1y', False, False),
            ('1M Performance', 'performance_1m', False, False),
            ('5D Performance', 'performance_5d', False, False),
        ]

        comparison_table = []
        for name, key, is_currency, is_large_num in metrics:
            val1 = data1.get(key, 'N/A')
            val2 = data2.get(key, 'N/A')
            
            # Format values
            if val1 != 'N/A' and is_currency:
                val1 = self._format_number(val1, is_indian=data1['is_indian'])
            if val2 != 'N/A' and is_currency:
                val2 = self._format_number(val2, is_indian=data2['is_indian'])
            
            comparison_table.append({
                'Metric': name,
                ticker1: val1,
                ticker2: val2,
                'Delta': self.calculate_delta(data1.get(key), data2.get(key)) if key not in ['recommendation'] else None
            })

        return {
            'table': pd.DataFrame(comparison_table),
            'data1': data1,
            'data2': data2,
            'is_indian': data1['is_indian'] or data2['is_indian'],
            'last_update': self.last_update
        }
