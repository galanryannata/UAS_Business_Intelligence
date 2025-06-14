from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import pandas as pd
import os

# Direktori simpan hasil
DATA_DIR = '/home/elluthya/datawarehouse'
EXTRACTED_PATH = f'{DATA_DIR}/raw_data.csv'

# --------------------
# 1. EXTRACT
# --------------------
def extract():
    df = pd.read_excel('/home/elluthya/airflow/dags/coba3.xlsx')  # Pastikan file ini ada
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(EXTRACTED_PATH, index=False)

# --------------------
# 2. TRANSFORM
# --------------------
def transform():
    df = pd.read_csv(EXTRACTED_PATH)

    # Transform DIM_Product_Category
    dim_category = df[['product_id', 'tanggal', 'product_category_name', 
                       'product_name_lenght', 'product_description_lenght']].copy()
    dim_category.rename(columns={'product_id': 'ID_Product'}, inplace=True)

    # Transform DIM_Product_Shape
    dim_shape = df[['product_length_cm', 'product_width_cm', 'product_height_cm']].drop_duplicates().copy()
    dim_shape['ID_Shape'] = range(1, len(dim_shape) + 1)
    df = df.merge(dim_shape, on=['product_length_cm', 'product_width_cm', 'product_height_cm'])

    # Transform DIM_Product_Weight
    dim_weight = df[['product_weight_g']].drop_duplicates().copy()
    dim_weight['ID_Weight'] = range(1, len(dim_weight) + 1)
    df = df.merge(dim_weight, on='product_weight_g')

    # FACT TABLES
    fact_shipping_risk = df[['shipping_risk', 'product_id', 'ID_Shape', 'ID_Weight']].copy()
    fact_shipping_risk.rename(columns={
        'shipping_risk': 'Shipping_Risk',
        'product_id': 'ID_Product'
    }, inplace=True)

    fact_shipping_cost = df[['shipping_cost', 'product_id', 'ID_Shape']].copy()
    fact_shipping_cost.rename(columns={
        'shipping_cost': 'Shipping_Cost',
        'product_id': 'ID_Product'
    }, inplace=True)

    fact_recommend_packing = df[['shipping_weight', 'volume_label', 'product_id', 'ID_Shape', 'ID_Weight']].copy()
    fact_recommend_packing.rename(columns={
        'shipping_weight': 'Shipping_Weight',
        'volume_label': 'Weight_Classification',
        'product_id': 'ID_Product'
    }, inplace=True)

    # Simpan hasil transform sementara
    dim_category.to_csv(f'{DATA_DIR}/DIM_Product_Category.csv', index=False)
    dim_shape.to_csv(f'{DATA_DIR}/DIM_Product_Shape.csv', index=False)
    dim_weight.to_csv(f'{DATA_DIR}/DIM_Product_Weight.csv', index=False)
    fact_shipping_risk.to_csv(f'{DATA_DIR}/Fact_Shipping_Risk.csv', index=False)
    fact_shipping_cost.to_csv(f'{DATA_DIR}/Fact_Shipping_Cost.csv', index=False)
    fact_recommend_packing.to_csv(f'{DATA_DIR}/Fact_Product_Recommend_Packing.csv', index=False)

# --------------------
# 3. LOAD
# --------------------
def load():
    # Untuk simulasi: anggap CSV hasil transform adalah "loaded" ke warehouse
    files = [
        'DIM_Product_Category.csv',
        'DIM_Product_Shape.csv',
        'DIM_Product_Weight.csv',
        'Fact_Shipping_Risk.csv',
        'Fact_Shipping_Cost.csv',
        'Fact_Product_Recommend_Packing.csv'
    ]
    for file in files:
        full_path = os.path.join(DATA_DIR, file)
        if os.path.exists(full_path):
            print(f"{file} ready to be loaded.")
        else:
            raise FileNotFoundError(f"{file} not found in {DATA_DIR}")

# --------------------
# DAG DEFINITION
# --------------------
with DAG(
    dag_id='etl_product_data_modular',
    schedule='@daily',  # Ganti schedule_interval → schedule (untuk Airflow 2.9+)
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['etl', 'product']
) as dag:

    extract_task = PythonOperator(
        task_id='extract_product_data',
        python_callable=extract
    )

    transform_task = PythonOperator(
        task_id='transform_product_data',
        python_callable=transform
    )

    load_task = PythonOperator(
        task_id='load_product_data',
        python_callable=load
    )

    # Define task dependencies
    extract_task >> transform_task >> load_task
