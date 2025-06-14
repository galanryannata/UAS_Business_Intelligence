from django.shortcuts import render
import pandas as pd
import json
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

def shipping_risk_dashboard(request):
    try:
        # Load data
        shipping_risk_df = pd.read_csv('dashboard/data/Fact_Shipping_Risk.csv')
        raw_data_df = pd.read_csv('dashboard/data/raw_data.csv')
    except Exception as e:
        return render(request, 'dashboard/chart.html', {'error': f'Gagal membaca file: {e}'})

    # Validasi kolom tanggal
    if 'tanggal' not in raw_data_df.columns:
        return render(request, 'dashboard/chart.html', {'error': "Kolom 'tanggal' tidak ditemukan di raw_data.csv"})

    # Samakan nama kolom kunci jika perlu
    if 'ID_Product' in shipping_risk_df.columns:
        shipping_risk_df.rename(columns={'ID_Product': 'product_id'}, inplace=True)

    if 'product_id' not in raw_data_df.columns or 'product_id' not in shipping_risk_df.columns:
        return render(request, 'dashboard/chart.html', {'error': 'Kolom product_id tidak ditemukan di salah satu file'})

    # Gabungkan data
    df = pd.merge(shipping_risk_df, raw_data_df, on='product_id', how='inner')

    # Parsing tanggal dan filter baris valid
    df['date'] = pd.to_datetime(df['tanggal'], errors='coerce')
    df = df.dropna(subset=['date', 'Shipping_Risk'])

    # Encode Shipping_Risk jika bertipe string
    if df['Shipping_Risk'].dtype == 'object':
        le = LabelEncoder()
        df['Shipping_Risk'] = le.fit_transform(df['Shipping_Risk'])

    # Buat kolom waktu
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['time_numeric'] = df['date'].dt.year + (df['date'].dt.month - 1) / 12

    # Cek cukup data
    if len(df) < 2:
        return render(request, 'dashboard/chart.html', {'error': 'Data tidak cukup untuk melatih model.'})

    # Machine learning - Linear Regression
    X = df[['time_numeric']]
    y = df['Shipping_Risk']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    # Prediksi dan pastikan tidak negatif
    df['predicted'] = model.predict(X)
    df['predicted'] = df['predicted'].clip(lower=0)

    # Agregasi bulanan
    monthly = df.groupby('year_month').agg({
        'Shipping_Risk': 'mean',
        'predicted': 'mean'
    }).reset_index()

    # Siapkan data untuk Chart.js
    labels = monthly['year_month'].tolist()
    actual = monthly['Shipping_Risk'].round(2).tolist()
    predicted = monthly['predicted'].round(2).tolist()

    return render(request, 'dashboard/chart.html', {
        'labels_json': json.dumps(labels),
        'actual_json': json.dumps(actual),
        'predicted_json': json.dumps(predicted),
    })
