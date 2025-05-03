# India Options Quant

A Streamlit application for option pricing and gamma squeeze analysis for Indian equity markets.

## Features

- Black-Scholes option pricing model
- Calculate option Greeks (Delta, Gamma, Vega, Theta, Rho)
- Gamma squeeze risk assessment
- User-friendly interface with adjustable parameters

## Installation

1. Clone this repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit app:
```
streamlit run app.py
```

The app will open in your browser, where you can:
- Adjust the spot price, strike price, days to expiry, etc.
- View the calculated option price
- Check the Greeks values
- See the gamma squeeze risk assessment

## Requirements

- Python 3.7+
- Streamlit
- SciPy