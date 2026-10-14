#!/usr/bin/env bash
set -euo pipefail

# Выполняется в окружении, где установлены hadoop, hive и pig.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

hdfs dfs -mkdir -p /data
hdfs dfs -put -f "$SCRIPT_DIR/data/users_hdfs.csv" /data/users_hdfs.csv

hive -f "$SCRIPT_DIR/hive_queries.hql"
pig "$SCRIPT_DIR/pig_analysis.pig"
