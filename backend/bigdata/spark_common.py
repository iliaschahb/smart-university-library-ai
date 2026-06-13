from pathlib import Path
from pyspark.sql import SparkSession

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw" / "goodbooks-10k"
PROCESSED_DIR = BASE_DIR / "data" / "processed" / "goodbooks"
ANALYTICS_DIR = BASE_DIR / "data" / "analytics"

REQUIRED_FILES = [
    "books.csv",
    "ratings.csv",
    "tags.csv",
    "book_tags.csv",
    "to_read.csv",
]

def create_spark_session(app_name: str) -> SparkSession:
    spark = (
        SparkSession.builder
        .appName(app_name)
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark

def ensure_dirs():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

def check_raw_files():
    missing = []
    for file_name in REQUIRED_FILES:
        if not (RAW_DIR / file_name).exists():
            missing.append(str(RAW_DIR / file_name))
    if missing:
        raise FileNotFoundError(
            "Fichiers Goodbooks-10k manquants:\n" + "\n".join(missing) +
            "\n\nPlace les fichiers Kaggle dans data/raw/goodbooks-10k/"
        )
