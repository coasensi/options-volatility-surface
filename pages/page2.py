# page2.py
# streamlit: name="IV"

import streamlit as st
import yfinance as yf
import numpy as np
import plotly.graph_objs as go
from datetime import datetime

def fetch_options_data(ticker, option_type='call'):
    stock = yf.Ticker(ticker)
    expirations = stock.options
    strikes, maturities, ivs = [], [], []
    current_date = datetime.now()

    for expiration in expirations:
        opt_chain = stock.option_chain(expiration)
        options_data = opt_chain.calls if option_type == 'call' else opt_chain.puts
        expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
        maturity = (expiration_date - current_date).days
        
        for _, option in options_data.iterrows():
            strikes.append(option['strike'])
            ivs.append(option['impliedVolatility'])
            maturities.append(maturity)

    return np.array(strikes), np.array(maturities), np.array(ivs)

# fn to exclude deep ITM and OTM options
def filter_strikes(strikes, maturities, ivs, spot_price, lower_bound=0.5, upper_bound=1.5):
    mask = (strikes >= spot_price * lower_bound) & (strikes <= spot_price * upper_bound)
    return strikes[mask], maturities[mask], ivs[mask]

# fn to exclude options with short maturity
def exclude_short_maturity(strikes, maturities, ivs, min_days_to_expiry=1):
    mask = maturities >= min_days_to_expiry
    return strikes[mask], maturities[mask], ivs[mask]

def plot_volatility_surface(strikes, maturities, ivs, ticker, option_type):
    if len(strikes) == 0 or len(maturities) == 0 or len(ivs) == 0:
        st.error("No data available to plot.")
        return
        
    unique_strikes = np.unique(strikes)
    unique_maturities = np.unique(maturities)

    strike_grid, maturity_grid = np.meshgrid(unique_strikes, unique_maturities)
    iv_grid = np.zeros_like(strike_grid, dtype=float)

    for i, strike in enumerate(unique_strikes):
        for j, maturity in enumerate(unique_maturities):
            mask = (strikes == strike) & (maturities == maturity)
            if mask.any():
                iv_grid[j, i] = ivs[mask].mean()

    fig = go.Figure(data=[go.Surface(
        x=strike_grid,
        y=maturity_grid,
        z=iv_grid,
        colorscale='Viridis',
        showscale=True
    )])

    fig.update_layout(
        title=f'Volatility Surface for {ticker.upper()} {option_type.capitalize()} Options',
        scene=dict(
            xaxis_title='Strike Price',
            yaxis_title='Maturity (Days)',
            zaxis_title='Implied Volatility'
        ),
        autosize=False,
        width=1200,
        height=800,
        margin=dict(l=100, r=100, b=100, t=100)
    )

    st.plotly_chart(fig)

def main():
    st.title("Volatility Surface Generator")
    ticker = st.sidebar.text_input("Enter the stock ticker (e.g., AAPL, TSLA): ").upper()
    option_type = st.sidebar.selectbox("Option Type", ('call', 'put'))

    if ticker:
        strikes, maturities, ivs = fetch_options_data(ticker, option_type)
        stock = yf.Ticker(ticker)
        spot_price = stock.history(period="1d")['Close'][0]

        # strike price filter
        if st.sidebar.checkbox("Filter Strikes by Spot Price", value=True):
            lower_bound = st.sidebar.slider('Lower Bound as % of Spot Price', 0.0, 1.0, 0.5)
            upper_bound = st.sidebar.slider('Upper Bound as % of Spot Price', 1.0, 50, 1.5)
            strikes, maturities, ivs = filter_strikes(strikes, maturities, ivs, spot_price, lower_bound, upper_bound)

        # maturity filter
        if st.sidebar.checkbox("Exclude Short Maturity Options", value=True):
            min_days = st.sidebar.slider('Minimum Days to Expiry', 0, 360, 1)
            strikes, maturities, ivs = exclude_short_maturity(strikes, maturities, ivs, min_days_to_expiry=min_days)

        if strikes.size > 0 and maturities.size > 0 and ivs.size > 0:
            plot_volatility_surface(strikes, maturities, ivs, ticker, option_type)
        else:
            st.write("No data available. Please check the ticker or try a different option type.")
    else:
        st.write("Please enter a stock ticker to generate the volatility surface.")

if __name__ == "__main__":
    main()
