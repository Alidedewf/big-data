"""Практическая работа №5: обработка сенсорных данных с Pandas и Dask."""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import dask.dataframe as dd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import psutil


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORT_DIR = BASE_DIR / "report"
CSV_PATH = DATA_DIR / "sensor_data.csv"
PANDAS_PARQUET = REPORT_DIR / "hourly_pandas.parquet"
DASK_PARQUET_DIR = REPORT_DIR / "hourly_dask"
ROLLING_PLOT = REPORT_DIR / "rolling_sensor.png"

CSV_DTYPES = {
    "sensor_id": "string",
    "measurement": "float32",
    "unit": "string",
    "quality": "float32",
}


def generate_sensor_data(path: Path) -> None:
    """Создаёт воспроизводимый учебный CSV, если исходный файл не приложен."""
    rng = np.random.default_rng(42)
    sensors = [f"sensor_{number:02d}" for number in range(1, 13)]
    timestamps = pd.date_range("2025-01-01", periods=7 * 24 * 60, freq="min")

    frame = pd.MultiIndex.from_product(
        [sensors, timestamps], names=["sensor_id", "timestamp"]
    ).to_frame(index=False)
    sensor_offset = frame["sensor_id"].str.extract(r"(\d+)")[0].astype(float).to_numpy()
    minutes = np.tile(np.arange(len(timestamps)), len(sensors))
    daily_wave = 4 * np.sin(2 * np.pi * minutes / (24 * 60))
    frame["measurement"] = (
        20 + sensor_offset * 0.25 + daily_wave + rng.normal(0, 0.7, len(frame))
    ).astype("float32")
    frame["unit"] = "C"
    frame["quality"] = rng.uniform(0.7, 1.0, len(frame)).astype("float32")

    # Пропуски оставлены только у строк достаточного качества: ffill имеет смысл.
    missing_rows = rng.choice(frame.index[frame["quality"] >= 0.8], size=900, replace=False)
    frame.loc[missing_rows, "measurement"] = np.nan
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def read_and_prepare_pandas() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Читает и очищает CSV в памяти, возвращая данные, агрегацию и rolling."""
    df = pd.read_csv(CSV_PATH, dtype=CSV_DTYPES, parse_dates=["timestamp"])
    cleaned = df.loc[df["quality"] >= 0.8].copy()
    cleaned = cleaned.sort_values(["sensor_id", "timestamp"])
    cleaned["measurement"] = cleaned.groupby("sensor_id")["measurement"].ffill()
    cleaned["hour"] = cleaned["timestamp"].dt.floor("h")

    hourly = (
        cleaned.groupby(["sensor_id", "hour"], as_index=False)["measurement"]
        .mean()
        .rename(columns={"measurement": "mean_measurement"})
    )

    sensor = cleaned.loc[cleaned["sensor_id"] == "sensor_01", ["timestamp", "measurement"]]
    rolling = sensor.set_index("timestamp")["measurement"].rolling("5min").mean().reset_index()
    rolling = rolling.rename(columns={"measurement": "rolling_5min"})
    return cleaned, hourly, rolling


def clean_dask_partition(partition: pd.DataFrame) -> pd.DataFrame:
    """Очистка каждой партиции; CSV заранее упорядочен по датчику и времени."""
    partition = partition.loc[partition["quality"] >= 0.8].copy()
    partition = partition.sort_values(["sensor_id", "timestamp"])
    partition["measurement"] = partition.groupby("sensor_id")["measurement"].ffill()
    partition["hour"] = partition["timestamp"].dt.floor("h")
    return partition


def write_dask_parquet(hourly: dd.DataFrame) -> None:
    """Сохраняет каждую Dask-партицию отдельным Parquet-файлом fastparquet."""
    if DASK_PARQUET_DIR.exists():
        shutil.rmtree(DASK_PARQUET_DIR)
    DASK_PARQUET_DIR.mkdir(parents=True)
    for number, delayed_partition in enumerate(hourly.to_delayed()):
        partition = delayed_partition.compute()
        partition.to_parquet(
            DASK_PARQUET_DIR / f"part-{number:05d}.parquet",
            engine="fastparquet",
            index=False,
        )


def process_with_dask() -> tuple[pd.DataFrame, int]:
    """Выполняет эквивалентную агрегацию Dask и возвращает результат для проверки."""
    ddf = dd.read_csv(
        CSV_PATH,
        dtype=CSV_DTYPES,
        parse_dates=["timestamp"],
        blocksize="512 KiB",
    )
    meta = ddf._meta.assign(hour=pd.Series(dtype="datetime64[ns]"))
    cleaned = ddf.map_partitions(clean_dask_partition, meta=meta)
    hourly = (
        cleaned.groupby(["sensor_id", "hour"])["measurement"]
        .mean()
        .reset_index()
        .rename(columns={"measurement": "mean_measurement"})
    )
    write_dask_parquet(hourly)
    result = hourly.compute().sort_values(["sensor_id", "hour"]).reset_index(drop=True)
    return result, ddf.npartitions


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    if not CSV_PATH.exists():
        generate_sensor_data(CSV_PATH)
        print(f"Создан учебный CSV: {CSV_PATH.name}")

    process = psutil.Process()
    memory_before = process.memory_info().rss / 1024**2

    pandas_started = time.perf_counter()
    source = pd.read_csv(CSV_PATH, dtype=CSV_DTYPES, parse_dates=["timestamp"])
    cleaned, hourly_pandas, rolling = read_and_prepare_pandas()
    pandas_seconds = time.perf_counter() - pandas_started
    memory_after_pandas = process.memory_info().rss / 1024**2
    hourly_pandas.to_parquet(PANDAS_PARQUET, engine="fastparquet", index=False)

    dask_started = time.perf_counter()
    hourly_dask, partitions = process_with_dask()
    dask_seconds = time.perf_counter() - dask_started
    memory_after_dask = process.memory_info().rss / 1024**2

    expected = hourly_pandas.sort_values(["sensor_id", "hour"]).reset_index(drop=True)
    comparison = expected.merge(
        hourly_dask,
        on=["sensor_id", "hour"],
        suffixes=("_pandas", "_dask"),
        how="outer",
        indicator=True,
    )
    difference = (
        comparison["mean_measurement_pandas"] - comparison["mean_measurement_dask"]
    ).abs().max()

    plt.figure(figsize=(11, 4))
    six_hours_end = rolling["timestamp"].min() + pd.Timedelta(hours=6)
    plot_data = rolling.loc[rolling["timestamp"] < six_hours_end]
    plt.plot(plot_data["timestamp"], plot_data["rolling_5min"], linewidth=1)
    plt.title("Скользящее среднее измерений sensor_01 за первые 6 часов")
    plt.xlabel("Время")
    plt.ylabel("Температура, C")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(ROLLING_PLOT, dpi=160)
    plt.close()

    print("\nПервые пять строк:")
    print(source.head().to_string(index=False))
    print("\nИнформация о данных:")
    source.info()
    print("\nОписательная статистика:")
    print(source.describe().to_string())
    print(f"\nУникальных датчиков: {source['sensor_id'].nunique()}")
    print(f"Строк до фильтрации: {len(source)}")
    print(f"Строк после quality >= 0.8: {len(cleaned)}")
    print(f"Пропусков measurement после ffill: {cleaned['measurement'].isna().sum()}")
    print(f"Почасовых групп: {len(hourly_pandas)}")
    print(f"Dask-партиций: {partitions}")
    print(f"Максимальная разница Pandas и Dask: {difference:.8f}")
    print(f"Pandas: {pandas_seconds:.4f} c, память процесса: {memory_after_pandas - memory_before:.2f} MiB")
    print(f"Dask: {dask_seconds:.4f} c, память процесса: {memory_after_dask - memory_after_pandas:.2f} MiB")
    print(f"Результаты: {PANDAS_PARQUET.name}, {DASK_PARQUET_DIR.name}/, {ROLLING_PLOT.name}")


if __name__ == "__main__":
    main()
