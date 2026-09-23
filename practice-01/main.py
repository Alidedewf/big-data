from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

data_path = Path(__file__).resolve().parent / "data" / "iris.csv"
df = pd.read_csv(data_path)
print(df.head())

print("\nОбщая информация:")
df.info()

print("\nОписательная статистика:")
print(df.describe())

print("\nПропуски по столбцам:")
print(df.isna().sum())

print("\nКоличество дубликатов:")
print(df.duplicated().sum())

print("\nОчистка данных:")
rows_before = len(df)

df = df.drop_duplicates().reset_index(drop=True)

print(f"Строк до очистки: {rows_before}")
print(f"Строк после очистки: {len(df)}")
print(f"Пропусков после очистки: {df.isna().sum().sum()}")
print(f"Дубликатов после очистки: {df.duplicated().sum()}")

stats = df.select_dtypes(include="number").agg(["mean", "min", "max"])
print(stats)


# График
plt.hist(df["sepal_length"], bins=10, edgecolor="black")

plt.title("Распределение длины чашелистика")
plt.xlabel("Длина чашелистика, см")
plt.ylabel("Количество цветков")
plt.tight_layout()

# Сохраняем график для отчёта
report_dir = Path(__file__).resolve().parent / "report"
report_dir.mkdir(exist_ok=True)
plt.savefig(report_dir / "histogram.png", dpi=150)

plt.show()