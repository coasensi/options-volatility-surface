import streamlit as st
import yfinance as yf
import numpy as np
import plotly.graph_objs as go
from datetime import datetime

def fetch_options_data(ticker, option_type='call', style='american'):
    stock = yf.Ticker(ticker)
    expirations = stock.options
    strikes, maturities, ivs = [], [], []
    current_date = datetime.now()

    for expiration in expirations:
        opt_chain = stock.option_chain(expiration)
        options_data = opt_chain.calls if option_type == 'call' else opt_chain.puts
        for _, option in options_data.iterrows():
            strikes.append(option['strike'])
            ivs.append(option['impliedVolatility'])
            expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
            maturity = (expiration_date - current_date).days
            maturities.append(maturity)

    return np.array(strikes), np.array(maturities), np.array(ivs)

def plot_volatility_surface(strikes, maturities, ivs, option_type, style, ticker):
    fig = go.Figure(data=[go.Surface(
        x=strikes,
        y=maturities,
        z=ivs,
        colorscale='Viridis',
        showscale=True
    )])
    fig.update_layout(
        title=f'Volatility Surface for {ticker} {style.capitalize()} {option_type.capitalize()} Options',
        scene=dict(
            xaxis_title='Strike Price',
            yaxis_title='Maturity (Days)',
            zaxis_title='Implied Volatility'
        ),
        autosize=True,
        margin=dict(l=65, r=50, b=65, t=90)
    )
    st.plotly_chart(fig)

def main():
    st.title("Volatility Surface Generator")
    ticker = st.sidebar.text_input("Enter the stock ticker (e.g., AAPL, TSLA): ").upper()
    option_type = st.sidebar.selectbox("Option Type", ('call', 'put'))
    style = 'american'

    if ticker:
        st.write(f"Fetching data for {ticker}...")
        strikes, maturities, ivs = fetch_options_data(ticker, option_type, style)
        if strikes.size > 0 and maturities.size > 0 and ivs.size > 0:
            plot_volatility_surface(strikes, maturities, ivs, option_type, style, ticker)
        else:
            st.write("No data available. Please check the ticker or try a different option type.")
    else:
        st.write("Please enter a stock ticker to generate the volatility surface.")

if __name__ == "__main__":
    main()
