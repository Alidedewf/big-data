"""Локальная проверка ожидаемых результатов HiveQL и Pig Latin без кластера Hadoop."""

from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).resolve().parent / "data" / "users.csv"


def table(frame: pd.DataFrame) -> str:
    return frame.to_string(index=False)


def main() -> None:
    users = pd.read_csv(DATA_PATH)

    older_users = users.loc[users["age"] > 30, ["name", "age"]]
    average_age = users["age"].mean()
    count_by_city = (
        users.groupby("city", as_index=False)
        .size()
        .rename(columns={"size": "total"})
        .sort_values("city")
    )
    sorted_salary = users.loc[:, ["name", "salary"]].sort_values("salary", ascending=False)
    names_cities = users.loc[:, ["name", "city"]]

    assert average_age == 31.2
    assert count_by_city["total"].sum() == len(users)
    assert sorted_salary.iloc[0].to_dict() == {"name": "Aigerim", "salary": 3500}

    print("Все пользователи:")
    print(table(users))
    print("\nHive: пользователи старше 30 лет:")
    print(table(older_users))
    print(f"\nHive: средний возраст: {average_age:.1f}")
    print("\nHive/Pig: количество пользователей по городам:")
    print(table(count_by_city))
    print("\nHive/Pig: сортировка по зарплате:")
    print(table(sorted_salary))
    print("\nPig: проекция имени и города:")
    print(table(names_cities))
    print("\nПроверка результатов завершена успешно.")


if __name__ == "__main__":
    main()
