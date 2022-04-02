import pandas as pd

data = pd.read_csv(f"uploads/products.csv")
df = pd.DataFrame(data)
df = df.drop_duplicates(subset=['sku'])
print(df.shape[0])

# for count, row in enumerate(data.itertuples(), start=1):
#         print(count)
#         print(row.description)