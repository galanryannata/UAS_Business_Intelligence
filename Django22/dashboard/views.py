from .models import ShippingCost, ProductCategory, ProductShape
import os
import csv
import json
import numpy as np
import pandas as pd
from datetime import datetime
from django.shortcuts import render
from django.conf import settings
from django.db import transaction
from django.db.models import Avg
from django.db.models.functions import ExtractYear, ExtractMonth
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.preprocessing import StandardScaler

def shipping_cost_dashboard(request):
    # Import data dari CSV jika ShippingCost kosong
    if not ShippingCost.objects.exists():
        shipping_csv_path = os.path.join(settings.BASE_DIR, 'dashboard/static/Fact_Shipping_Cost.csv')
        category_csv_path = os.path.join(settings.BASE_DIR, 'dashboard/static/DIM_Product_Category.csv')

        df_cost = pd.read_csv(shipping_csv_path)
        df_cat = pd.read_csv(category_csv_path)

        # Perbaiki nama kolom typo
        df_cat = df_cat.rename(columns={
            'product_description_lenght': 'product_description_length',
            'product_name_lenght': 'product_name_length'
        })

        df_cost['ID_Product'] = df_cost['ID_Product'].astype(str).str.strip()
        df_cat['ID_Product'] = df_cat['ID_Product'].astype(str).str.strip()

        df_cat['tanggal'] = pd.to_datetime(df_cat['tanggal'])

        # Simpan ke ProductCategory
        categories = []
        for _, row in df_cat.iterrows():
            categories.append(ProductCategory(
                ID_Product=row['ID_Product'],
                tanggal=row['tanggal'],
                product_category_name=row['product_category_name'],
                product_description_length=row['product_description_length'],
                product_name_length=row['product_name_length']
            ))
        with transaction.atomic():
            ProductCategory.objects.bulk_create(categories, ignore_conflicts=True)

        shipping_records = []
        for _, row in df_cost.iterrows():
            try:
                product = ProductCategory.objects.get(ID_Product=row['ID_Product'])
                shape = ProductShape.objects.get(ID_Shape=row['ID_Shape'])
                shipping_records.append(ShippingCost(
                    ID_Product=product,
                    ID_Shape=shape,
                    Shipping_Cost=row['Shipping_Cost'],
                    tanggal=product.tanggal
                ))
            except (ProductCategory.DoesNotExist, ProductShape.DoesNotExist):
                continue

        with transaction.atomic():
            ShippingCost.objects.bulk_create(shipping_records)

    # Ambil data untuk visualisasi
    data = (
        ShippingCost.objects
        .annotate(year=ExtractYear('tanggal'), month=ExtractMonth('tanggal'))
        .values('year', 'month')
        .annotate(avg_cost=Avg('Shipping_Cost'))
        .order_by('year', 'month')
    )

    X, y, labels = [], [], []
    for row in data:
        year, month = row['year'], row['month']
        avg_cost = float(row['avg_cost']) if row['avg_cost'] else 0
        labels.append(f"{year}-{month:02d}")
        time_index = year + (month - 1) / 12
        X.append([time_index])
        y.append(avg_cost)

    y_pred = []
    if X:
        # Normalisasi X dan y
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        
        X_scaled = scaler_X.fit_transform(X)
        y_scaled = scaler_y.fit_transform(np.array(y).reshape(-1, 1))

        # Polynomial Regression
        poly = PolynomialFeatures(degree=2)
        X_poly = poly.fit_transform(X_scaled)

        model = LinearRegression()
        model.fit(X_poly, y_scaled)

        y_pred_scaled = model.predict(X_poly)
        y_pred = scaler_y.inverse_transform(y_pred_scaled).flatten().tolist()  # balikkan ke skala asli

    return render(request, "shipping_cost_chart.html", {
        'labels_json': json.dumps(labels),
        'values_json': json.dumps(y),
        'predictions_json': json.dumps(y_pred),
    })
