import pandas as pd

url = "https://football.razzball.com/projections/"

tables = pd.read_html(url)

print("Tables found:", len(tables))

for i, table in enumerate(tables):
    print()
    print("=" * 60)
    print("TABLE", i)
    print("Shape:", table.shape)
    print("Columns:")
    print(table.columns.tolist())

    if len(table) > 20:
        print()
        print(table.head(10).to_string(index=False))