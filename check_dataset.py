import pandas as pd

df = pd.read_csv("BDCBC7196_Hematology_Dataset.csv")

print("Columns:")
print(df.columns)

print("\nUnique Diagnosis Values:")
print(df["Diagnosis"].unique())

print("\nFirst 5 rows:")
print(df.head())
