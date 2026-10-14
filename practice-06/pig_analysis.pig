-- Практическая работа №6. Запуск: pig pig_analysis.pig
-- До запуска загрузить users_hdfs.csv в HDFS: /data/users_hdfs.csv.

users = LOAD '/data/users_hdfs.csv'
USING PigStorage(',')
AS (user_id:int, name:chararray, age:int, city:chararray, salary:int);

-- Фильтрация пользователей старше 30 лет.
older_users = FILTER users BY age > 30;
DUMP older_users;

-- Проекция: только имя и город.
names_cities = FOREACH users GENERATE name, city;
DUMP names_cities;

-- Группировка и подсчёт пользователей по городам.
grouped = GROUP users BY city;
count_by_city = FOREACH grouped GENERATE group AS city, COUNT(users) AS total;
DUMP count_by_city;

-- Сортировка по зарплате по убыванию.
sorted = ORDER users BY salary DESC;
DUMP sorted;
