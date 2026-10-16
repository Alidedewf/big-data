"""CRUD в HBase через HappyBase. Требует запущенный HBase Thrift Server."""

import happybase


def main() -> None:
    connection = happybase.Connection("localhost")
    connection.open()

    table_name = "students"
    if table_name.encode() not in connection.tables():
        connection.create_table(
            table_name,
            {"info": dict(), "grades": dict()},
        )

    table = connection.table(table_name)
    table.put(
        b"1001",
        {
            b"info:name": b"Aigerim",
            b"info:age": b"22",
            b"grades:math": b"95",
        },
    )

    print("До обновления:", table.row(b"1001"))
    table.put(b"1001", {b"grades:math": b"98"})
    table.delete(b"1001", columns=[b"info:age"])
    print("После обновления и удаления:", table.row(b"1001"))

    print("Сканирование таблицы:")
    for row_key, data in table.scan():
        print(row_key, data)

    connection.close()


if __name__ == "__main__":
    main()
