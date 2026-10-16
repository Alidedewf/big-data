"""Проверяет логику CRUD из методички без установленного HBase-кластера."""


def show(row_key: str, row: dict[str, str]) -> None:
    print(f"{row_key} => {row}")


def main() -> None:
    # В HBase строка определяется row key, а колонки объединены в column families.
    students: dict[str, dict[str, str]] = {}

    students["1001"] = {
        "info:name": "Aigerim",
        "info:age": "22",
        "grades:math": "95",
    }
    print("CREATE/PUT:")
    show("1001", students["1001"])

    print("\nGET 'students', '1001':")
    show("1001", students["1001"])

    print("\nUPDATE: grades:math = 98")
    students["1001"]["grades:math"] = "98"
    print("DELETE: info:age")
    del students["1001"]["info:age"]
    show("1001", students["1001"])

    assert students["1001"] == {"info:name": "Aigerim", "grades:math": "98"}
    print("\nSCAN 'students':")
    for row_key, row in students.items():
        show(row_key, row)
    print("\nЛокальная проверка CRUD завершена успешно.")


if __name__ == "__main__":
    main()
