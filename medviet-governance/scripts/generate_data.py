# scripts/generate_data.py
import pandas as pd
from faker import Faker
import random
import csv

fake = Faker("vi_VN")
Faker.seed(42)

def generate_patients(n=200):
    records = []
    for _ in range(n):
        records.append({
            "patient_id": fake.uuid4(),
            "ho_ten": fake.name(),
            "cccd": f"{random.randint(10000000000,99999999999)}",
            "ngay_sinh": fake.date_of_birth(minimum_age=18, maximum_age=90)
                              .strftime("%d/%m/%Y"),
            "so_dien_thoai": f"0{random.choice([3,5,7,8,9])}" +
                              "".join([str(random.randint(0,9)) for _ in range(8)]),
            "email": fake.email(),
            "dia_chi": fake.address(),
            "benh": random.choice(["Tiểu đường", "Huyết áp cao", 
                                   "Tim mạch", "Khỏe mạnh"]),
            "ket_qua_xet_nghiem": round(random.uniform(3.5, 12.0), 2),
            "bac_si_phu_trach": fake.name(),
            "ngay_kham": fake.date_this_year().strftime("%d/%m/%Y"),
        })
    return pd.DataFrame(records)

df = generate_patients()
# Force string columns to stay as string in CSV
df["cccd"] = df["cccd"].astype(str)
df["so_dien_thoai"] = df["so_dien_thoai"].astype(str)
# Add quotes to preserve leading zeros
df.to_csv("data/raw/patients_raw.csv", index=False, quoting=csv.QUOTE_ALL)
print(f"Generated {len(df)} patient records")
print(df.head(3))
