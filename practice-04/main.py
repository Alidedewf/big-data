from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split


REPORT_DIR = Path(__file__).resolve().parent / "report"
REPORT_DIR.mkdir(exist_ok=True)
DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def main() -> None:
    # California Housing: target — медианная стоимость дома в сотнях тысяч долларов.
    # Кэш датасета сохраняется рядом с работой, а не в домашней папке пользователя.
    housing = fetch_california_housing(data_home=DATA_DIR)
    df = pd.DataFrame(housing.data, columns=housing.feature_names)
    df["target"] = housing.target

    print("Первые пять строк:")
    print(df.head().to_string())
    print("\nИнформация о данных:")
    df.info()

    # X — независимые признаки, y — числовая целевая переменная.
    X = df.drop(columns="target")
    y = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"\nРазмер обучающей выборки: {len(X_train)}")
    print(f"Размер тестовой выборки: {len(X_test)}")
    print(f"MAE: {mae:.4f}")
    print(f"MSE: {mse:.4f}")
    print(f"R²: {r2:.4f}")

    # Идеальные предсказания находятся на красной диагонали y = x.
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.45, edgecolors="none")
    limits = [min(y_test.min(), y_pred.min()), max(y_test.max(), y_pred.max())]
    plt.plot(limits, limits, "r--", label="Идеальное предсказание")
    plt.xlim(limits)
    plt.ylim(limits)
    plt.xlabel("Фактическая стоимость, $100 000")
    plt.ylabel("Предсказанная стоимость, $100 000")
    plt.title("California Housing: фактические и предсказанные значения")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "actual_vs_predicted.png", dpi=160)
    plt.show()
    plt.close()


if __name__ == "__main__":
    main()
