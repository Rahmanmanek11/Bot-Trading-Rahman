# 🤖 Bot Trading Rahman v3.0 – ULTIMATE $10 Profit Mode

Bot trading otomatis untuk XAU/USD (Gold) khusus untuk trader modal kecil.

## ⚡ Spesifikasi Khusus

| Setting | Nilai |
|---------|-------|
| **Modal** | $10 (default) |
| **Lot Size** | 0.01 (micro) |
| **Max Loss per Trade** | $2 |
| **Max Profit per Trade** | $3 |
| **Timeframe Default** | 1 Menit |
| **Auto-refresh** | 30 detik |

## ✨ Fitur Unggulan

- 🕯️ **Analisis Candlestick Real-Time** – Deteksi Hammer, Engulfing, Doji, Morning/Evening Star
- 📊 **Multi-Konfirmasi Sinyal** – Minimal 3 indikator harus konfirmasi sebelum beri sinyal
- 📋 **Tombol Salin + Download** – Copy paste SL/TP langsung ke MT4/MT5
- 🔮 **Prediksi ML** – Ensemble forecasting (ETS + Linear Reg + Random Forest)
- 📈 **Chart Interaktif** – Candlestick + Bollinger + EMA + MACD + RSI
- 💰 **Auto-Kalkulasi** – SL/TP otomatis berdasarkan $ target, bukan hanya ATR

## 🚀 Cara Deploy

### 1. Buat Repository GitHub
```bash
git init
git add .
git commit -m "Bot Trading Rahman v3.0"
git branch -M main
git remote add origin https://github.com/USERNAME/bot-trading-rahman.git
git push -u origin main
```

### 2. Deploy ke Streamlit Cloud
1. Buka [share.streamlit.io](https://share.streamlit.io)
2. Login dengan GitHub
3. New app → Pilih repository
4. File utama: `bot_trading_rahman_v3_ultimate.py`
5. Deploy!

## ⚠️ Penting!

- Data 1 menit dari Yahoo Finance **delay ~15 menit** dan sering **rate limit**
- Gunakan **akun demo** terlebih dahulu!
- Tidak ada jaminan profit 100% – ini hanya alat bantu analisis
- Trading forex/emas sangat berisiko

## 📝 Catatan Teknis

- PIP value untuk XAU/USD 0.01 lot = $0.01 per pip
- SL/TP dihitung berdasarkan target dollar ($2 loss / $3 profit)
- Konfirmasi minimal 3 indikator untuk sinyal valid
