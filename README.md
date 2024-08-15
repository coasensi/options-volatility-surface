This repository hosts a web application designed to illustrate volatility surfaces. 

All the data is sourced from yfinance python API. Thus, the program functions for any stock which options are reported on Yahoo Finance.

The Implied Volatility axis is in decimal format (0.2: 20% Implied Volaility). The strike price and maturity filters allow to exclude extreme IV values from the graph (especially regarding deep ITM options and 0dte), to provide better graph readability.

My work is accessible on: https://greeks.streamlit.app
