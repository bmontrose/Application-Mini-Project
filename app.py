import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from stock_analysis import analyze_breakouts

# Page configuration
st.set_page_config(
    page_title="Stock Breakout Analyzer",
    page_icon="📈",
    layout="wide"
)

# Title and description
st.title('📈 Stock Breakout Analyzer')
st.markdown("""
This tool analyzes stock breakouts based on volume and price changes. It identifies potential breakout 
opportunities when:
- Daily volume exceeds the 20-day average volume by a specified percentage
- Price increases by a minimum specified percentage
""")

# Input form
with st.form("analysis_form"):
    col1, col2, col3 = st.columns([2,1,1])
    
    with col1:
        ticker = st.text_input('Enter Stock Ticker:', value='AAPL').upper()
    
    with col2:
        start_date = st.date_input('Start Date', 
                                 value=datetime.now() - timedelta(days=365))
    with col3:
        end_date = st.date_input('End Date')

    col4, col5, col6 = st.columns(3)
    
    with col4:
        volume_threshold = st.number_input('Volume Breakout Threshold (%)', 
                                         value=200, min_value=0)
    with col5:
        price_threshold = st.number_input('Price Change Threshold (%)', 
                                        value=2.0, step=0.1)
    with col6:
        holding_period = st.number_input('Holding Period (Days)', 
                                       value=10, min_value=1)

    submitted = st.form_submit_button('Generate Report')

if submitted:
    with st.spinner('Analyzing breakouts...'):
        try:
            results_df = analyze_breakouts(
                ticker, 
                start_date, 
                end_date, 
                volume_threshold, 
                price_threshold, 
                holding_period
            )
            
            if len(results_df) > 0:
                # Results section
                st.subheader('Analysis Results')
                
                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Number of Breakouts", len(results_df))
                with col2:
                    avg_return = results_df['Return'].mean()
                    st.metric("Average Return", f"{avg_return:.2f}%")
                with col3:
                    win_rate = (results_df['Return'] > 0).mean() * 100
                    st.metric("Win Rate", f"{win_rate:.1f}%")
                with col4:
                    best_return = results_df['Return'].max()
                    st.metric("Best Return", f"{best_return:.2f}%")
                
                # Detailed results
                st.dataframe(results_df, use_container_width=True)
                
                # Download button
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Results as CSV",
                    data=csv,
                    file_name=f"{ticker}_breakout_analysis.csv",
                    mime="text/csv"
                )
            else:
                st.warning('No breakouts found for the given parameters.')
                
        except Exception as e:
            st.error(f'Error analyzing data: {str(e)}')
            st.error('Please check the ticker symbol and try again.')
