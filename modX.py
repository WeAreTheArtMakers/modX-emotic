import requests
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
from matplotlib.widgets import RadioButtons 
import matplotlib.font_manager as fm

# Emoji destekleyen fontu global olarak ayarla
mpl.rcParams['font.family'] = 'sans-serif'

# Emoji destekleyen fontu ayarla
font_path = "/Users/bg/modCharts/AppleColorEmoji.ttc " 
emoji_font = fm.FontProperties(fname=font_path, size=14)

# Başlangıç teması
current_theme = "light"

# Binance API'den veri çekme fonksiyonu
def get_binance_data(symbol="BTCUSDT", interval="1m", limit=60):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Binance API'ye erişim başarısız. Lütfen ayarları kontrol edin.")
        return pd.DataFrame()  # Boş bir DataFrame döndür
    data = response.json()
    df = pd.DataFrame(data, columns=[
        "Open Time", "Open", "High", "Low", "Close", "Volume",
        "Close Time", "Quote Asset Volume", "Number of Trades",
        "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"
    ])
    df["Open Time"] = pd.to_datetime(df["Open Time"], unit="ms")
    df["Close"] = df["Close"].astype(float)
    return df[["Open Time", "Close"]]


# Fibonacci seviyelerini hesaplama
def calculate_fibonacci_levels(data):
    high = data["Close"].max()
    low = data["Close"].min()
    diff = high - low
    levels = {
        "0%": low,
        "23.6%": high - 0.236 * diff,
        "38.2%": high - 0.382 * diff,
        "50%": high - 0.5 * diff,
        "61.8%": high - 0.618 * diff,
        "100%": high
    }
    # Seviyelere en yakın kapanış fiyatlarını bul
    prices = {key: data["Close"][(data["Close"] - value).abs().idxmin()] for key, value in levels.items()}
    return levels, prices

# Grafik ve animasyon
def plot_graph():
    global ax, ani, symbol, interval, limit

    # Binance API'den veri çek
    data = get_binance_data(symbol=symbol, interval=interval, limit=limit)
    if data.empty:
        print("Veri alınamadı.")
        return

    # Fibonacci seviyeleri ve fiyatları al
    levels, prices = calculate_fibonacci_levels(data)

    def update(frame):
        # Grafiği temizle
        ax.clear()

        # Fiyatları çiz
        ax.plot(data["Open Time"], data["Close"], label=f"{symbol} Fiyat", color="blue")

        # Fibonacci seviyeleri ve fiyatlarını güncelle
        for level_name, level_value in levels.items():
            ax.axhline(level_value, linestyle="--", label=f"modX {level_name}", color="gray")
            # Seviyelerin yanına fiyatları yaz
            ax.text(data["Open Time"].iloc[-1], level_value, f"{prices[level_name]:.2f}",
                    fontsize=10, color="red", ha="left", va="center")

         # Simge karakterlerini ekle
        for t, y, emoji in emojies:
            offset_index = (frame * 100 + list(data["Open Time"]).index(t)) % len(data)
            ax.text(data["Open Time"].iloc[offset_index], data["Close"].iloc[offset_index], emoji, fontsize=10, ha="center")

        # Emojileri ekle
        for t, y, emoji in emojies:
            ax.text(t, y, emoji, fontsize=14, ha="center", fontproperties=emoji_font)

        # Grafiğin ayarları
        ax.legend()
        ax.set_title(f"{symbol} modX Fiyat Hareketleri ({interval})")
        # ax.set_xlabel("Zaman")
        ax.set_ylabel("Fiyat")

    # Animasyonu başlat
    global ani  # Global olarak tanımlayın
    ani = FuncAnimation(fig, update, frames=range(len(data)), interval=1000 )
    plt.draw()


    # Emojileri grafiğe ekle
    emojies = []
    for i in range(len(data)):
        close_price = data["Close"].iloc[i]
    # Emoji mantığını düzelt
    if close_price > levels["50%"]:  # 50%'nin üstünde
        emoji = "⬆"
    elif close_price <= levels["38.2%"]:  # 38.2%'nin altında
        emoji = "⬇"
    else:  # Arada kalan seviyeler
        emoji = "↔"  # Belirsiz veya orta seviye hareket  
    if close_price > levels["61.8%"]:
        emoji = "😎"  # Fiyat yüksek seviyede
    elif close_price < levels["23.6%"]:
        emoji = "😇"  # Fiyat düşük seviyede
    elif levels["38.2%"] <= close_price <= levels["50%"]:
        emoji = "⚖"  # Orta seviyede
    else:
        emoji = "⚠"  # Belirsiz durum    
    emojies.append((data["Open Time"].iloc[i], close_price, emoji))

    def update(frame):
        ax.clear()
        ax.plot(data["Open Time"], data["Close"], label=f"{symbol} Fiyat", color="blue")

        # Fibonacci seviyelerini çiz
        for level_name, level_value in levels.items():
            ax.axhline(level_value, linestyle="--", label=f"USD {level_value:.2f}")

        for level_name, level_value in levels.items():
            ax.axhline(level_value, linestyle="--", color="gray") 

        ax.legend()
        ax.set_title(f"{symbol} modX Fiyat Hareketleri ({interval})")
        ax.set_xlabel("Zaman")
        ax.set_ylabel("Fiyat")

        # Emojileri güncelle
        for t, y, emoji in emojies:
            offset_index = (frame + list(data["Open Time"]).index(t)) % len(data)
            ax.text(data["Open Time"].iloc[offset_index], data["Close"].iloc[offset_index], emoji, fontsize=14, ha="center")

    ani = FuncAnimation(fig, update, frames=range(len(data)), interval=500)
    plt.draw()

# İlk değerler
symbol = "BTCUSDT"
interval = "1m"
limit = 60

# Matplotlib arayüzü
fig, ax = plt.subplots(figsize=(8, 6))
plt.subplots_adjust(left=0.25)  # Sol tarafta butonlar için yer aç

# Zaman aralığı değiştirme butonları
def change_interval(label):
    global interval
    interval = label
    plot_graph()

# Sembol değiştirme butonları
def change_symbol(label):
    global symbol
    symbol = label
    plot_graph()

# Bilgi kutusu ekle
info_text = (
    "⬆: Fiyat yüksek seviyede\n"
    "⬇: Fiyat düşük seviyede\n"
    "↔: Fiyat orta seviyede\n"
    "😎: Çok yüksek fiyat\n"
    "😇: Çok düşük fiyat\n"
    "⚖: Dengeli fiyat"
)
info_ax = plt.axes([0.01, 0.77, 0.25, 0.15])  # Sol üstte bilgi kutusu
info_ax.axis("off")  # Çerçeve kaldırıldı
info_ax.text(
    0, 0.5, info_text, fontsize=10, verticalalignment="center", horizontalalignment="left",
    transform=info_ax.transAxes, bbox=dict(facecolor="white", alpha=0.8, edgecolor="gray")
)

# Zaman aralığı için RadioButtons
ax_interval = plt.axes([0.01, 0.4, 0.1, 0.3])  # Sol tarafta yer
interval_radio = RadioButtons(ax_interval, ["1m", "3m", "15m", "1h", "4h", "1d", "3d", "8h", "6h", "2d", "3d"])
interval_radio.on_clicked(change_interval)

# Sembol değiştirme için RadioButtons
ax_symbol = plt.axes([0.01, 0.05, 0.15, 0.3])  # Sol tarafta yer
symbol_radio = RadioButtons(ax_symbol, ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "AVAXUSDT","BHCUSDT","ALGOUSDT","DOTUSDT","ATOMUSDT","APTUSDT"])
symbol_radio.on_clicked(change_symbol)

# Grafiği başlat
plot_graph()
plt.show()