import pandas as pd
import json
from django.shortcuts import render
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder

def packaging_trend_dashboard(request):
    try:
        df = pd.read_csv('dashboard/data/raw_data.csv')
    except Exception as e:
        return render(request, 'dashboard/chart.html', {'error': f'Gagal membaca file: {e}'})

    # Validasi kolom
    if 'tanggal' not in df.columns or 'recommended_packaging' not in df.columns:
        return render(request, 'dashboard/chart.html', {'error': 'Kolom tanggal atau recommended_packaging tidak ditemukan di file.'})

    # Parse tanggal dan bulan-tahun
    df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    df = df.dropna(subset=['tanggal', 'recommended_packaging'])
    df['year_month'] = df['tanggal'].dt.to_period('M').astype(str)

    # Hitung jumlah kemasan per bulan
    trend_df = df.groupby(['year_month', 'recommended_packaging']).size().reset_index(name='jumlah')

    # Prediksi per recommended_packaging
    result = {}
    for packaging in trend_df['recommended_packaging'].unique():
        subset = trend_df[trend_df['recommended_packaging'] == packaging].copy()
        subset['time_numeric'] = range(len(subset))

        X = subset[['time_numeric']]
        y = subset['jumlah']

        model = LinearRegression()
        model.fit(X, y)
        subset['predicted'] = model.predict(X).clip(min=0)

        result[packaging] = {
            'labels': subset['year_month'].tolist(),
            'actual': subset['jumlah'].tolist(),
            'predicted': subset['predicted'].round(2).tolist()
        }

    return render(request, 'dashboard/chart.html', {
        'result_json': json.dumps(result)
    })
