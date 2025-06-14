import pandas as pd

df_cost = pd.read_csv("dashboard/static/Fact_Shipping_Cost.csv")
df_cat = pd.read_csv("dashboard/static/DIM_Product_Category.csv")

print("Kolom Fact_Shipping_Cost:", df_cost.columns.tolist())
print("Kolom DIM_Product_Category:", df_cat.columns.tolist())
