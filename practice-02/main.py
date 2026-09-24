from pathlib import Path
import pandas as pd
import seaborn as sns
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent

data_path = BASE_DIR / "data" / "titanic.csv"
data_path.parent.mkdir(parents=True, exist_ok=True)

if data_path.exists():
    df = pd.read_csv(data_path)
else:
    df = sns.load_dataset("titanic")

    df.to_csv(data_path, index=False)

print("Первые пять строк:")
print(df.head().to_string())

print("\nРазмер таблицы:")
print(df.shape)

print("\nИнформация о столбцах:")
df.info()

print("\nПропуски по столбцам:")

missing = pd.DataFrame({
    "Количество": df.isna().sum(),
    "Процент": (df.isna().mean() * 100).round(2)
})

print(missing)

df_clean = df.copy()
age_median = df_clean["age"].median()
df_clean["age"] = df_clean["age"].fillna(age_median)

port_mode = df_clean["embarked"].mode().iloc[0]

town_mode = (
    df_clean.loc[df_clean["embarked"] == port_mode, "embark_town"]
    .mode()
    .iloc[0]
)

df_clean["embarked"] = df_clean["embarked"].fillna(port_mode)
df_clean["embark_town"] = df_clean["embark_town"].fillna(town_mode)

df_clean = df_clean.drop(columns=["deck"])

print("\nЗначения для заполнения:")
print(f"Медиана возраста: {age_median}")
print(f"Порт: {port_mode}, город: {town_mode}")

print("\nПропуски после обработки:")
print(df_clean.isna().sum())

print("\nРазмер после обработки:")
print(df_clean.shape)

df_encoded = pd.get_dummies(
    df_clean,
    columns=["sex", "embarked"],
    drop_first=True,
    dtype=int
)

print("\nДо кодирования:")
print(df_clean[["sex", "embarked"]].head())

print("\nПосле кодирования:")
print(
    df_encoded[
        ["sex_male", "embarked_Q", "embarked_S"]
    ].head()
)

df_scaled = df_encoded.copy()

scaler = StandardScaler()

df_scaled[["age", "fare"]] = scaler.fit_transform(
    df_encoded[["age", "fare"]]
)

print("\nДо стандартизации:")
print(df_encoded[["age", "fare"]].head())

print("\nПосле стандартизации:")
print(df_scaled[["age", "fare"]].head())

print("\nПроверка среднего:")
print(df_scaled[["age", "fare"]].mean().round(6))

print("\nПроверка стандартного отклонения:")
print(df_scaled[["age", "fare"]].std(ddof=0).round(6))

# Папка для сохранения графиков
report_dir = BASE_DIR / "report"
report_dir.mkdir(parents=True, exist_ok=True)

plt.figure(figsize=(9, 5))

sns.histplot(
    data=df_clean,
    x="age",
    bins=30,
    kde=True
)

plt.title("Распределение возраста пассажиров Titanic")
plt.xlabel("Возраст, лет")
plt.ylabel("Количество пассажиров")
plt.tight_layout()

plt.savefig(report_dir / "age_histogram.png", dpi=150)
plt.show()
plt.close()