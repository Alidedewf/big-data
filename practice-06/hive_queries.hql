-- Практическая работа №6. Запуск: hive -f hive_queries.hql
-- До запуска загрузить файл без заголовка в HDFS: /data/users_hdfs.csv.

CREATE DATABASE IF NOT EXISTS lab_hive;
USE lab_hive;

CREATE EXTERNAL TABLE IF NOT EXISTS users (
    user_id INT,
    name STRING,
    age INT,
    city STRING,
    salary INT
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/data';

-- Просмотр всех данных.
SELECT * FROM users;

-- Пользователи старше 30 лет.
SELECT name, age FROM users WHERE age > 30;

-- Средний возраст.
SELECT AVG(age) AS avg_age FROM users;

-- Количество пользователей по городам.
SELECT city, COUNT(*) AS total FROM users GROUP BY city ORDER BY city;

-- Сортировка по зарплате по убыванию.
SELECT name, salary FROM users ORDER BY salary DESC;
