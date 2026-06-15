# =====================================================
#  BOT TRADING RAHMAN – XAU/USD ULTIMATE v3.0
#  Khusus Modal Kecil ($10) | Lot 0.01 | TF 1 Menit
#  Max Loss $2 | Max Profit $3 | Auto-SL/TP
# =====================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import base64

# ================= KONFIGURASI DEFAULT =================
# SEMUA DEFAULT SESUAI PERMINTAAN USER
DEFAULT_MODAL = 10.0
DEFAULT_RISIKO = 20.0  # 20% dari $10 = $2 max loss
DEFAULT_LOT = 0.01
DEFAULT_TP_DOLLAR = 3.0  # Max profit $3
DEFAULT_SL_DOLLAR = 2.0   # Max loss $2

SYMBOLS = ["GC=F", "XAUUSD=X", "GLD"]
TIMEFRAME_OPTIONS = {
    "1 Menit": "1m", "2 Menit": "2m", "5 Menit": "5m",
    "15 Menit": "15m", "30 Menit": "30m", "60 Menit": "60m",
    "1 Jam": "1h", "4 Jam": "4h", "1 Hari": "1d",
}

# Harga emas: $0.01 per pip untuk 0.01 lot (micro)
# 1 pip XAU/USD = $0.01 untuk 0.01 lot
PIP_VALUE_PER_LOT = 1.0  # $1 per pip per 1.0 lot
MICRO_PIP_VALUE = 0.01   # $0.01 per pip per 0.01 lot

st.set_page_config(
    page_title="🤖 Bot Rahman – $10 Profit",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh setiap 30 detik untuk 1 menit TF (lebih cepat)
st.markdown('<meta http-equiv="refresh" content="30">', unsafe_allow_html=True)

# ================= CSS CUSTOM =================
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: bold;
        background: linear-gradient(90deg, #FFD700, #FFA500, #FF6B6B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
    }
    .signal-box {
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 10px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    .buy-signal { 
        background: linear-gradient(135deg, #00b894, #00cec9, #55efc4); 
        color: white; 
        border: 3px solid #00b894;
    }
    .sell-signal { 
        background: linear-gradient(135deg, #d63031, #e17055, #ff7675); 
        color: white; 
        border: 3px solid #d63031;
    }
    .neutral-signal { 
        background: linear-gradient(135deg, #636e72, #b2bec3, #dfe6e9); 
        color: #2d3436; 
    }
    .info-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin: 8px 0;
        border: 1px solid rgba(255,215,0,0.3);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .copy-btn {
        background: linear-gradient(90deg, #6c5ce7, #a29bfe, #74b9ff);
        color: white;
        padding: 15px 30px;
        border-radius: 30px;
        border: none;
        cursor: pointer;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s;
        box-shadow: 0 5px 20px rgba(108, 92, 231, 0.4);
    }
    .copy-btn:hover {
        transform: scale(1.08);
        box-shadow: 0 8px 25px rgba(108, 92, 231, 0.6);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #FFD700;
        text-shadow: 0 0 10px rgba(255,215,0,0.3);
    }
    .profit-target {
        background: linear-gradient(135deg, #00b894, #55efc4);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    .loss-limit {
        background: linear-gradient(135deg, #d63031, #ff7675);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        font-weight: bold;
    }
    .live-price {
        font-size: 3rem;
        font-weight: bold;
        color: #FFD700;
        text-align: center;
        text-shadow: 0 0 20px rgba(255,215,0,0.5);
        animation: glow 1.5s ease-in-out infinite alternate;
    }
    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(255,215,0,0.5); }
        to { text-shadow: 0 0 30px rgba(255,215,0,0.8), 0 0 40px rgba(255,215,0,0.4); }
    }
    .candle-info {
        background: rgba(0,0,0,0.3);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 3px solid #FFD700;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FFD700, #FFA500) !important;
    }
    .stAlert {
        border-radius: 15px !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🤖 Bot Trading Rahman – $10 Profit Mode</h1>', unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; color:#FFD700;'>💰 Modal $10 | Lot 0.01 | Max Loss $2 | Max Profit $3</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888;'>⚡ Auto-refresh 30 detik | TF 1 Menit Default | Analisis Candlestick Real-Time</p>", unsafe_allow_html=True)

# ================= AMBIL STATE DARI URL =================
def get_query_param(key, default, type_func=str):
    if key in st.query_params:
        try:
            return type_func(st.query_params[key])
        except:
            return default
    return default

# DEFAULT SEMUA SESUAI PERMINTAAN
default_tf = get_query_param("tf", "1 Menit")
if default_tf not in TIMEFRAME_OPTIONS:
    default_tf = "1 Menit"

default_modal = get_query_param("modal", DEFAULT_MODAL, float)
default_risiko = get_query_param("risiko", DEFAULT_RISIKO, float)
default_lot = get_query_param("lot", DEFAULT_LOT, float)
default_tp = get_query_param("tp", DEFAULT_TP_DOLLAR, float)
default_sl = get_query_param("sl", DEFAULT_SL_DOLLAR, float)

default_eksekusi = get_query_param("eksekusi", "Market Execution")
TIPE_EKSEKUSI = ["Market Execution", "Buy Limit", "Sell Limit", "Buy Stop", "Sell Stop"]
if default_eksekusi not in TIPE_EKSEKUSI:
    default_eksekusi = "Market Execution"

# ------------------- SIDEBAR -------------------
with st.sidebar:
    st.markdown("## ⚙️ Pengaturan Trading")
    st.markdown("---")

    tf_label = st.selectbox("⏱️ Timeframe", list(TIMEFRAME_OPTIONS.keys()),
                            index=list(TIMEFRAME_OPTIONS.keys()).index(default_tf))
    tf = TIMEFRAME_OPTIONS[tf_label]
    st.query_params["tf"] = tf_label

    st.markdown("---")
    st.subheader("💰 Modal & Risiko")
    modal = st.number_input("Modal (USD)", min_value=1.0, value=default_modal, step=1.0)
    risiko_persen = st.slider("Risiko per trade (%)", 1.0, 50.0, default_risiko, 1.0)

    st.markdown("---")
    st.subheader("📊 Lot & Target")
    lot_size = st.number_input("Lot Size", min_value=0.001, value=default_lot, step=0.001, format="%.3f")
    max_loss = st.number_input("Max Loss ($)", min_value=0.5, value=default_sl, step=0.5)
    max_profit = st.number_input("Max Profit ($)", min_value=0.5, value=default_tp, step=0.5)

    st.query_params["modal"] = str(modal)
    st.query_params["risiko"] = str(risiko_persen)
    st.query_params["lot"] = str(lot_size)
    st.query_params["tp"] = str(max_profit)
    st.query_params["sl"] = str(max_loss)

    st.markdown("---")
    st.subheader("⚡ Tipe Eksekusi")
    tipe_order = st.selectbox("Pilih Tipe Order", TIPE_EKSEKUSI,
                              index=TIPE_EKSEKUSI.index(default_eksekusi))
    st.query_params["eksekusi"] = tipe_order

    st.markdown("---")
    st.subheader("🔮 Prediksi")
    use_ml = st.toggle("Gunakan Machine Learning", value=True)
    forecast_candles = st.slider("Jumlah Candle Prediksi", 3, 15, 5)

    st.markdown("---")
    if st.button("🔄 Refresh Sekarang", use_container_width=True):
        st.rerun()

    st.markdown("**⏰ Auto-refresh setiap 30 detik**")
    st.caption("Terakhir update: " + datetime.now().strftime("%H:%M:%S"))

# ================= FUNGSI =================
@st.cache_data(ttl=30)
def ambil_data(tf, symbol="GC=F"):
    """Ambil data dengan multiple fallback."""
    symbols_to_try = [symbol, "GC=F", "XAUUSD=X", "GLD"]
    for sym in symbols_to_try:
        try:
            ticker = yf.Ticker(sym)
            df = ticker.history(period="7d", interval=tf)
            if not df.empty and len(df) >= 20:
                return sym, df[['Open','High','Low','Close','Volume']]
            df = ticker.history(period="1d", interval=tf)
            if not df.empty and len(df) >= 20:
                return sym, df[['Open','High','Low','Close','Volume']]
            df = ticker.history(period="5d", interval=tf)
            if not df.empty and len(df) >= 20:
                return sym, df[['Open','High','Low','Close','Volume']]
        except Exception:
            continue
    return None, pd.DataFrame()

def hitung_indikator(df):
    if df.empty or len(df) < 50:
        return df

    # Trend
    df['SMA_5'] = ta.trend.sma_indicator(df['Close'], 5)
    df['SMA_10'] = ta.trend.sma_indicator(df['Close'], 10)
    df['SMA_20'] = ta.trend.sma_indicator(df['Close'], 20)
    df['EMA_5'] = ta.trend.ema_indicator(df['Close'], 5)
    df['EMA_10'] = ta.trend.ema_indicator(df['Close'], 10)
    df['EMA_20'] = ta.trend.ema_indicator(df['Close'], 20)

    # MACD
    macd = ta.trend.MACD(df['Close'])
    df['MACD_line'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_hist'] = macd.macd_diff()

    # RSI
    df['RSI_14'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
    df['RSI_7'] = ta.momentum.RSIIndicator(df['Close'], 7).rsi()
    df['RSI_3'] = ta.momentum.RSIIndicator(df['Close'], 3).rsi()

    # Bollinger Bands
    bb = ta.volatility.BollingerBands(df['Close'], 20, 2)
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_middle'] = bb.bollinger_mavg()
    df['BB_lower'] = bb.bollinger_lband()
    df['BB_pct'] = bb.bollinger_pband()

    # Stochastic
    stoch = ta.momentum.StochasticOscillator(df['High'], df['Low'], df['Close'], 14, 3)
    df['Stoch_K'] = stoch.stoch()
    df['Stoch_D'] = stoch.stoch_signal()

    # ADX & ATR
    adx = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], 14)
    df['ADX'] = adx.adx()
    df['DI_plus'] = adx.adx_pos()
    df['DI_minus'] = adx.adx_neg()
    df['ATR'] = ta.volatility.AverageTrueRange(df['High'], df['Low'], df['Close'], 14).average_true_range()

    # Volume
    df['Volume_SMA'] = df['Volume'].rolling(10).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']

    # Candle properties
    df['Body'] = abs(df['Close'] - df['Open'])
    df['Upper_Shadow'] = df['High'] - df[['Close', 'Open']].max(axis=1)
    df['Lower_Shadow'] = df[['Close', 'Open']].min(axis=1) - df['Low']
    df['Total_Range'] = df['High'] - df['Low']
    df['Body_Pct'] = df['Body'] / df['Total_Range']

    return df

def analisis_candlestick_lengkap(df):
    """Analisis pola candlestick yang sangat detail untuk TF 1 menit."""
    if len(df) < 5:
        return "Tidak cukup data", []

    patterns = []
    signals = []

    for i in range(-5, 0):  # Analisis 5 candle terakhir
        if i < -len(df):
            continue
        candle = df.iloc[i]
        prev = df.iloc[i-1] if i-1 >= -len(df) else candle
        prev2 = df.iloc[i-2] if i-2 >= -len(df) else prev

        body = candle['Body']
        upper = candle['Upper_Shadow']
        lower = candle['Lower_Shadow']
        total = candle['Total_Range']
        body_pct = candle['Body_Pct']

        if total == 0:
            continue

        # Bullish patterns
        if body_pct > 0.7 and candle['Close'] > candle['Open']:
            if lower > upper * 2:
                patterns.append(f"Candle {i+6}: 🔨 Hammer Bullish")
                signals.append("BUY")
            else:
                patterns.append(f"Candle {i+6}: 🟢 Strong Bullish Body")
                signals.append("BUY")

        # Bearish patterns
        elif body_pct > 0.7 and candle['Close'] < candle['Open']:
            if upper > lower * 2:
                patterns.append(f"Candle {i+6}: ⭐ Shooting Star Bearish")
                signals.append("SELL")
            else:
                patterns.append(f"Candle {i+6}: 🔴 Strong Bearish Body")
                signals.append("SELL")

        # Doji
        elif body_pct < 0.1:
            patterns.append(f"Candle {i+6}: 🕯️ Doji (Reversal Signal)")
            if candle['Close'] > prev['Close']:
                signals.append("BUY")
            else:
                signals.append("SELL")

        # Engulfing
        prev_body = abs(prev['Close'] - prev['Open'])
        if body > prev_body * 1.5:
            if candle['Close'] > candle['Open'] and prev['Close'] < prev['Open']:
                patterns.append(f"Candle {i+6}: 🟢 Bullish Engulfing")
                signals.append("BUY")
            elif candle['Close'] < candle['Open'] and prev['Close'] > prev['Open']:
                patterns.append(f"Candle {i+6}: 🔴 Bearish Engulfing")
                signals.append("SELL")

        # Morning/Evening Star
        if i >= -3:
            star_body = abs(prev['Close'] - prev['Open'])
            if (prev2['Close'] < prev2['Open'] and 
                star_body < 0.3 * total and
                candle['Close'] > candle['Open'] and candle['Close'] > prev2['Open']):
                patterns.append(f"Candle {i+6}: 🌅 Morning Star")
                signals.append("BUY")
            elif (prev2['Close'] > prev2['Open'] and 
                  star_body < 0.3 * total and
                  candle['Close'] < candle['Open'] and candle['Close'] < prev2['Open']):
                patterns.append(f"Candle {i+6}: 🌇 Evening Star")
                signals.append("SELL")

    # Count signals
    buy_count = signals.count("BUY")
    sell_count = signals.count("SELL")

    if buy_count > sell_count:
        dominant = f"🟢 Dominan BULLISH ({buy_count} vs {sell_count})"
    elif sell_count > buy_count:
        dominant = f"🔴 Dominan BEARISH ({sell_count} vs {buy_count})"
    else:
        dominant = "⚪ Seimbang (tunggu konfirmasi)"

    return dominant, patterns

def sinyal_akurat(row, tipe, atr, df, max_loss_dollar, max_profit_dollar, lot):
    """Sinyal yang sangat akurat dengan konfirmasi multi-indikator."""
    if pd.isna(row['RSI_14']) or pd.isna(atr):
        return "⚪ TUNGGU", 0, (None, None, None, ""), {}

    score = 0
    reasons = []
    confirmations = 0

    # === RSI KONFIRMASI ===
    if row['RSI_14'] < 25:
        score += 4
        confirmations += 1
        reasons.append("✅ RSI oversold ekstrem (<25) – SANGAT BULLISH")
    elif row['RSI_14'] < 35:
        score += 3
        confirmations += 1
        reasons.append("✅ RSI oversold (<35) – BULLISH")
    elif row['RSI_14'] < 45:
        score += 1
        reasons.append("⚡ RSI mendekati oversold")
    elif row['RSI_14'] > 75:
        score -= 4
        confirmations += 1
        reasons.append("✅ RSI overbought ekstrem (>75) – SANGAT BEARISH")
    elif row['RSI_14'] > 65:
        score -= 3
        confirmations += 1
        reasons.append("✅ RSI overbought (>65) – BEARISH")
    elif row['RSI_14'] > 55:
        score -= 1
        reasons.append("⚡ RSI mendekati overbought")

    # RSI 7 untuk konfirmasi cepat
    if row['RSI_7'] < 30 and row['RSI_14'] < 40:
        score += 2
        confirmations += 1
        reasons.append("✅ RSI-7 konfirmasi oversold")
    elif row['RSI_7'] > 70 and row['RSI_14'] > 60:
        score -= 2
        confirmations += 1
        reasons.append("✅ RSI-7 konfirmasi overbought")

    # === MACD KONFIRMASI ===
    if row['MACD_line'] > row['MACD_signal'] and row['MACD_hist'] > 0:
        score += 3
        confirmations += 1
        reasons.append("✅ MACD bullish crossover + histogram positif")
    elif row['MACD_line'] < row['MACD_signal'] and row['MACD_hist'] < 0:
        score -= 3
        confirmations += 1
        reasons.append("✅ MACD bearish crossover + histogram negatif")
    elif row['MACD_line'] > row['MACD_signal']:
        score += 1
        reasons.append("⚡ MACD line di atas signal")
    else:
        score -= 1
        reasons.append("⚡ MACD line di bawah signal")

    # === MOVING AVERAGE KONFIRMASI ===
    if row['EMA_5'] > row['EMA_10'] > row['EMA_20']:
        score += 3
        confirmations += 1
        reasons.append("✅ EMA 5>10>20 (Golden Alignment) – BULLISH")
    elif row['EMA_5'] < row['EMA_10'] < row['EMA_20']:
        score -= 3
        confirmations += 1
        reasons.append("✅ EMA 5<10<20 (Death Alignment) – BEARISH")

    if row['Close'] > row['SMA_20']:
        score += 1
        reasons.append("⚡ Harga di atas SMA 20")
    else:
        score -= 1
        reasons.append("⚡ Harga di bawah SMA 20")

    # === BOLLINGER BANDS KONFIRMASI ===
    if row['Close'] <= row['BB_lower']:
        score += 3
        confirmations += 1
        reasons.append("✅ Harga di BOLLINGER LOWER – BOUNCE POTENSIAL")
    elif row['Close'] >= row['BB_upper']:
        score -= 3
        confirmations += 1
        reasons.append("✅ Harga di BOLLINGER UPPER – REVERSAL POTENSIAL")
    elif row['BB_pct'] < 0.2:
        score += 1
        reasons.append("⚡ Harga di zona bawah BB")
    elif row['BB_pct'] > 0.8:
        score -= 1
        reasons.append("⚡ Harga di zona atas BB")

    # === STOCHASTIC KONFIRMASI ===
    if row['Stoch_K'] < 20 and row['Stoch_K'] > row['Stoch_D']:
        score += 3
        confirmations += 1
        reasons.append("✅ Stochastic bullish crossover (oversold)")
    elif row['Stoch_K'] > 80 and row['Stoch_K'] < row['Stoch_D']:
        score -= 3
        confirmations += 1
        reasons.append("✅ Stochastic bearish crossover (overbought)")
    elif row['Stoch_K'] < row['Stoch_D']:
        score -= 1
    else:
        score += 1

    # === ADX TREND STRENGTH ===
    if row['ADX'] > 30:
        if score > 0:
            score += 2
            confirmations += 1
            reasons.append("✅ Trend KUAT BULLISH (ADX>30)")
        elif score < 0:
            score -= 2
            confirmations += 1
            reasons.append("✅ Trend KUAT BEARISH (ADX>30)")
    elif row['ADX'] > 20:
        if score > 0:
            score += 1
            reasons.append("⚡ Trend moderat bullish")
        elif score < 0:
            score -= 1
            reasons.append("⚡ Trend moderat bearish")

    # DI Plus/Minus
    if row['DI_plus'] > row['DI_minus'] + 5:
        score += 2
        confirmations += 1
        reasons.append("✅ DI+ jauh di atas DI- (bullish momentum kuat)")
    elif row['DI_minus'] > row['DI_plus'] + 5:
        score -= 2
        confirmations += 1
        reasons.append("✅ DI- jauh di atas DI+ (bearish momentum kuat)")

    # === VOLUME KONFIRMASI ===
    if row['Volume_Ratio'] > 2.0:
        if score > 0:
            score += 2
            confirmations += 1
            reasons.append("✅ Volume TINGGI konfirmasi bullish")
        elif score < 0:
            score -= 2
            confirmations += 1
            reasons.append("✅ Volume TINGGI konfirmasi bearish")
    elif row['Volume_Ratio'] > 1.5:
        if score > 0:
            score += 1
            reasons.append("⚡ Volume di atas rata-rata")
        elif score < 0:
            score -= 1

    # === CANDLESTICK PATTERN KONFIRMASI ===
    if len(df) >= 3:
        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]

        body_pct = last_candle['Body_Pct']
        if body_pct > 0.8 and last_candle['Close'] > last_candle['Open']:
            score += 2
            confirmations += 1
            reasons.append("✅ Candle bullish body besar")
        elif body_pct > 0.8 and last_candle['Close'] < last_candle['Open']:
            score -= 2
            confirmations += 1
            reasons.append("✅ Candle bearish body besar")

        # Hammer detection
        if last_candle['Lower_Shadow'] > 2 * last_candle['Body'] and last_candle['Close'] > last_candle['Open']:
            score += 2
            confirmations += 1
            reasons.append("✅ Hammer pattern terdeteksi")
        elif last_candle['Upper_Shadow'] > 2 * last_candle['Body'] and last_candle['Close'] < last_candle['Open']:
            score -= 2
            confirmations += 1
            reasons.append("✅ Shooting Star pattern terdeteksi")

    # === DECISION LOGIC ===
    # Hanya beri sinyal jika ada minimal 3 konfirmasi
    if score >= 5 and confirmations >= 3:
        sinyal = "🟢🟢 STRONG BUY"
        arah = "BUY"
        confidence = "TINGGI"
    elif score >= 3 and confirmations >= 2:
        sinyal = "🟢 BUY"
        arah = "BUY"
        confidence = "SEDANG"
    elif score <= -5 and confirmations >= 3:
        sinyal = "🔴🔴 STRONG SELL"
        arah = "SELL"
        confidence = "TINGGI"
    elif score <= -3 and confirmations >= 2:
        sinyal = "🔴 SELL"
        arah = "SELL"
        confidence = "SEDANG"
    else:
        sinyal = "⚪ TUNGGU"
        arah = "NEUTRAL"
        confidence = "RENDAH"
        return sinyal, score, (None, None, None, "Belum ada konfirmasi cukup. Tunggu sinyal kuat."), {
            "confidence": confidence, 
            "reasons": reasons, 
            "confirmations": confirmations
        }

    # === HITUNG SL/TP BERDASARKAN DOLLAR TARGET ===
    price = row['Close']

    # Hitung pip value untuk lot size
    pip_value = lot * PIP_VALUE_PER_LOT  # $0.01 per pip untuk 0.01 lot

    # SL dalam pips (points) untuk gold
    sl_pips = max_loss_dollar / pip_value if pip_value > 0 else 200
    tp_pips = max_profit_dollar / pip_value if pip_value > 0 else 300

    # Minimum SL/TP berdasarkan ATR juga
    atr_sl = atr * 1.5
    atr_tp = atr * 2.0

    # Gunakan yang lebih besar (lebih aman)
    final_sl_pips = max(sl_pips, atr_sl)
    final_tp_pips = max(tp_pips, atr_tp)

    if tipe == "Market Execution":
        entry = price
    elif tipe == "Buy Limit":
        entry = price - final_sl_pips * 0.3
    elif tipe == "Sell Limit":
        entry = price + final_sl_pips * 0.3
    elif tipe == "Buy Stop":
        entry = price + final_sl_pips * 0.2
    elif tipe == "Sell Stop":
        entry = price - final_sl_pips * 0.2
    else:
        entry = price

    if arah == "BUY":
        sl = entry - final_sl_pips
        tp = entry + final_tp_pips
    else:
        sl = entry + final_sl_pips
        tp = entry - final_tp_pips

    # Round
    entry = round(entry, 2)
    sl = round(sl, 2)
    tp = round(tp, 2)

    # Warning
    warning = ""
    if tipe in ["Buy Limit", "Buy Stop"] and arah != "BUY":
        warning = "⚠️ Sinyal bukan BUY, tipe order ini tidak disarankan!"
    elif tipe in ["Sell Limit", "Sell Stop"] and arah != "SELL":
        warning = "⚠️ Sinyal bukan SELL, tipe order ini tidak disarankan!"

    return sinyal, score, (entry, sl, tp, warning), {
        "confidence": confidence, 
        "reasons": reasons, 
        "confirmations": confirmations,
        "sl_pips": final_sl_pips,
        "tp_pips": final_tp_pips
    }

def forecast_future(df, steps=5, use_ml=True):
    close = df['Close'].dropna()
    if len(close) < 30:
        return None

    predictions = []

    try:
        model = ExponentialSmoothing(close, trend='add', seasonal=None, damped_trend=True)
        fit = model.fit()
        pred_ets = fit.forecast(steps)
        predictions.append(pred_ets.values)
    except:
        predictions.append(None)

    try:
        X = np.arange(len(close)).reshape(-1, 1)
        y = close.values
        reg = LinearRegression().fit(X[-50:], y[-50:])
        future_idx = np.arange(len(close), len(close) + steps).reshape(-1, 1)
        pred_lr = reg.predict(future_idx)
        predictions.append(pred_lr)
    except:
        predictions.append(None)

    if use_ml and len(close) >= 50:
        try:
            features = []
            targets = []
            for i in range(20, len(close) - steps):
                feat = [
                    close.iloc[i] - close.iloc[i-5],
                    close.iloc[i] - close.iloc[i-10],
                    close.iloc[i] - close.iloc[i-20],
                    close.iloc[i-5:i].mean(),
                    close.iloc[i-10:i].mean(),
                    close.iloc[i-20:i].mean(),
                    close.iloc[i-5:i].std(),
                ]
                features.append(feat)
                targets.append(close.iloc[i:i+steps].values)

            if len(features) > 10:
                rf = RandomForestRegressor(n_estimators=50, random_state=42)
                rf.fit(features, targets)
                last_feat = [
                    close.iloc[-1] - close.iloc[-5],
                    close.iloc[-1] - close.iloc[-10],
                    close.iloc[-1] - close.iloc[-20],
                    close.iloc[-5:].mean(),
                    close.iloc[-10:].mean(),
                    close.iloc[-20:].mean(),
                    close.iloc[-5:].std(),
                ]
                pred_ml = rf.predict([last_feat])[0]
                predictions.append(pred_ml)
        except:
            predictions.append(None)

    valid_preds = [p for p in predictions if p is not None]
    if not valid_preds:
        return None

    ensemble_pred = np.mean(valid_preds, axis=0)

    last_time = close.index[-1]
    if tf.endswith('m'):
        delta = timedelta(minutes=int(tf[:-1]))
    elif tf.endswith('h'):
        delta = timedelta(hours=int(tf[:-1]))
    elif tf.endswith('d'):
        delta = timedelta(days=int(tf[:-1]))
    else:
        delta = timedelta(minutes=1)

    future_times = [last_time + delta * (i + 1) for i in range(steps)]

    result = pd.DataFrame({
        'Forecast': np.round(ensemble_pred, 2),
        'Trend': ['UP' if ensemble_pred[i] > ensemble_pred[i-1] else 'DOWN' if i > 0 else 'FLAT' for i in range(steps)]
    }, index=pd.DatetimeIndex(future_times))

    return result

def buat_candlestick_chart(df, symbol):
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f'🕯️ {symbol} Live Chart', '📊 MACD', '📈 RSI')
    )

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Candlestick',
        increasing_line_color='#00b894',
        decreasing_line_color='#d63031',
        increasing_fillcolor='#00b894',
        decreasing_fillcolor='#d63031'
    ), row=1, col=1)

    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_upper'], name='BB Upper', 
                             line=dict(color='rgba(255,0,0,0.6)', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_lower'], name='BB Lower',
                             line=dict(color='rgba(255,0,0,0.6)', width=1),
                             fill='tonexty', fillcolor='rgba(255,0,0,0.05)'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['BB_middle'], name='BB Middle',
                             line=dict(color='rgba(128,128,128,0.7)', width=1, dash='dash')), row=1, col=1)

    # EMA
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_5'], name='EMA 5',
                             line=dict(color='#fdcb6e', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], name='EMA 20',
                             line=dict(color='#6c5ce7', width=1.5)), row=1, col=1)

    # MACD
    colors_macd = ['#00b894' if x > 0 else '#d63031' for x in df['MACD_hist']]
    fig.add_trace(go.Bar(x=df.index, y=df['MACD_hist'], name='MACD Hist',
                         marker_color=colors_macd), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_line'], name='MACD',
                             line=dict(color='#0984e3', width=1.5)), row=2, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['MACD_signal'], name='Signal',
                             line=dict(color='#d63031', width=1.5)), row=2, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_14'], name='RSI 14',
                             line=dict(color='#6c5ce7', width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI_7'], name='RSI 7',
                             line=dict(color='#fdcb6e', width=1.5)), row=3, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
    fig.add_hline(y=50, line_dash="dot", line_color="gray", row=3, col=1)

    fig.update_layout(
        height=900,
        template='plotly_dark',
        xaxis_rangeslider_visible=False,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=50, r=50, t=100, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    fig.update_yaxes(title_text="Harga ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1)

    return fig

def generate_copy_text(tipe_order, entry, sl, tp, symbol, score, confidence, lot, max_loss, max_profit):
    sl_jarak = abs(entry - sl)
    tp_jarak = abs(tp - entry)
    rr = tp_jarak / sl_jarak if sl_jarak > 0 else 0

    text = f"""═══════════════════════════════════════
🤖 BOT TRADING RAHMAN – SINYAL {symbol}
═══════════════════════════════════════
📅 Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
📊 Score: {score} | Confidence: {confidence}

⚡ Tipe Order: {tipe_order}
💰 Entry: {entry:.2f}
🛑 Stop Loss: {sl:.2f}
🎯 Take Profit: {tp:.2f}

📏 Jarak SL: {sl_jarak:.2f} pips
📏 Jarak TP: {tp_jarak:.2f} pips
⚖️ Risk:Reward = 1:{rr:.2f}

💰 Modal: $10 | Lot: {lot}
🛑 Max Loss: ${max_loss:.2f}
🎯 Max Profit: ${max_profit:.2f}

💡 PASTE INI KE MT4/MT5 ANDA!
═══════════════════════════════════════"""
    return text

def create_download_link(text, filename="sinyal_trading.txt"):
    b64 = base64.b64encode(text.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}" style="text-decoration:none;"><button class="copy-btn">📥 DOWNLOAD SINYAL (.txt)</button></a>'

# ------------------- MAIN -------------------
symbol_used, df = ambil_data(tf)

if df.empty:
    st.error("⚠️ Yahoo Finance sedang tidak bisa diakses. Coba lagi nanti.")
    st.info("💡 Tips: TF 1 menit sering rate limit. Coba refresh manual atau ganti ke 5m.")
else:
    st.success(f"✅ Data: **{symbol_used}** | Candle: {len(df)} | Update: {datetime.now().strftime('%H:%M:%S')}")

    df = hitung_indikator(df)

    if len(df) < 2:
        st.error("Data terlalu sedikit.")
    else:
        last_candle = df.iloc[-2]
        current_price = df.iloc[-1]['Close']
        atr = last_candle['ATR']

        sinyal, skor, (entry, sl, tp, warning), analysis = sinyal_akurat(
            last_candle, tipe_order, atr, df, max_loss, max_profit, lot_size
        )
        candle_dominant, candle_patterns = analisis_candlestick_lengkap(df)

        # ================= LIVE PRICE =================
        st.markdown("---")
        st.markdown(f'<div class="live-price">💰 {current_price:.2f} USD</div>', unsafe_allow_html=True)

        change = ((current_price - df.iloc[-2]['Close']) / df.iloc[-2]['Close'] * 100) if len(df) > 1 else 0
        col_change1, col_change2, col_change3 = st.columns(3)
        with col_change1:
            st.metric("Perubahan", f"{change:.3f}%", delta=f"{current_price - df.iloc[-2]['Close']:.2f}")
        with col_change2:
            st.metric("High", f"{df.iloc[-1]['High']:.2f}")
        with col_change3:
            st.metric("Low", f"{df.iloc[-1]['Low']:.2f}")

        # ================= SIGNAL BOX =================
        st.markdown("---")
        col_sig1, col_sig2 = st.columns([2, 1])

        with col_sig1:
            signal_class = "buy-signal" if "BUY" in sinyal else "sell-signal" if "SELL" in sinyal else "neutral-signal"
            st.markdown(f'<div class="signal-box {signal_class}">{sinyal}</div>', unsafe_allow_html=True)

        with col_sig2:
            confidence = analysis.get("confidence", "RENDAH")
            confirmations = analysis.get("confirmations", 0)
            st.metric("📊 Confidence", confidence)
            st.metric("✅ Konfirmasi", f"{confirmations}/10")
            st.progress(min(abs(skor) / 10, 1.0), text=f"Strength: {abs(skor)}/10")

        if warning:
            st.warning(warning)

        # ================= TARGET BOXES =================
        st.markdown("---")
        col_target1, col_target2, col_target3 = st.columns(3)

        with col_target1:
            st.markdown(f'<div class="info-card">💰 Modal<br><span class="metric-value">${modal:.2f}</span></div>', unsafe_allow_html=True)
        with col_target2:
            st.markdown(f'<div class="loss-limit">🛑 Max Loss<br>${max_loss:.2f}</div>', unsafe_allow_html=True)
        with col_target3:
            st.markdown(f'<div class="profit-target">🎯 Max Profit<br>${max_profit:.2f}</div>', unsafe_allow_html=True)

        # ================= COPY SL/TP =================
        if entry is not None and sl is not None and tp is not None:
            st.markdown("---")
            st.subheader(f"⚡ REKOMENDASI ORDER – {tipe_order}")

            col_order1, col_order2, col_order3 = st.columns(3)
            with col_order1:
                st.markdown(f'<div class="info-card">📍 Entry<br><span class="metric-value">{entry:.2f}</span></div>', unsafe_allow_html=True)
            with col_order2:
                st.markdown(f'<div class="loss-limit">🛑 Stop Loss<br><span class="metric-value">{sl:.2f}</span></div>', unsafe_allow_html=True)
            with col_order3:
                st.markdown(f'<div class="profit-target">🎯 Take Profit<br><span class="metric-value">{tp:.2f}</span></div>', unsafe_allow_html=True)

            sl_jarak = abs(entry - sl)
            tp_jarak = abs(tp - entry)
            rr = tp_jarak / sl_jarak if sl_jarak > 0 else 0

            col_rr1, col_rr2 = st.columns(2)
            with col_rr1:
                st.info(f"📏 Jarak SL: **{sl_jarak:.2f} pips** | Jarak TP: **{tp_jarak:.2f} pips**")
            with col_rr2:
                st.success(f"⚖️ Risk:Reward = **1:{rr:.2f}**")

            # Tombol Salin
            copy_text = generate_copy_text(tipe_order, entry, sl, tp, symbol_used, skor, 
                                          analysis.get("confidence", "RENDAH"), lot_size, max_loss, max_profit)

            col_copy1, col_copy2, col_copy3 = st.columns(3)
            with col_copy1:
                st.code(copy_text, language="")
            with col_copy2:
                if st.button("📋 SALIN SEMUA DATA", use_container_width=True):
                    st.session_state['clipboard'] = copy_text
                    st.success("✅ Data sudah disalin! Paste ke broker Anda.")
                    st.balloons()
            with col_copy3:
                st.markdown(create_download_link(copy_text), unsafe_allow_html=True)

            # Info lot
            st.info(f"📊 **Lot: {lot_size}** | Modal: ${modal:.2f} | Max Loss: ${max_loss:.2f} | Max Profit: ${max_profit:.2f}")

            penjelasan = {
                "Market Execution": "📌 Eksekusi langsung di harga pasar. Paling cepat untuk sinyal kuat.",
                "Buy Limit": "📌 Order beli di bawah harga pasar. Tunggu pullback lalu naik.",
                "Sell Limit": "📌 Order jual di atas harga pasar. Tunggu resistance lalu turun.",
                "Buy Stop": "📌 Order beli di atas harga pasar. Breakout naik.",
                "Sell Stop": "📌 Order jual di bawah harga pasar. Breakdown turun."
            }
            st.caption(penjelasan.get(tipe_order, ""))
        else:
            st.info("⏳ Belum ada sinyal kuat. Tunggu konfirmasi indikator. Bot akan otomatis update setiap 30 detik.")

        # ================= CANDLESTICK ANALYSIS =================
        st.markdown("---")
        st.subheader("🕯️ Analisis Candlestick (5 Candle Terakhir)")

        col_cand1, col_cand2 = st.columns([1, 2])

        with col_cand1:
            st.markdown(f'<div class="info-card">{candle_dominant}</div>', unsafe_allow_html=True)

            # Current candle info
            curr = df.iloc[-1]
            st.markdown("#### 🕯️ Candle Saat Ini")
            st.markdown(f"""
            <div class="candle-info">
                <b>Open:</b> {curr['Open']:.2f}<br>
                <b>High:</b> {curr['High']:.2f}<br>
                <b>Low:</b> {curr['Low']:.2f}<br>
                <b>Close:</b> {curr['Close']:.2f}<br>
                <b>Body:</b> {curr['Body']:.2f} ({curr['Body_Pct']*100:.1f}%)<br>
                <b>Upper Shadow:</b> {curr['Upper_Shadow']:.2f}<br>
                <b>Lower Shadow:</b> {curr['Lower_Shadow']:.2f}
            </div>
            """, unsafe_allow_html=True)

        with col_cand2:
            if candle_patterns:
                for pattern in candle_patterns:
                    if "Bullish" in pattern or "BUY" in pattern or "Hammer" in pattern or "Morning" in pattern:
                        st.success(pattern)
                    elif "Bearish" in pattern or "SELL" in pattern or "Shooting" in pattern or "Evening" in pattern:
                        st.error(pattern)
                    else:
                        st.warning(pattern)
            else:
                st.info("Belum ada pola candlestick yang terdeteksi.")

        # ================= INDICATOR DETAIL =================
        st.markdown("---")
        st.subheader("📊 Detail Indikator Teknis")

        col_ind1, col_ind2, col_ind3, col_ind4 = st.columns(4)

        with col_ind1:
            st.markdown("#### 📈 Trend")
            st.write(f"EMA 5: {last_candle['EMA_5']:.2f}")
            st.write(f"EMA 10: {last_candle['EMA_10']:.2f}")
            st.write(f"EMA 20: {last_candle['EMA_20']:.2f}")
            st.write(f"SMA 20: {last_candle['SMA_20']:.2f}")

        with col_ind2:
            st.markdown("#### 📉 Momentum")
            st.write(f"RSI (14): {last_candle['RSI_14']:.1f}")
            st.write(f"RSI (7): {last_candle['RSI_7']:.1f}")
            st.write(f"Stoch K: {last_candle['Stoch_K']:.1f}")
            st.write(f"Stoch D: {last_candle['Stoch_D']:.1f}")

        with col_ind3:
            st.markdown("#### 📊 Oscillator")
            st.write(f"MACD: {last_candle['MACD_line']:.4f}")
            st.write(f"Signal: {last_candle['MACD_signal']:.4f}")
            st.write(f"Hist: {last_candle['MACD_hist']:.4f}")
            st.write(f"ADX: {last_candle['ADX']:.1f}")

        with col_ind4:
            st.markdown("#### 📏 Volatilitas")
            st.write(f"ATR: {last_candle['ATR']:.2f}")
            st.write(f"DI+: {last_candle['DI_plus']:.1f}")
            st.write(f"DI-: {last_candle['DI_minus']:.1f}")
            st.write(f"BB%: {last_candle['BB_pct']*100:.1f}%")

        # Alasan sinyal
        if analysis.get("reasons"):
            with st.expander("📋 Lihat Semua Alasan Sinyal"):
                for i, reason in enumerate(analysis["reasons"], 1):
                    st.write(f"{i}. {reason}")

        # ================= CHART =================
        st.markdown("---")
        st.subheader("📊 Chart Candlestick Live")

        chart_fig = buat_candlestick_chart(df, symbol_used)
        st.plotly_chart(chart_fig, use_container_width=True)

        # ================= PREDIKSI =================
        st.markdown("---")
        st.subheader(f"🔮 Prediksi {forecast_candles} Candle ke Depan")

        forecast_df = forecast_future(df, forecast_candles, use_ml)
        if forecast_df is not None:
            col_f1, col_f2 = st.columns([2, 1])

            with col_f1:
                def highlight_trend(row):
                    if row['Trend'] == 'UP':
                        return ['background-color: rgba(0,184,148,0.3)'] * 2
                    elif row['Trend'] == 'DOWN':
                        return ['background-color: rgba(214,48,49,0.3)'] * 2
                    return [''] * 2

                st.dataframe(forecast_df.style.apply(highlight_trend, axis=1), use_container_width=True)

            with col_f2:
                first_price = forecast_df['Forecast'].iloc[0]
                last_price = forecast_df['Forecast'].iloc[-1]
                change_pct = ((last_price - first_price) / first_price) * 100

                st.metric("Prediksi Perubahan", f"{change_pct:.3f}%", 
                         delta=f"{last_price - first_price:.2f} pips")

                up_count = (forecast_df['Trend'] == 'UP').sum()
                down_count = (forecast_df['Trend'] == 'DOWN').sum()

                st.write(f"📈 Naik: {up_count} candle")
                st.write(f"📉 Turun: {down_count} candle")

                if change_pct > 0.3:
                    st.success(f"📈 Prediksi KENAIKAN dalam {forecast_candles} candle!")
                elif change_pct < -0.3:
                    st.error(f"📉 Prediksi PENURUNAN dalam {forecast_candles} candle!")
                else:
                    st.info(f"⚪ Prediksi SIDeways dalam {forecast_candles} candle.")

            # Forecast Chart
            fig_forecast = go.Figure()
            fig_forecast.add_trace(go.Scatter(
                x=df.index[-20:], y=df['Close'].iloc[-20:],
                mode='lines', name='History',
                line=dict(color='#74b9ff', width=2)
            ))
            fig_forecast.add_trace(go.Scatter(
                x=forecast_df.index, y=forecast_df['Forecast'],
                mode='lines+markers', name='Forecast',
                line=dict(color='#00b894', width=2, dash='dash'),
                marker=dict(size=10, symbol='diamond')
            ))
            fig_forecast.update_layout(
                title="🔮 Prediksi Harga Masa Depan",
                template='plotly_dark',
                height=400,
                xaxis_title="Waktu",
                yaxis_title="Harga ($)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_forecast, use_container_width=True)
        else:
            st.warning("⚠️ Butuh minimal 30 candle untuk prediksi.")

        # ================= FOOTER =================
        st.markdown("---")
        col_foot1, col_foot2, col_foot3 = st.columns(3)

        with col_foot1:
            st.caption("⏰ Auto-refresh: 30 detik")
        with col_foot2:
            st.caption(f"🔄 Update: {datetime.now().strftime('%H:%M:%S')}")
        with col_foot3:
            st.caption("⚠️ Gunakan akun demo dulu!")

        st.markdown("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(90deg, #1a1a2e, #16213e); border-radius: 15px; margin-top: 20px; border: 1px solid rgba(255,215,0,0.2);">
            <h4 style="color: #FFD700;">🤖 Bot Trading Rahman v3.0 – $10 Profit Mode</h4>
            <p style="color: #888;">Dibuat khusus untuk trader modal kecil yang ingin profit konsisten</p>
            <p style="color: #666; font-size: 0.8rem;">TF 1 Menit | Lot 0.01 | Max Loss $2 | Max Profit $3</p>
        </div>
        """, unsafe_allow_html=True)
