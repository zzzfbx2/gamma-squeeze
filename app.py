# India Options Quant Starter Setup with Streamlit

import streamlit as st
from math import log, sqrt, exp
from scipy.stats import norm
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

# Set page configuration and theme
st.set_page_config(
    page_title="India Options Pricer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1.5rem;
        border-bottom: 1px solid #42A5F5;
        padding-bottom: 0.3rem;
    }
    .card {
        background-color: transparent;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border: none;
        box-shadow: none;
    }
    .highlight-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1565C0;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #0D47A1;
    }
    .risk-high {
        color: #D32F2F;
        font-weight: bold;
    }
    .risk-medium {
        color: #FB8C00;
        font-weight: bold;
    }
    .risk-low {
        color: #388E3C;
        font-weight: bold;
    }
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        font-size: 0.9rem;
        color: #616161;
        background-color: #f5f5f5;
        border-top: 1px solid #e0e0e0;
    }
    .footer a {
        color: #1976D2;
        text-decoration: none;
    }
    .heart {
        color: #E91E63;
        animation: heartbeat 1.5s infinite;
    }
    @keyframes heartbeat {
        0% { transform: scale(1); }
        25% { transform: scale(1.1); }
        50% { transform: scale(1); }
        75% { transform: scale(1.1); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Black-Scholes Model
def black_scholes_price(S, K, T, r, sigma, option_type):
    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    if option_type == 'call':
        price = S * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
    elif option_type == 'put':
        price = K * exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        raise ValueError("Invalid option type")
    return price

# Greeks Calculation
def greeks(S, K, T, r, sigma, option_type):
    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    delta = norm.cdf(d1) if option_type == 'call' else -norm.cdf(-d1)
    gamma = norm.pdf(d1) / (S * sigma * sqrt(T))
    vega = S * norm.pdf(d1) * sqrt(T) / 100
    theta_call = (-S * norm.pdf(d1) * sigma / (2 * sqrt(T)) - r * K * exp(-r * T) * norm.cdf(d2)) / 365
    theta_put = (-S * norm.pdf(d1) * sigma / (2 * sqrt(T)) + r * K * exp(-r * T) * norm.cdf(-d2)) / 365
    rho_call = K * T * exp(-r * T) * norm.cdf(d2) / 100
    rho_put = -K * T * exp(-r * T) * norm.cdf(-d2) / 100
    theta = theta_call if option_type == 'call' else theta_put
    rho = rho_call if option_type == 'call' else rho_put
    return {
        'Delta': delta,
        'Gamma': gamma,
        'Vega': vega,
        'Theta': theta,
        'Rho': rho
    }

# Gamma Squeeze Detector
def gamma_squeeze_likelihood(gamma, days_to_expiry):
    if gamma > 0.02 and days_to_expiry <= 2:
        return {
            "text": "⚠️ High Gamma + Near Expiry → Gamma Squeeze Likely",
            "level": "high",
            "score": 9
        }
    elif gamma > 0.015:
        return {
            "text": "Moderate Gamma Exposure → Monitor for squeeze",
            "level": "medium",
            "score": 6
        }
    else:
        return {
            "text": "Low Gamma Squeeze Risk",
            "level": "low",
            "score": 3
        }

# Generate price simulation data
def generate_price_simulation(S, days=7, volatility=0.02, simulations=1):
    daily_returns = []
    prices = [S]
    
    for i in range(days):
        daily_return = norm.rvs(0, volatility)
        daily_returns.append(daily_return)
        new_price = prices[-1] * (1 + daily_return)
        prices.append(new_price)
    
    return prices

# Streamlit UI
st.markdown("<h1 class='main-header'>🇮🇳 Gamma Squeeze Indicator</h1>", unsafe_allow_html=True)

# Add a brief introduction
with st.expander("ℹ️ About this app", expanded=False):
    st.markdown("""
    This app uses the Black-Scholes model to price options and calculate Greeks for the Indian markets. 
    It also provides a gamma squeeze risk assessment based on gamma values and days to expiry.
    
    **How to use:**
    1. Enter your parameters in the sidebar
    2. Click "Calculate" to update the results
    3. Analyze the option pricing, Greeks, and risk metrics
    """)

# Sidebar styling
st.sidebar.markdown("<div class='sidebar-header'>📊 Input Parameters</div>", unsafe_allow_html=True)

# Instead of tabs, use a simple header for the main content
st.markdown("<h2 class='subheader' style='margin-top: 0;'>📈 Option Analysis</h2>", unsafe_allow_html=True)

with st.sidebar.form("input_form"):
    # Add stock/index name field at the top
    stock_name = st.text_input("Stock/Index Name", value="NIFTY 50", help="Enter the name of the underlying stock or index")
    
    st.markdown("<hr style='margin: 15px 0px; border: none; height: 1px; background-color: #e0e0e0;'>", unsafe_allow_html=True)
    
    # Create two columns for the remaining inputs
    col1, col2 = st.columns(2)
    
    with col1:
        S = st.number_input("Spot Price (₹)", min_value=100.0, max_value=100000.0, value=24420.0, step=10.0)
        days_to_expiry = st.number_input("Days to Expiry", min_value=1, max_value=365, value=3, step=1)
        sigma = st.number_input("IV (%)", min_value=1.0, max_value=100.0, value=18.0, step=0.5) / 100
    
    with col2:
        K = st.number_input("Strike Price (₹)", min_value=100.0, max_value=100000.0, value=24500.0, step=10.0)
        r = st.number_input("Risk-Free Rate (%)", min_value=1.0, max_value=15.0, value=6.5, step=0.1) / 100
        option_type = st.selectbox("Option Type", ["call", "put"])
    
    calculate_button = st.form_submit_button("💲 Calculate")

# Calculate time to expiry in years
T = days_to_expiry / 365

# Calculations
price = black_scholes_price(S, K, T, r, sigma, option_type)
greek_values = greeks(S, K, T, r, sigma, option_type)
gamma_signal = gamma_squeeze_likelihood(greek_values['Gamma'], days_to_expiry)

# Generate price simulation
price_simulation = generate_price_simulation(S, days=7, volatility=sigma/3)

# Display selected stock/index name at the top
st.markdown(f"<h2 style='text-align: center; margin-bottom: 20px;'>Analysis for <span style='color: #1565C0;'>{stock_name}</span></h2>", unsafe_allow_html=True)

# Top row with key metrics
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"<h3 style='text-align: center;'>Option Type</h3>", unsafe_allow_html=True)
    st.markdown(f"<p class='highlight-value' style='text-align: center;'>{option_type.upper()}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Strike: ₹{K:,.2f}</p>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<h3 style='text-align: center;'>Fair Value</h3>", unsafe_allow_html=True)
    st.markdown(f"<p class='highlight-value' style='text-align: center;'>₹{price:,.2f}</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>Spot: ₹{S:,.2f}</p>", unsafe_allow_html=True)

with col3:
    st.markdown(f"<h3 style='text-align: center;'>Time to Expiry</h3>", unsafe_allow_html=True)
    st.markdown(f"<p class='highlight-value' style='text-align: center;'>{days_to_expiry} Days</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>IV: {sigma*100:.1f}%</p>", unsafe_allow_html=True)

# Greeks section
st.markdown("<h2 class='subheader'>Option Greeks</h2>", unsafe_allow_html=True)

greek_cols = st.columns(5)
greek_names = list(greek_values.keys())

for i, col in enumerate(greek_cols):
    greek_name = greek_names[i]
    greek_value = greek_values[greek_name]
    
    col.markdown(f"<h3 style='text-align: center;'>{greek_name}</h3>", unsafe_allow_html=True)
    col.markdown(f"<p class='highlight-value' style='text-align: center;'>{greek_value:.4f}</p>", unsafe_allow_html=True)

# Gamma squeeze analysis
st.markdown("<h2 class='subheader'>Gamma Squeeze Risk Analysis</h2>", unsafe_allow_html=True)

risk_class = f"risk-{gamma_signal['level']}"

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"<p class='{risk_class}'>{gamma_signal['text']}</p>", unsafe_allow_html=True)
    st.markdown(f"<p>Gamma: {greek_values['Gamma']:.4f} | Days to Expiry: {days_to_expiry}</p>", unsafe_allow_html=True)

with col2:
    # Risk meter
    progress_color = {
        "high": "#D32F2F",
        "medium": "#FB8C00",
        "low": "#388E3C"
    }
    
    st.markdown(f"<p style='text-align: center;'>Risk Score: {gamma_signal['score']}/10</p>", unsafe_allow_html=True)
    st.progress(gamma_signal['score']/10, text=None)

# Market Insights Section
st.markdown("<h2 class='subheader'>Market Insights</h2>", unsafe_allow_html=True)

# Price Simulation
st.markdown("<h3 style='margin-top: 1.5rem; color: #1976D2;'>Price Simulation (7 Days)</h3>", unsafe_allow_html=True)

# Convert to dataframe for Altair
df = pd.DataFrame({
    'Day': range(len(price_simulation)),
    'Price': price_simulation
})

# Create chart
chart = alt.Chart(df).mark_line(point=True).encode(
    x=alt.X('Day:O', title='Trading Day'),
    y=alt.Y('Price:Q', title=f'{stock_name} Price (₹)', scale=alt.Scale(zero=False)),
    tooltip=['Day:O', 'Price:Q']
).properties(
    height=300,
    title=f"{stock_name} Price Simulation (Next 7 Trading Days)"
).interactive()

st.altair_chart(chart, use_container_width=True)

# Profit/Loss Analysis
st.markdown("<h3 style='margin-top: 1.5rem; color: #1976D2;'>Profit/Loss at Expiry</h3>", unsafe_allow_html=True)

# Generate P/L data for chart
price_range = [S * (1 + i/100) for i in range(-10, 11, 2)]

if option_type == 'call':
    pnl = [max(0, p - K) - price for p in price_range]
else:
    pnl = [max(0, K - p) - price for p in price_range]

pnl_df = pd.DataFrame({
    'Price': price_range,
    'P/L': pnl
})

pnl_chart = alt.Chart(pnl_df).mark_line(point=True).encode(
    x=alt.X('Price:Q', title=f'{stock_name} Price at Expiry (₹)'),
    y=alt.Y('P/L:Q', title='Profit/Loss (₹)'),
    tooltip=['Price:Q', 'P/L:Q'],
    color=alt.condition(
        alt.datum['P/L'] > 0,
        alt.value("#388E3C"),  # green for profit
        alt.value("#D32F2F")   # red for loss
    )
).properties(
    height=250,
    title=f"{stock_name} {option_type.upper()} Option P/L at Expiry"
).interactive()

st.altair_chart(pnl_chart, use_container_width=True)

# Add footer
st.markdown("""
<div class="footer">
    Made with <span class="heart">❤</span> by Raj Matharasi
</div>
""", unsafe_allow_html=True)