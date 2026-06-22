#!/usr/bin/env bash
set -e

cd /workspaces/smart-university-library-ai
source .venv/bin/activate

python -m pip show pyspark >/dev/null 2>&1 || python -m pip install -r requirements_spark.txt

PYTHONPATH=backend python backend/bigdata/spark_goodbooks_processing.py

echo ""
echo "Fichiers générés :"
ls -lh data/processed/spark_books_features.csv data/processed/spark_processing_summary.json
