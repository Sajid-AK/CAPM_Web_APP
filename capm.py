import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import datetime
import capm_functions

st.set_page_config(page_title ='CAPM', page_icon='chart_with_upwards_trend', layout ='wide')
st.title('Capital Asset Pricing Model')

## getting input form users
col1 , col2 = st.columns([1,1])
with col1:
    stock_list = st.multiselect('Choose 4 Stocks' , ('TSLA', 'AAPL','MSFT','NVDA','GOOGL','MGM'),['TSLA', 'AAPL','MSFT','NVDA'])
with col2:
    year = st.number_input('Number of year ', 1,10)


## Download data for sp500


try:
    # Define the date range
    start = datetime.date(datetime.date.today().year - year, datetime.date.today().month, datetime.date.today().day)
    end = datetime.date.today()
    
    # Get S&P 500 data
    SP500 = web.DataReader(['sp500'], 'fred', start, end)

    # Initialize the stocks DataFrame
    stocks_df = pd.DataFrame()

    # Download stock data
    for stock in stock_list:
        data = yf.download(stock, period=f'{year}y')
        stocks_df[f'{stock}'] = data['Close']

    # Reset index for merging
    stocks_df.reset_index(inplace=True)
    SP500.reset_index(inplace=True)

    # Change column name for merging
    SP500.columns = ['Date', 'sp500']

    # Merge stocks data with SP500 data
    stocks_df = pd.merge(stocks_df, SP500, on='Date', how='inner')

    # Display DataFrame head and tail
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Dataframe head")
        st.dataframe(stocks_df.head(), use_container_width=True)
    with col2:
        st.markdown("### Dataframe Tail")
        st.dataframe(stocks_df.tail(), use_container_width=True)

    # Plot stock prices
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Price of all Stocks")
        st.plotly_chart(capm_functions.interactive_plot(stocks_df))
    with col2:
        st.markdown('### Normalize Price of all Stocks')
        st.plotly_chart(capm_functions.interactive_plot(capm_functions.normalize(stocks_df)))

    # Calculate daily returns
    stocks_daily_return = capm_functions.daily_return(stocks_df)
    print(stocks_daily_return.head())

    # Calculate alpha and beta values
    beta = {}
    alpha = {}
    for i in stocks_daily_return.columns:
        if i != 'Date' and i != 'sp500':
            b, a = capm_functions.calculate_beta(stocks_daily_return, i)
            beta[i] = b
            alpha[i] = a
    print(f'Beta values: {beta},\nAlpha values: {alpha}')

    # Prepare beta DataFrame for display
    beta_df = pd.DataFrame(columns=['Stock', 'Beta Value'])
    beta_df['Stock'] = beta.keys()
    beta_df['Beta Value'] = [str(round(i, 2)) for i in beta.values()]

    # Display beta values
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Calculated Beta Value")
        st.dataframe(beta_df, use_container_width=True)

    # CAPM calculations
    rf = 0  # Risk-free rate
    rm = stocks_daily_return['sp500'].mean() * 252  # Expected market return (annualized)

    return_df = pd.DataFrame()
    return_value = []
    for stock, value in beta.items():
        return_value.append(str(round(rf + (value * (rm - rf)), 2)))
    return_df['Stock'] = stock_list
    return_df['Return Value'] = return_value

    # Display CAPM result
    with col2:
        st.markdown("### Calculated result using CAPM")
        st.dataframe(return_df, use_container_width=True)

except:
    print("Please enter valid inputs. Error:")