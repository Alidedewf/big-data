#!/usr/bin/env bash
set -euo pipefail

# Для shell-команд:
start-hbase.sh
hbase shell < "$(dirname "$0")/hbase_shell_commands.txt"

# Для Python API предварительно нужен Thrift Server:
# hbase-daemon.sh start thrift
# python "$(dirname "$0")/hbase_api.py"
