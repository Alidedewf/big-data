# Отчёт по практической работе №6

**Дисциплина:** Методы анализа и обработки больших данных  
**Тема:** Работа с Apache Hive и Apache Pig в экосистеме больших данных

## Цель работы

Освоить базовые операции анализа данных в Apache Hive и Apache Pig: загрузку CSV из HDFS, фильтрацию, проекцию, агрегацию и сортировку. Сравнить SQL-подобный язык HiveQL и конвейерный язык Pig Latin.

## 1. Исходные данные

Использован набор из пяти пользователей. Файл [users.csv](practice-06/data/users.csv) содержит заголовок и удобен для просмотра. Для Hive и Pig подготовлен [users_hdfs.csv](practice-06/data/users_hdfs.csv) без заголовка: это предотвращает попытку интерпретировать строку с названиями столбцов как данные.

| user_id | name | age | city | salary |
| ---: | --- | ---: | --- | ---: |
| 1 | Alex | 25 | Almaty | 1200 |
| 2 | Maria | 32 | Astana | 2300 |
| 3 | Timur | 28 | Shymkent | 1800 |
| 4 | Aigerim | 42 | Almaty | 3500 |
| 5 | Diana | 29 | Karaganda | 2000 |

## 2. Apache Hive

Apache Hive — слой SQL-подобных запросов над данными в HDFS. Запросы HiveQL преобразуются в задачи выполнения, например MapReduce, Tez или Spark. Hive удобен для аналитических запросов, таблиц, агрегирования и соединений данных.

В файле [hive_queries.hql](practice-06/hive_queries.hql) создана база `lab_hive` и внешняя таблица `users`.

```sql
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
```

Внешняя таблица хранит только метаданные в Hive Metastore, а сами данные остаются в HDFS по пути `/data`. При удалении внешней таблицы файлы HDFS не удаляются автоматически.

Выполнены запросы:

```sql
SELECT * FROM users;
SELECT name, age FROM users WHERE age > 30;
SELECT AVG(age) AS avg_age FROM users;
SELECT city, COUNT(*) AS total FROM users GROUP BY city ORDER BY city;
SELECT name, salary FROM users ORDER BY salary DESC;
```

## 3. Apache Pig

Apache Pig — высокоуровневый инструмент для создания последовательных конвейеров обработки данных. Его язык Pig Latin описывает поток: загрузка → фильтрация → проекция → группировка → сортировка. Pig преобразует скрипт в задания для Hadoop.

Скрипт [pig_analysis.pig](practice-06/pig_analysis.pig) загружает данные и создаёт отношения для каждой операции.

```pig
users = LOAD '/data/users_hdfs.csv'
USING PigStorage(',')
AS (user_id:int, name:chararray, age:int, city:chararray, salary:int);

older_users = FILTER users BY age > 30;
names_cities = FOREACH users GENERATE name, city;
grouped = GROUP users BY city;
count_by_city = FOREACH grouped GENERATE group AS city, COUNT(users) AS total;
sorted = ORDER users BY salary DESC;
```

`DUMP` в скрипте выводит каждое отношение в консоль. В реальной задаче вместо `DUMP` для больших объёмов обычно используют `STORE` для сохранения результата в HDFS.

## 4. Результаты запросов

### Пользователи старше 30 лет

| name | age |
| --- | ---: |
| Maria | 32 |
| Aigerim | 42 |

### Средний возраст

```text
31.2
```

### Количество пользователей по городам

| city | total |
| --- | ---: |
| Almaty | 2 |
| Astana | 1 |
| Karaganda | 1 |
| Shymkent | 1 |

### Сортировка зарплат по убыванию

| name | salary |
| --- | ---: |
| Aigerim | 3500 |
| Maria | 2300 |
| Diana | 2000 |
| Timur | 1800 |
| Alex | 1200 |

### Проекция имени и города в Pig

| name | city |
| --- | --- |
| Alex | Almaty |
| Maria | Astana |
| Timur | Shymkent |
| Aigerim | Almaty |
| Diana | Karaganda |

Результаты проверены локально программой [verify_results.py](practice-06/verify_results.py). Она воспроизводит логику заданий над тем же CSV и содержит проверки ожидаемого среднего возраста, суммарного числа пользователей и максимальной зарплаты.

## 5. Запуск в Hadoop-среде

Для фактического выполнения Hive и Pig требуются установленные Hadoop, Hive и Pig, которых в текущей среде нет. Готовый сценарий [run_hdfs_commands.sh](practice-06/run_hdfs_commands.sh) выполняет загрузку данных в HDFS и запускает оба скрипта:

```bash
chmod +x practice-06/run_hdfs_commands.sh
practice-06/run_hdfs_commands.sh
```

Эквивалентные команды:

```bash
hdfs dfs -mkdir -p /data
hdfs dfs -put -f practice-06/data/users_hdfs.csv /data/users_hdfs.csv
hive -f practice-06/hive_queries.hql
pig practice-06/pig_analysis.pig
```

Локальная проверка без Hadoop:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python practice-06/verify_results.py
```

## 6. Сравнение Hive и Pig

| Критерий | Hive | Pig |
| --- | --- | --- |
| Язык | HiveQL, похож на SQL | Pig Latin, пошаговый язык потока данных |
| Удобные задачи | SQL-аналитика, BI, отчёты, агрегаты, таблицы | ETL, последовательные трансформации, нестандартная обработка |
| Модель работы | Декларативная: описывается требуемый результат | Процедурная: описываются этапы получения результата |
| Хранение | Таблицы и метаданные над данными HDFS | Отношения и конвейеры над файлами HDFS |

HiveQL похож на SQL, но работает с данными в распределённой файловой системе и обычно не предназначен для коротких транзакционных операций. Запрос Hive компилируется в распределённые задачи, поэтому время ответа и модель выполнения отличаются от классической реляционной СУБД.

## 7. Ответы на контрольные вопросы

### 1. Для чего используется Apache Hive?

Hive используется для SQL-подобного анализа больших данных, находящихся в HDFS или совместимых хранилищах. Он позволяет определять таблицы и выполнять фильтрацию, агрегацию, сортировку, соединения и аналитические запросы.

### 2. Чем отличается HiveQL от SQL?

Синтаксис HiveQL во многом похож на SQL, но HiveQL ориентирован на пакетную распределённую обработку, а не на транзакции с малой задержкой. HiveQL-запрос преобразуется в вычислительные задачи Hadoop-экосистемы и работает с файлами, а не с традиционными страницами реляционной СУБД.

### 3. Что такое Pig Latin и чем он удобен?

Pig Latin — язык описания потоков обработки данных в Apache Pig. Он удобен тем, что превращает сложную цепочку фильтраций, проекций, группировок и сортировок в последовательность читаемых шагов, не требуя писать MapReduce-код вручную.

### 4. Какой тип задач удобнее решать в Pig, а какой — в Hive?

Pig удобнее для ETL-конвейеров, очистки и многошаговых трансформаций данных. Hive удобнее для SQL-аналитики, агрегированных отчётов, работы с таблицами и BI-инструментами. На практике можно использовать Pig для подготовки, а Hive — для последующего анализа подготовленных данных.

### 5. Как осуществляется взаимодействие Hive/Pig с HDFS?

Оба инструмента читают и записывают файлы в HDFS. Hive создаёт метаданные таблиц, связывающие схему с путём к файлам; Pig загружает файлы оператором `LOAD` и сохраняет результат оператором `STORE`. Их вычисления превращаются в распределённые задачи, которые получают данные из HDFS и записывают результаты обратно.

## Вывод

Подготовлены HiveQL-запросы и Pig Latin-конвейер для анализа пользователей из CSV. Выполнены фильтрация, проекция, среднее, группировка и сортировка. Hive подходит для SQL-подобной аналитики, Pig — для пошаговой трансформации данных. Скрипты готовы к запуску в среде Hadoop; локальная проверка подтвердила ожидаемые результаты без имитации наличия Hive/Pig.
