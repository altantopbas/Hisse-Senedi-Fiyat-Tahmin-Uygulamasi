#####################
# AUTHOR: 
  # ALTAN TOPBAS
# TIME: 
  # 11.09.2024
#####################

import yfinance as yf
import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Veri indirme fonksiyonu
def download_data(op, start_date, end_date):
    try:
        df = yf.download(op, start=start_date, end=end_date, progress=False)
        if df.empty:
            raise ValueError("Boş veri seti")
        # Sadece hafta içi günleri al
        df = df[df.index.dayofweek < 5]
        return df
    except Exception as e:
        raise ValueError(f"Veri indirme hatası: {str(e)}")


# Tahmin modeli fonksiyonu
def model_engine(model, num, stock, data):
    df = data[['Close']].copy()  
    df['preds'] = df['Close'].shift(-num)

    x = df.drop(['preds'], axis=1).values
    x = scaler.fit_transform(x)
    x = x[:-num]
    x_forecast = x[-num:]

    y = df['preds'].values
    y = y[:-num]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    model.fit(x_train, y_train)
    preds = model.predict(x_test)
    accuracy = r2_score(y_test, preds) * 100
    print(f"İncelenen Firmanın Hisse Senedi Kodu: {stock} 'dir")
    print(f"Modelin Sağladığı Doğruluk Tahmini: %{accuracy:.2f}")

    forecasted_pred = model.predict(x_forecast)

    day = 1
    for i in forecasted_pred:
        print(f"{day}.Gün İçin Tahmini Kapanış Fiyatı: {i}")
        day += 1
    return forecasted_pred


# Grafik çizme fonksiyonu
def plot_forecast(stock, actual_data, predicted_data, forecast_dates):
    # Son 30 iş gününün gerçek kapanışlarını seç
    actual_last_30_days = actual_data[-30:]

    plt.figure(figsize=(12, 6))

    # Gerçek kapanışlar (son 30 iş günü)
    plt.plot(actual_last_30_days.index, actual_last_30_days, label=f"{stock} Son 30 İş Gününün Gerçek Kapanış Verisi", color='blue',
             linewidth=2)

    # Tahmin edilen kapanışlar (10 gün sonrası)
    plt.plot(forecast_dates, predicted_data, label=f"{stock} 10 Gün Sonrası Tahmini Kapanış Verisi", color='red',
             linestyle='--', linewidth=2)

    # Grafik ayarları
    plt.xlabel("Tarih")
    plt.ylabel("Fiyat")
    plt.title(f"{stock} Hisse Senedi Tahmini ve Son 30 İş Gününün Kapanış Verisi")

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Yalnızca iş günlerinin gösterilmesini sağla
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gca().xaxis.set_minor_locator(mdates.WeekdayLocator())

    plt.grid(True)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()


# Excel'e veri kaydetme fonksiyonu
def save_to_excel(stock, predicted_data, dates):
    df = pd.DataFrame({'Tarih': dates, 'Tahmini Kapanış Fiyatı': predicted_data})
    df['Tarih'] = df['Tarih'].dt.strftime('%Y-%m-%d')
    filename = f"{stock}_Tahminleri.xlsx"
    df.to_excel(filename, index=False)
    print(f"Tahmin sonuçları {filename} dosyasına kaydedildi.")


# Doğru şirket kodu alınana kadar tekrar sorulacak
def get_valid_stock():
    while True:
        stock = input("Tahmin yapmak istediğiniz şirketin hisse senedi kodunu girin (örneğin ASELS.IS): ")
        try:
            test_data = download_data(stock, start_date, end_date)
            if test_data.empty:
                raise ValueError("Boş veri seti")
            return stock
        except ValueError as e:
            print(f"Hatalı bir hisse senedi kodu girdiniz veya veri alınamadı: {str(e)}. Lütfen tekrar deneyin!")

while True:
    stock = input("Tahmin yapmak istediğiniz şirketin hisse senedi kodunu girin (örneğin ASELS.IS) veya çıkmak için 'exit' yazın: ")
    if stock.lower() == 'exit':
        break
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=365)
    end_date = today
    try:
        data = download_data(stock, start_date, end_date)
        num = 10
        scaler = StandardScaler()
        engine = LinearRegression()
        forecasted_pred = model_engine(engine, num, stock, data)
        last_date = data.index[-1]
        forecast_dates = []
        days_ahead = 1
        while len(forecast_dates) < num:
            next_date = last_date + datetime.timedelta(days=days_ahead)
            if next_date.weekday() < 5:
                forecast_dates.append(next_date)
            days_ahead += 1
        plot_forecast(stock, data['Close'], forecasted_pred, forecast_dates)
        save_to_excel(stock, forecasted_pred, forecast_dates)
    except Exception as e:
        print(f"An error occurred: {e}")
