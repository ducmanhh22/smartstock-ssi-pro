"""SmartStock Terminal • SSI-only read-only market data dashboard."""
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from demo import BASE, example_candles
from finance import analyze, describe, summarize
from ssi_data import fetch_ssi
from storage import load, save

st.set_page_config(
    page_title="SmartStock Terminal | SSI Market Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="auto",
)

# Appearance shared across all modes. Never embed tokens or other secrets in markup.
BG = "#080D17"
PANEL = "#111B2A"
ACCENT = "#16D9AD"
UP = "#16D9AD"
DOWN = "#FF627D"
TEXT = "#EDF5FF"
MUTED = "#8799B2"
GRID = "#233046"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { color-scheme: dark; }
html, body, [data-testid="stApp"], [data-testid="stMarkdownContainer"] {font-family: 'DM Sans',sans-serif;}
[data-testid="stAppViewContainer"] {background: radial-gradient(ellipse at 84% 0%, #12263b 0%, #080d17 42%); color:#eaf3ff;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stMainBlockContainer"], .block-container {max-width: 1600px; padding-top: 1.5rem; padding-bottom:3.4rem;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#101c2d 0%,#0b1422 100%);border-right:1px solid #273449;}
[data-testid="stSidebar"] .block-container {padding-top:1rem;}
[data-testid="stSidebar"] hr {border-color:#26364b;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {color:#9eafc3;}
*, *:before, *:after {box-sizing:border-box;}
html, body {max-width:100%;overflow-x:hidden;}
h1,h2,h3,h4 {font-family:'Space Grotesk',sans-serif; letter-spacing:-.03em;}
h1 {font-size:2.1rem!important;}
h2 {font-size:1.4rem!important;}
h3 {font-size:1.12rem!important;}
.stButton > button[kind="primary"] {background:linear-gradient(110deg,#16d9ad,#0db7c7);color:#052425;border:0;border-radius:11px;font-weight:800;box-shadow:0 8px 26px rgba(13,207,174,.17);}
.stButton > button[kind="primary"]:hover {background:linear-gradient(110deg,#36f3c5,#17d6e5);color:#031e22;}
.stButton button, .stDownloadButton button {border-radius:11px;border:1px solid #304057;min-height:43px;font-weight:700;}
.stButton button:hover, .stDownloadButton button:hover {border-color:#16d9ad;color:#16d9ad;}
[data-baseweb="select"] > div, [data-testid="stTextInput"] input {border-radius:10px!important;background:#111d2e!important;border-color:#324057!important;}
[data-testid="stRadio"] label, [data-testid="stCheckbox"] label {font-size:0.9rem;}
[data-testid="stTabs"] [data-baseweb="tab-list"] {gap:8px; border-bottom:1px solid #29374b;}
[data-testid="stTabs"] [data-baseweb="tab"] {font-weight:700; padding:14px 20px; border-radius:10px 10px 0 0;}
[data-testid="stTabs"] [aria-selected="true"] {color:#27edc1; background:#12362f;}
[data-testid="stDataFrame"], [data-testid="stPlotlyChart"] {border:1px solid #28364b;border-radius:15px;overflow:hidden;background:#101928;}
[data-testid="stMetric"] {background:#111b2b;border:1px solid #28384d;padding:17px;border-radius:13px;}
[data-testid="stMetricValue"] {color:#e9f6ff;}
[data-testid="stAlert"] {border-radius:12px;}
section[data-testid="stSidebar"] [data-testid="stSidebarContent"] {padding-top:1.1rem;}
.topline {display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:10px;}
.brand {font:700 21px 'Space Grotesk',sans-serif;letter-spacing:-1px;color:#e8f7ff;}
.brand .dot {display:inline-block;width:11px;height:11px;border-radius:4px;background:#16d9ad;transform:rotate(45deg);margin-right:9px;box-shadow:0 0 17px #18d8a95a;}
.brand b {color:#15e0b1;}
.brand-sub {color:#758ba5;font-size:10px;letter-spacing:2px;font-weight:800;margin:3px 0 25px 22px;}
.nav-caption {color:#627a96;font-size:10px;font-weight:800;letter-spacing:2px;margin:17px 0 9px;}
.hero {border:1px solid #2a4550;background:linear-gradient(110deg, #14283b 0%, #0e1b2b 62%, #0d352e 120%);padding:25px 28px;border-radius:19px;position:relative;overflow:hidden;margin:0 0 19px;}
.hero:before {content:'';width:350px;height:350px;border-radius:50%;position:absolute;right:-120px;top:-225px;border:45px solid #18d4af12;pointer-events:none;}
.hero:after {content:'';position:absolute;right:5%;bottom:-125px;width:240px;height:240px;border-radius:50%;background:#15c99d12;filter:blur(28px);pointer-events:none;}
.hero-eyebrow {font-size:11px;letter-spacing:2.1px;color:#19d5ae;font-weight:800;margin-bottom:11px;}
.hero-title {font:700 clamp(27px,3.2vw,42px) 'Space Grotesk',sans-serif;letter-spacing:-1.7px;color:#f2f8ff;margin-bottom:8px;}
.hero-copy {color:#a4b8cf;line-height:1.65;font-size:13px;margin:0;}
.hero-badge {display:inline-block;border:1px solid #1f705e;background:#16493b;color:#59f1ce;padding:6px 11px;border-radius:100px;font-size:11px;font-weight:800;letter-spacing:.5px;margin-top:14px;}
.hero-badge.demo {border-color:#85672c;background:#423216;color:#f8c764;}
.kicker {color:#7088a2;font-size:11px;font-weight:800;letter-spacing:1.8px;margin:21px 0 12px;}
.section-title {color:#eaf4ff;font:700 20px 'Space Grotesk',sans-serif;letter-spacing:-.5px; margin:20px 0 7px;}
.section-sub {color:#8297af;font-size:12px;margin:0 0 14px;line-height:1.55;}
.kpi-card {background:linear-gradient(155deg,#152235,#111b2a);border:1px solid #2a394d;border-radius:15px;padding:17px 18px;min-height:119px;position:relative;box-shadow:0 8px 30px #00000015;}
.kpi-card:before {content:'';position:absolute;left:16px;right:16px;top:0;height:2px;background:linear-gradient(90deg,#19dcad40,transparent);}
.kpi-label {font-size:11px;color:#849bb7;font-weight:700;letter-spacing:.5px;margin-bottom:12px;}
.kpi-value {font:700 clamp(20px,2.15vw,30px) 'Space Grotesk',sans-serif;letter-spacing:-.9px;color:#f0f8ff;overflow-wrap:anywhere;line-height:1.18;}
.kpi-foot {font-size:11px;color:#7e95aa;margin-top:8px;}
.kpi-positive {color:#2ce0ad;font-weight:700;}
.kpi-negative {color:#ff738b;font-weight:700;}
.panel {background:#111b2a;border:1px solid #2a394e;border-radius:15px;padding:19px 20px;margin:0 0 13px;}
.panel-title {font:700 14px 'Space Grotesk',sans-serif;color:#f2f8ff;margin-bottom:11px;}
.panel-text {color:#9bacbf;line-height:1.7;font-size:12px;}
.mini-row {display:flex;justify-content:space-between;gap:13px;border-bottom:1px solid #27374b;padding:11px 0;font-size:12px;}
.mini-row:last-child {border-bottom:0;}
.mini-row .a {color:#8296ad;} .mini-row .b {color:#d9e6f3;font-weight:700;}
.mode-ribbon {border:1px solid #394558;color:#a9b8c9;background:#151d2b;border-radius:10px;padding:10px 14px;font-size:12px;margin:0 0 15px;}
.mode-ribbon strong {color:#ddecf8;}
.mode-ribbon.demo {border-color:#6b542b;background:#342a1d;color:#eccb83;}
.insight {background:linear-gradient(120deg,#17362f,#132531);border:1px solid #285c50;border-radius:14px;padding:16px 18px;color:#d6f1e9;font-size:13px;line-height:1.65;}
.footer {border-top:1px solid #253448;padding:17px 0 7px;color:#677e99;font-size:11px;line-height:1.8;margin-top:34px;}
.empty {border:1px dashed #385066;background:#111c2b;text-align:center;border-radius:18px;padding:65px 20px;margin:30px 0;color:#a1b8ce;}
.empty h3 {color:#e1f5fd;margin-bottom:7px;}
/* Flexible market app layout: 4 cards desktop, 2 tablet/mobile, 1 very small phones. */
.kpi-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:12px 0 6px;}
.toolbar-note {color:#8299b2;font-size:11px;margin:-5px 0 14px;line-height:1.5;}
.ticker-track {display:flex;gap:8px;overflow-x:auto;overflow-y:hidden;scroll-snap-type:x mandatory;padding:4px 1px 12px;margin-bottom:3px;scrollbar-width:thin;scrollbar-color:#3c5368 transparent;}
.ticker-item {display:flex;align-items:center;justify-content:space-between;flex:0 0 auto;min-width:170px;gap:14px;padding:11px 13px;border:1px solid #2a3c50;background:#111c2b;border-radius:11px;scroll-snap-align:start;}
.ticker-item .sym {color:#e9f5ff;font-weight:800;font-size:12px;letter-spacing:.2px;}
.ticker-item .pct {font-size:11px;font-weight:700;}
.ticker-item .last {font-size:10px;color:#7f97af;margin-top:5px;text-align:right;}
.watch-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:12px 0 15px;}
.watch-card {border:1px solid #2a3b50;background:linear-gradient(135deg,#142236,#101a29);border-radius:12px;padding:14px;min-width:0;}
.watch-symbol {font-weight:800;font-size:13px;color:#eaf5ff;}
.watch-price {font:700 19px 'Space Grotesk',sans-serif;color:#eaf6ff;margin:12px 0 5px;overflow-wrap:anywhere;}
.watch-change {font-weight:700;font-size:12px;}
.watch-sub {color:#7992ab;font-size:10px;margin-top:9px;}
[data-testid="stPlotlyChart"] {max-width:100%;min-width:0;}
[data-testid="stDataFrame"] {max-width:100%;min-width:0;}
@media (max-width: 1200px) {
  .kpi-grid,.watch-grid {grid-template-columns:repeat(2,minmax(0,1fr));}
  [data-testid="stMainBlockContainer"],.block-container {padding-left:1.35rem;padding-right:1.35rem;}
}
@media (max-width: 767px) {
  [data-testid="stMainBlockContainer"],.block-container {padding:.7rem .85rem 3rem!important;width:100%!important;max-width:100%!important;}
  [data-testid="stHorizontalBlock"] {flex-wrap:wrap!important;gap:.65rem!important;}
  [data-testid="stHorizontalBlock"] > [data-testid="column"] {flex:1 1 100%!important;min-width:0!important;width:100%!important;}
  [data-testid="stTabs"] [data-baseweb="tab-list"] {overflow-x:auto!important;overflow-y:hidden!important;flex-wrap:nowrap!important;scrollbar-width:thin;gap:0;}
  [data-testid="stTabs"] [data-baseweb="tab"] {font-size:12px!important;white-space:nowrap;min-width:max-content;padding:12px 13px;}
  .hero {padding:19px 17px;border-radius:15px;margin-top:8px;}
  .hero-title {font-size:clamp(25px,8vw,34px);letter-spacing:-1px;line-height:1.16;}
  .hero-copy {font-size:12px;}
  .kpi-grid,.watch-grid {grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;}
  .kpi-card {min-height:107px;padding:13px 12px;border-radius:12px;}
  .kpi-value {font-size:clamp(17px,4.8vw,23px);letter-spacing:-.6px;}
  .kpi-label {font-size:10px;letter-spacing:0;line-height:1.4;margin-bottom:9px;}
  .kpi-foot {font-size:10px;line-height:1.4;}
  .watch-card {padding:12px;}
  .watch-price {font-size:18px;}
  .topline {margin:0 0 5px;}
  .topline div {font-size:10px!important;}
  .section-title {font-size:18px;}
  .ticker-item {min-width:153px;}
  .panel {padding:15px;}
  .footer {font-size:10px;}
  .stButton button,.stDownloadButton button {min-height:44px;}
  div[data-testid="stTextInput"] input,div[data-baseweb="select"] {max-width:100%;}
}
@media (max-width: 350px) {
  .kpi-grid,.watch-grid {grid-template-columns:1fr;}
  .hero-title {font-size:25px;}
}
@media (prefers-reduced-motion:reduce){*,*:before,*:after{scroll-behavior:auto!important;animation:none!important;}}

</style>
""", unsafe_allow_html=True)


def format_price(x):
    if x is None or pd.isna(x):
        return "—"
    return f"{float(x):,.2f}".rstrip("0").rstrip(".")


def format_compact(x):
    if x is None or pd.isna(x):
        return "—"
    n = float(x)
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:,.2f}M"
    if abs(n) >= 1_000:
        return f"{n / 1_000:,.2f}K"
    return f"{n:,.0f}"


def metric(label, value, foot, change=None):
    cls = "kpi-positive" if change is not None and change >= 0 else "kpi-negative" if change is not None else ""
    return (f'<div class="kpi-card"><div class="kpi-label">{escape(label)}</div>'
            f'<div class="kpi-value {cls}">{escape(value)}</div>'
            f'<div class="kpi-foot">{escape(foot)}</div></div>')


def pair(label, value):
    return (f'<div class="mini-row"><span class="a">{escape(label)}</span>'
            f'<span class="b">{escape(str(value))}</span></div>')


def plot_theme(fig, height):
    fig.update_layout(
        template="plotly_dark", height=height, autosize=True,
        margin=dict(l=14, r=12, t=40, b=20),
        paper_bgcolor="#111b2a", plot_bgcolor="#111b2a",
        font=dict(family="DM Sans, sans-serif", size=11, color="#9BB0C8"),
        hoverlabel=dict(bgcolor="#1d2d43", font_color="#eaf3fb"),
        legend=dict(orientation="h", y=1.13, x=0, bgcolor="rgba(0,0,0,0)", font_size=10),
        hovermode="x unified", showlegend=True,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#233047", zeroline=False, linecolor="#31415a", tickfont_size=10)
    fig.update_yaxes(showgrid=True, gridcolor="#233047", zeroline=False, linecolor="#31415a", tickfont_size=10)
    return fig


def candle_chart(df, chart_kind, overlays):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        row_heights=[0.77, 0.23], vertical_spacing=.035)
    if chart_kind == "Nến OHLC":
        fig.add_trace(go.Candlestick(
            x=df['Time'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Giá", increasing=dict(line=dict(color=UP, width=1), fillcolor=UP),
            decreasing=dict(line=dict(color=DOWN, width=1), fillcolor=DOWN)), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=df['Time'], y=df['Close'], name='Giá đóng', mode='lines',
                                 line=dict(color=ACCENT, width=2.4), fill='tozeroy',
                                 fillcolor='rgba(22,217,173,.055)'), row=1, col=1)
    lines = {'SMA5': ('#F6C45D', 1.8), 'SMA20': ('#668EFF', 2.1), 'EMA12': ('#D78CFF', 1.8),
             'BBUpper': ('#91A5B9',1.2), 'BBLower': ('#91A5B9',1.2)}
    if 'Bollinger' in overlays:
        overlays = [x for x in overlays if x!='Bollinger'] + ['BBUpper', 'BBLower']
    for name in overlays:
        if name in lines and name in df:
            color, width = lines[name]
            fig.add_trace(go.Scatter(x=df['Time'], y=df[name], name=name, mode='lines',
                                     line=dict(color=color, width=width,
                                               dash='dot' if name.startswith('BB') else 'solid')),
                          row=1, col=1)
    colors = [UP if c >= o else DOWN for c,o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(x=df['Time'], y=df['Volume'], marker_color=colors,
                         opacity=.8, name='Khối lượng', showlegend=False), row=2, col=1)
    fig.update_layout(xaxis_rangeslider_visible=False)
    plot_theme(fig, 485)
    fig.update_yaxes(title_text='GIÁ', row=1, col=1, title_font_size=10)
    fig.update_yaxes(title_text='KL', row=2, col=1, title_font_size=10)
    return fig


def indicator_chart(df, indicator):
    fig = go.Figure()
    if indicator == 'RSI (14)':
        fig.add_trace(go.Scatter(x=df.Time, y=df.RSI14, name='RSI14', line=dict(color='#C39BFF', width=2.3)))
        fig.add_hline(y=70, line_color='#FF7187', line_dash='dash', opacity=.65)
        fig.add_hline(y=30, line_color='#16D9AD', line_dash='dash', opacity=.65)
        fig.update_yaxes(range=[0, 100])
    else:
        fig.add_trace(go.Scatter(x=df.Time, y=df.MACD, name='MACD', line=dict(color='#13d8b0', width=2)))
        fig.add_trace(go.Scatter(x=df.Time, y=df.MACDSignal, name='Signal', line=dict(color='#f0b65c', width=2)))
        hist = df.MACD - df.MACDSignal
        fig.add_trace(go.Bar(x=df.Time, y=hist, name='Histogram', marker_color=[UP if v>=0 else DOWN for v in hist], opacity=.65))
    return plot_theme(fig, 295)


SYMBOLS = ['FPT', 'HPG', 'VNM', 'VCB', 'SSI', 'MWG', 'VPB', 'TCB']
source_names = {'DEMO': 'DỮ LIỆU MẪU', 'SSI': 'SSI FASTCONNECT'}
now_text = datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).strftime('%d/%m/%Y · %H:%M')

with st.sidebar:
    st.markdown('<div class="brand"><i class="dot"></i>SMART<b>STOCK</b></div><div class="brand-sub">SSI MARKET ANALYTICS</div>', unsafe_allow_html=True)
    st.markdown('<div class="nav-caption">VỀ WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel-text">Trung tâm phân tích giá và khối lượng với đồ thị nến, SMA, RSI, MACD và lịch sử dữ liệu từ SSI FastConnect.</div>', unsafe_allow_html=True)
    st.divider()
    st.markdown('<div class="panel-title">◉ Nguồn dữ liệu</div>', unsafe_allow_html=True)
    st.caption('DEMO: dữ liệu mô phỏng có gắn nhãn riêng.')
    st.caption('SSI: chỉ hiển thị dữ liệu thực đã nhận và lưu trên máy.')
    st.markdown('<div class="panel-title" style="margin-top:18px">Bảo mật & phạm vi</div>', unsafe_allow_html=True)
    st.caption('Chỉ đọc dữ liệu. Không có thao tác mua/bán, không lưu API Key vào mã nguồn.')
    st.caption('Thời gian giao diện: Việt Nam (UTC+7). Thời gian nến theo dữ liệu SSI.')
    st.markdown('<div style="height:20px"></div><div style="font-size:11px;color:#677f9a;line-height:1.6">SMARTSTOCK / RESPONSIVE EDITION<br>Desktop · Tablet · Mobile</div>', unsafe_allow_html=True)

st.markdown(f'''<div class="topline"><div style="color:#839ab3;font-size:12px;letter-spacing:1px;font-weight:800">SMARTSTOCK <span style="color:#45546b">/</span> SSI MARKET ANALYTICS</div><div style="font-size:12px;color:#839bb3">◷ {escape(now_text)} VN</div></div>''', unsafe_allow_html=True)
st.markdown('''<div class="hero"><div class="hero-eyebrow">SSI FASTCONNECT · MARKET INTELLIGENCE</div><div class="hero-title">Thị trường trong tầm mắt.</div><p class="hero-copy">Một không gian theo dõi chứng khoán chuyên nghiệp: biểu đồ giá, động lượng, khối lượng và dữ liệu có thể kiểm chứng — <b style="color:#e6f6ff">không đặt lệnh giao dịch</b>.</p><span class="hero-badge">◆ SMARTSTOCK PRO · SSI EDITION</span></div>''', unsafe_allow_html=True)
st.markdown('<div class="kicker">BỘ ĐIỀU KHIỂN THỊ TRƯỜNG</div>', unsafe_allow_html=True)
with st.container():
    ctl1, ctl2, ctl3, ctl4 = st.columns([1.5,1,1,1], gap='small')
    with ctl1:
        choice = st.selectbox('Nguồn dữ liệu', ['Demo (mô phỏng)', 'SSI FastConnect (thật)'], key='data_source', help='Không bao giờ thay dữ liệu SSI thật bằng dữ liệu mô phỏng khi có lỗi.')
    with ctl2:
        symbol = st.selectbox('Mã cổ phiếu', SYMBOLS, key='symbol')
    with ctl3:
        count_label = st.selectbox('Khoảng dữ liệu', ['Tất cả nến', '120 nến', '60 nến', '30 nến'], index=0)
    with ctl4:
        st.write('')
        st.write('')
        fetch = st.button('↻  Cập nhật dữ liệu', use_container_width=True, type='primary')
source = 'DEMO' if choice.startswith('Demo') else 'SSI'
st.markdown('<div class="toolbar-note">Chọn nguồn và mã ở đây trên cả máy tính lẫn điện thoại. Với SSI, bấm cập nhật để tải nến thật từ API.</div>', unsafe_allow_html=True)

if fetch:
    try:
        with st.spinner(f'Đang tải {symbol} từ {source_names[source]}...'):
            new_raw = example_candles(symbol) if source == 'DEMO' else fetch_ssi(symbol)
            new_processed = analyze(new_raw)
            if new_processed.empty:
                st.warning('Nguồn không trả dữ liệu OHLCV hợp lệ. Không dùng dữ liệu giả thay thế.')
            else:
                save(new_processed, source, symbol)
                st.session_state['last_fetch'] = (source, symbol, now_text)
                st.toast(f'Đã lưu {len(new_processed)} nến {symbol}', icon='✅')
    except Exception as e:
        st.error(f'Không lấy được dữ liệu {source_names[source]}. Loại lỗi: {type(e).__name__}. Kiểm tra kết nối và quyền API; không hiển thị khóa bí mật.')

# DEMO opens with attractive data immediately; SSI only uses real downloaded/stored candles.
if source == 'DEMO':
    df_full = analyze(example_candles(symbol))
else:
    df_full = analyze(load('SSI', symbol))

meta = source_names[source]
if source == 'DEMO':
    st.markdown('<div class="mode-ribbon demo"><strong>◆ DEMO / MÔ PHỎNG</strong> &nbsp; Toàn bộ giá và khối lượng ở chế độ này là dữ liệu giả định. Không phải giá thị trường.</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="mode-ribbon"><strong>● SSI FASTCONNECT / DỮ LIỆU THẬT</strong> &nbsp; Dữ liệu lấy từ API và đã lưu; có thể là dữ liệu lịch sử, không cam kết realtime.</div>', unsafe_allow_html=True)

if df_full.empty:
    st.markdown('<div class="empty"><h3>Chưa có dữ liệu SSI cho mã này</h3><p>Chọn “Tải / cập nhật dữ liệu” ở menu bên trái. Không sử dụng dữ liệu mẫu trong chế độ SSI.</p></div>', unsafe_allow_html=True)
    st.stop()

window = {'Tất cả nến': None, '120 nến': 120, '60 nến': 60, '30 nến': 30}[count_label]
df = df_full.tail(window).copy() if window else df_full.copy()
s = summarize(df)
latest = df.iloc[-1]
chg = s['window_change_pct']

# Horizontal, touch-scrollable ticker; SSI only uses data downloaded from SSI.
ticker_parts = []
for tape_symbol in SYMBOLS:
    tape_data = analyze(example_candles(tape_symbol)) if source == 'DEMO' else analyze(load('SSI', tape_symbol))
    if tape_data.empty:
        continue
    tape_info = summarize(tape_data)
    pct = tape_info['window_change_pct']
    color = '#16D9AD' if pct >= 0 else '#FF627D'
    ticker_parts.append(
        f'<div class="ticker-item"><div class="sym">{escape(tape_symbol)}</div>'
        f'<div><div class="pct" style="color:{color}">{pct:+.2f}%</div>'
        f'<div class="last">{escape(format_price(tape_info["last_close"]))}</div></div></div>'
    )
if ticker_parts:
    st.markdown('<div class="ticker-track">' + ''.join(ticker_parts) + '</div>', unsafe_allow_html=True)

st.markdown('<div class="kicker">01 / TỔNG QUAN GIÁ VÀ THANH KHOẢN</div>', unsafe_allow_html=True)
cards = [
    metric('GIÁ ĐÓNG NẾN CUỐI', format_price(s['last_close']), 'Đơn vị giá theo API'),
    metric('BIẾN ĐỘNG CỬA SỔ', f'{chg:+.2f}%', 'Đóng nến cuối / mở nến đầu', change=chg),
    metric('TỔNG KHỐI LƯỢNG', format_compact(s['total_volume']), 'Tổng khối lượng các nến'),
    metric('ĐỈNH / ĐÁY CỬA SỔ', f'{format_price(s["window_high"])} / {format_price(s["window_low"])}', f'{len(df)} nến đang hiển thị'),
]
st.markdown('<div class="kpi-grid">'+''.join(cards)+'</div>', unsafe_allow_html=True)
st.caption(f'Nến mới nhất trong dữ liệu: {s["last_time"]}  ·  {source_names[source]}  ·  Chỉ số theo khoảng đang xem, không mặc định là biến động toàn phiên.')

tab_overview, tab_watch, tab_analysis, tab_history = st.tabs(['◈ Biểu đồ', '▦ Bảng giá', '◎ Kỹ thuật', '⇩ Dữ liệu'])

with tab_overview:
    st.markdown('<div class="section-title">Diễn biến giá</div><div class="section-sub">Giá OHLC, đường trung bình động và khối lượng giao dịch trong cùng một biểu đồ.</div>', unsafe_allow_html=True)
    p1,p2 = st.columns([1,2], gap='medium')
    with p1:
        chart_kind = st.selectbox('Dạng biểu đồ', ['Nến OHLC', 'Đường giá'], label_visibility='collapsed')
    with p2:
        overlays = st.multiselect('Chỉ báo hiển thị', ['SMA5','SMA20','EMA12','Bollinger'], default=['SMA5','SMA20'], label_visibility='collapsed')
    left,right = st.columns([3.5,1.3], gap='medium')
    with left:
        st.plotly_chart(candle_chart(df, chart_kind, overlays), use_container_width=True, config={'displaylogo':False, 'scrollZoom':True, 'responsive':True})
    with right:
        rsi = latest['RSI14']
        sma20 = latest['SMA20']
        trend = 'Trên SMA20' if pd.notna(sma20) and latest['Close']>sma20 else 'Dưới SMA20' if pd.notna(sma20) and latest['Close']<sma20 else 'Chưa đủ dữ liệu'
        st.markdown('<div class="panel"><div class="panel-title">Tóm tắt phiên quan sát</div>'
                    + pair('Mã',symbol) + pair('Mở nến đầu',format_price(s['window_open']))
                    + pair('Đóng nến cuối',format_price(s['last_close']))
                    + pair('Giá cao nhất',format_price(s['window_high']))
                    + pair('Giá thấp nhất',format_price(s['window_low']))
                    + pair('RSI (14)',f'{rsi:.1f}' if pd.notna(rsi) else '—')
                    + pair('Vị trí giá',trend) + '</div>', unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="panel-title">Tính minh bạch</div>'
                    '<div class="panel-text">Dữ liệu được gắn nhãn theo nguồn. Các nến trùng và bản ghi thiếu được loại bỏ. Không có lệnh mua/bán hoặc tín hiệu giao dịch tự động.</div></div>', unsafe_allow_html=True)

with tab_watch:
    st.markdown('<div class="section-title">Danh sách theo dõi</div><div class="section-sub">Các mã cổ phiếu đã có dữ liệu. Với SSI, chỉ hiển thị những mã đã thật sự tải về máy.</div>', unsafe_allow_html=True)
    rows=[]
    for sym in SYMBOLS:
        data = analyze(example_candles(sym)) if source=='DEMO' else analyze(load('SSI', sym))
        if data.empty:
            if source=='SSI':
                rows.append({'Mã':sym,'Giá đóng':'Chưa tải', 'Biến động':None, 'Số nến':0, 'Thời điểm nến':'—'})
            continue
        x = summarize(data)
        rows.append({'Mã':sym, 'Giá đóng':round(x['last_close'],2),
                     'Biến động':round(x['window_change_pct'],2),
                     'Số nến':x['candles'], 'Thời điểm nến':x['last_time']})
    watch = pd.DataFrame(rows)
    tile_parts = []
    for item in rows:
        price = item['Giá đóng']
        percentage = item['Biến động']
        signed = f'{percentage:+.2f}%' if percentage is not None else '—'
        p_color = '#16D9AD' if percentage is not None and percentage >= 0 else '#FF627D' if percentage is not None else '#8799B2'
        shown_price = format_price(price) if isinstance(price, (float,int)) else str(price)
        tile_parts.append(
            '<div class="watch-card">'
            f'<div class="watch-symbol">{escape(item["Mã"])}</div>'
            f'<div class="watch-price">{escape(shown_price)}</div>'
            f'<div class="watch-change" style="color:{p_color}">{escape(signed)}</div>'
            f'<div class="watch-sub">{int(item["Số nến"])} nến lưu</div></div>'
        )
    st.markdown('<div class="watch-grid">'+''.join(tile_parts)+'</div>', unsafe_allow_html=True)
    st.dataframe(watch, use_container_width=True, hide_index=True, height=380,
                 column_config={'Biến động':st.column_config.NumberColumn('Biến động (%)', format='%.2f%%'),
                                'Số nến':st.column_config.NumberColumn('Số nến',format='%d')})
    st.caption('Danh sách là dữ liệu lịch sử đã tải hoặc mô phỏng. Không phải bảng giá realtime toàn thị trường.')
    if source=='DEMO':
        st.markdown('<div class="mode-ribbon demo"><strong>Mọi giá trong bảng này đều được tạo giả lập.</strong> Chuyển sang SSI để chỉ xem dữ liệu thực đã tải.</div>', unsafe_allow_html=True)

with tab_analysis:
    st.markdown('<div class="section-title">Trung tâm phân tích kỹ thuật</div><div class="section-sub">Công thức công khai, phân tích mang tính mô tả. Không phải tín hiệu giao dịch.</div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    for slot,label,col in [(a,'SMA (5)','SMA5'),(b,'SMA (20)','SMA20'),(c,'RSI (14)','RSI14'),(d,'MACD (12/26)','MACD')]:
        with slot:
            st.markdown(metric(label,format_price(latest[col]),'Theo chuỗi nến đang lưu'), unsafe_allow_html=True)
    st.markdown('<div class="section-title">Diễn biến động lượng</div>', unsafe_allow_html=True)
    ind = st.radio('Chọn chỉ báo', ['RSI (14)', 'MACD (12/26/9)'], horizontal=True)
    st.plotly_chart(indicator_chart(df, ind), use_container_width=True, config={'displaylogo':False, 'responsive':True})
    st.markdown('<div class="insight"><strong>NHẬN ĐỊNH MÔ TẢ</strong><br>' + escape(describe(df_full)) + '</div>', unsafe_allow_html=True)
    with st.expander('Phương pháp, công thức và giới hạn', expanded=False):
        st.markdown('''**Biến động cửa sổ:** `(đóng nến cuối / mở nến đầu − 1) × 100%`. Không đồng nghĩa % thay đổi từ giá tham chiếu phiên.

**SMA5, SMA20:** Trung bình động giản đơn của 5 hoặc 20 giá đóng nến. **EMA12:** Trung bình động hàm mũ 12 kỳ.

**RSI14:** Dựa trên trung bình 14 kỳ của giá tăng và giảm; nằm trong khoảng 0–100.

**MACD:** EMA12 − EMA26; đường tín hiệu EMA9 của MACD. **Bollinger:** SMA20 ± 2 lần độ lệch chuẩn 20 kỳ.

Dữ liệu SSI được lấy từ `get_ohlc_1minute`; đây là dữ liệu nến, có thể không phản ánh giá tức thời. Mọi phân tích đều cần kiểm chứng trước khi dùng cho quyết định tài chính.''')

with tab_history:
    st.markdown('<div class="section-title">Nhật ký dữ liệu OHLCV</div><div class="section-sub">Quan sát chi tiết các nến đã làm sạch, thống kê và tải về CSV để đối chiếu.</div>', unsafe_allow_html=True)
    shown = df[['Time','Open','High','Low','Close','Volume','SMA5','SMA20','RSI14','MACD']].copy()
    st.dataframe(shown.sort_values('Time',ascending=False),use_container_width=True,hide_index=True,height=410)
    st.download_button('↓  Tải dữ liệu CSV',data=df.to_csv(index=False).encode('utf-8-sig'),
                       file_name=f'SmartStock_{source}_{symbol}_OHLCV.csv',mime='text/csv',use_container_width=False)
    st.markdown('<div class="panel"><div class="panel-title">Thông tin tập dữ liệu</div>'
                + pair('Nguồn',source_names[source]) + pair('Mã chứng khoán',symbol)
                + pair('Nến hợp lệ',f'{len(df):,}') + pair('Nến cuối',s['last_time'])
                + pair('Dữ liệu lỗi/trùng','Được lọc trước khi lưu') + '</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">SMARTSTOCK TERMINAL · SSI FASTCONNECT MARKET ANALYTICS &nbsp; / &nbsp; Bản responsive cho desktop & mobile — chỉ đọc dữ liệu, không gửi lệnh giao dịch. Dữ liệu mô phỏng luôn có nhãn riêng. Giá và thời gian phải được đối chiếu với đơn vị và quy ước của nguồn cung cấp.</div>', unsafe_allow_html=True)
