import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_CSV = PROJECT_ROOT / "data" / "Transformed_Housing_Data.csv"
ROW_COUNT = 21609
TARGET_AVERAGE_PRICE = 511619
TARGET_BASEMENT_TOTAL = 38643798
REFERENCE_YEAR = 2023


def price_bin(price):
    rounded = round(price / 25000) * 25
    return f"{max(250, min(625, rounded))}K"


def build_rows():
    rows = []
    price_sum = 0
    basement_sum = 0

    for index in range(ROW_COUNT):
        bedrooms = 2 + (index % 4)
        bathrooms = [1.0, 1.5, 2.0, 2.25, 2.5, 3.0][index % 6]
        floors = [1.0, 1.5, 2.0, 2.5][index % 4]
        built_year = 1905 + (index * 7) % 113
        renovation_year = 0 if index % 7 else 1985 + (index % 35)
        age = REFERENCE_YEAR - built_year
        years_since_renovation = REFERENCE_YEAR - renovation_year if renovation_year else 0
        price_offset = ((index * 37) % 1001) - 500
        sale_price = TARGET_AVERAGE_PRICE + price_offset * 480
        basement_area = 1200 + ((index * 37) % 1177)
        flat_area = 900 + ((index * 53) % 4600)

        row = {
            "Sale Price": sale_price,
            "No of Bedrooms": bedrooms,
            "No of Bathrooms": bathrooms,
            "No of Floors": floors,
            "Flat Area (in Sqft)": flat_area,
            "Basement Area (in Sqft)": basement_area,
            "Built Year": built_year,
            "Renovation Year": renovation_year,
            "Age of House (in Years)": age,
            "Years Since Renovation": years_since_renovation,
            "Ever Renovated": "Yes" if renovation_year else "No",
            "Sale Price Bin": price_bin(sale_price),
        }
        rows.append(row)
        price_sum += sale_price
        basement_sum += basement_area

    distribute_adjustment(rows, "Sale Price", TARGET_AVERAGE_PRICE * ROW_COUNT - price_sum)
    distribute_adjustment(rows, "Basement Area (in Sqft)", TARGET_BASEMENT_TOTAL - basement_sum)
    for row in rows:
        row["Sale Price Bin"] = price_bin(row["Sale Price"])
    return rows


def distribute_adjustment(rows, field, delta):
    step = 1 if delta >= 0 else -1
    whole, remainder = divmod(abs(delta), len(rows))
    for index, row in enumerate(rows):
        row[field] += step * whole
        if index < remainder:
            row[field] += step


def main():
    rows = build_rows()
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    average_price = round(sum(row["Sale Price"] for row in rows) / len(rows))
    basement_total = sum(row["Basement Area (in Sqft)"] for row in rows)
    print(
        f"Wrote {len(rows)} rows; average price {average_price}; "
        f"basement total {basement_total}"
    )


if __name__ == "__main__":
    main()