"""
Traitement Big Data avec Apache Spark pour Smart University Library AI.

Version corrigée finale :
- compatible avec le books.csv Goodbooks-10k qui contient best_book_id mais pas forcément goodreads_book_id ;
- évite les colonnes Spark de type VOID, non supportées par l'export CSV ;
- génère :
    data/processed/spark_books_features.csv
    data/processed/spark_processing_summary.json

Exécution :
    cd /workspaces/smart-university-library-ai
    source .venv/bin/activate
    PYTHONPATH=backend python backend/bigdata/spark_goodbooks_processing.py
"""

from pathlib import Path
import json
import shutil

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    col,
    count,
    countDistinct,
    coalesce,
    lit,
    log1p,
    round as spark_round,
)
from pyspark.sql.types import StringType, DoubleType, LongType

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw" / "goodbooks-10k"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SPARK_OUT_DIR = PROCESSED_DIR / "spark_books_features"
FINAL_CSV = PROCESSED_DIR / "spark_books_features.csv"
SUMMARY_JSON = PROCESSED_DIR / "spark_processing_summary.json"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

REQUIRED_FILES = {
    "books": RAW_DIR / "books.csv",
    "ratings": RAW_DIR / "ratings.csv",
    "to_read": RAW_DIR / "to_read.csv",
}


def check_required_files():
    missing = [str(path) for path in REQUIRED_FILES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Fichiers Goodbooks-10k manquants :\n"
            + "\n".join(missing)
            + "\n\nPlace les fichiers dans data/raw/goodbooks-10k/."
        )


def copy_single_part_csv(spark_output_dir: Path, final_csv: Path):
    parts = list(spark_output_dir.glob("part-*.csv"))
    if not parts:
        raise FileNotFoundError(f"Aucun fichier part-*.csv trouvé dans {spark_output_dir}")
    if final_csv.exists():
        final_csv.unlink()
    shutil.copy(parts[0], final_csv)


def optional_col(df, name: str, alias: str = None, default_value="", dtype="string"):
    """
    Retourne une colonne si elle existe, sinon une colonne par défaut typée.
    Important : Spark CSV ne supporte pas les colonnes VOID, donc on caste toujours.
    """
    output_name = alias or name

    if name in df.columns:
        return col(name).alias(output_name)

    if dtype == "long":
        return lit(default_value if default_value is not None else 0).cast(LongType()).alias(output_name)
    if dtype == "double":
        return lit(default_value if default_value is not None else 0.0).cast(DoubleType()).alias(output_name)
    return lit(default_value if default_value is not None else "").cast(StringType()).alias(output_name)


def main():
    check_required_files()

    spark = (
        SparkSession.builder
        .appName("SmartLibraryGoodbooksBigDataProcessing")
        .master("local[*]")
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    print("=== Lecture des fichiers Goodbooks-10k avec Spark ===")
    books = spark.read.csv(str(REQUIRED_FILES["books"]), header=True, inferSchema=True)
    ratings = spark.read.csv(str(REQUIRED_FILES["ratings"]), header=True, inferSchema=True)
    to_read = spark.read.csv(str(REQUIRED_FILES["to_read"]), header=True, inferSchema=True)

    print("Colonnes books.csv détectées :")
    print(books.columns)

    total_books = books.count()
    total_ratings = ratings.count()
    total_to_read = to_read.count()

    print(f"Livres lus      : {total_books}")
    print(f"Ratings lus     : {total_ratings}")
    print(f"To-read lus     : {total_to_read}")

    print("=== Agrégation des ratings ===")
    ratings_agg = (
        ratings
        .groupBy("book_id")
        .agg(
            count("*").alias("spark_ratings_count"),
            countDistinct("user_id").alias("spark_distinct_users_count"),
            spark_round(avg("rating"), 4).alias("spark_average_rating"),
        )
    )

    print("=== Agrégation des listes de lecture ===")
    to_read_agg = (
        to_read
        .groupBy("book_id")
        .agg(
            count("*").alias("spark_to_read_count"),
            countDistinct("user_id").alias("spark_to_read_users_count"),
        )
    )

    print("=== Construction des features Spark ===")

    selected_books = books.select(
        optional_col(books, "book_id", "book_id", 0, "long"),
        optional_col(books, "goodreads_book_id", "goodreads_book_id", "", "string"),
        optional_col(books, "best_book_id", "best_book_id", 0, "long"),
        optional_col(books, "work_id", "work_id", 0, "long"),
        optional_col(books, "title", "title", "", "string"),
        optional_col(books, "authors", "authors", "", "string"),
        optional_col(books, "original_publication_year", "original_publication_year", 0, "double"),
        optional_col(books, "average_rating", "catalog_average_rating", 0.0, "double"),
        optional_col(books, "ratings_count", "catalog_ratings_count", 0, "long"),
        optional_col(books, "work_ratings_count", "work_ratings_count", 0, "long"),
        optional_col(books, "work_text_reviews_count", "work_text_reviews_count", 0, "long"),
    )

    features = (
        selected_books
        .join(ratings_agg, on="book_id", how="left")
        .join(to_read_agg, on="book_id", how="left")
        .fillna({
            "goodreads_book_id": "",
            "best_book_id": 0,
            "work_id": 0,
            "title": "",
            "authors": "",
            "original_publication_year": 0,
            "catalog_average_rating": 0,
            "catalog_ratings_count": 0,
            "work_ratings_count": 0,
            "work_text_reviews_count": 0,
            "spark_ratings_count": 0,
            "spark_distinct_users_count": 0,
            "spark_average_rating": 0,
            "spark_to_read_count": 0,
            "spark_to_read_users_count": 0,
        })
    )

    features = features.withColumn(
        "spark_popularity_score",
        spark_round(
            log1p(coalesce(col("spark_ratings_count"), lit(0))) * lit(0.45)
            + log1p(coalesce(col("spark_to_read_count"), lit(0))) * lit(0.35)
            + coalesce(col("spark_average_rating"), lit(0)) * lit(0.20),
            4,
        )
    )

    features = features.orderBy(col("spark_popularity_score").desc())

    print("=== Écriture des résultats Spark ===")
    if SPARK_OUT_DIR.exists():
        shutil.rmtree(SPARK_OUT_DIR)

    features.coalesce(1).write.mode("overwrite").option("header", True).csv(str(SPARK_OUT_DIR))
    copy_single_part_csv(SPARK_OUT_DIR, FINAL_CSV)

    features_count = features.count()
    top_rows = [row.asDict() for row in features.select(
        "book_id",
        "title",
        "authors",
        "spark_popularity_score",
        "spark_ratings_count",
        "spark_to_read_count",
    ).limit(10).collect()]

    summary = {
        "tool": "Apache Spark / PySpark",
        "execution_mode": "local[*]",
        "input_files": {name: str(path.relative_to(BASE_DIR)) for name, path in REQUIRED_FILES.items()},
        "output_csv": str(FINAL_CSV.relative_to(BASE_DIR)),
        "spark_output_dir": str(SPARK_OUT_DIR.relative_to(BASE_DIR)),
        "total_books": total_books,
        "total_ratings": total_ratings,
        "total_to_read": total_to_read,
        "features_count": features_count,
        "available_book_columns": books.columns,
        "top_10_books_by_spark_popularity": top_rows,
    }

    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Traitement Spark terminé avec succès.")
    print(f"CSV final : {FINAL_CSV}")
    print(f"Résumé   : {SUMMARY_JSON}")

    spark.stop()


if __name__ == "__main__":
    main()
