from pyspark.sql.functions import col, trim, lower
from spark_common import create_spark_session, RAW_DIR, PROCESSED_DIR, ensure_dirs, check_raw_files

def main():
    ensure_dirs()
    check_raw_files()
    spark = create_spark_session("SmartLibraryClean")

    books_df = spark.read.csv(str(RAW_DIR / "books.csv"), header=True, inferSchema=True)
    ratings_df = spark.read.csv(str(RAW_DIR / "ratings.csv"), header=True, inferSchema=True)
    tags_df = spark.read.csv(str(RAW_DIR / "tags.csv"), header=True, inferSchema=True)
    book_tags_df = spark.read.csv(str(RAW_DIR / "book_tags.csv"), header=True, inferSchema=True)
    to_read_df = spark.read.csv(str(RAW_DIR / "to_read.csv"), header=True, inferSchema=True)

    books_clean = books_df.dropna(subset=["book_id"]).dropDuplicates(["book_id"])
    if "title" in books_clean.columns:
        books_clean = books_clean.withColumn("title", trim(col("title"))).fillna({"title": "Sans titre"})
    if "authors" in books_clean.columns:
        books_clean = books_clean.withColumn("authors", trim(col("authors"))).fillna({"authors": "Inconnu"})
    if "language_code" in books_clean.columns:
        books_clean = books_clean.withColumn("language_code", lower(trim(col("language_code")))).fillna({"language_code": "unknown"})
    for numeric_col in ["average_rating", "ratings_count", "work_ratings_count", "original_publication_year"]:
        if numeric_col in books_clean.columns:
            books_clean = books_clean.fillna({numeric_col: 0})

    ratings_clean = (
        ratings_df
        .dropna(subset=["user_id", "book_id", "rating"])
        .dropDuplicates()
        .filter((col("rating") >= 1) & (col("rating") <= 5))
    )

    tags_clean = tags_df.dropna(subset=["tag_id"]).dropDuplicates(["tag_id"])
    if "tag_name" in tags_clean.columns:
        tags_clean = tags_clean.withColumn("tag_name", lower(trim(col("tag_name")))).fillna({"tag_name": "unknown"})

    book_tags_clean = book_tags_df.dropna(subset=["goodreads_book_id", "tag_id"]).dropDuplicates()
    to_read_clean = to_read_df.dropna(subset=["user_id", "book_id"]).dropDuplicates()

    books_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "books_clean.parquet"))
    ratings_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "ratings_clean.parquet"))
    tags_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "tags_clean.parquet"))
    book_tags_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "book_tags_clean.parquet"))
    to_read_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "to_read_clean.parquet"))

    print("Nettoyage terminé avec succès.")
    print("Livres:", books_clean.count())
    print("Ratings:", ratings_clean.count())
    print("Tags:", tags_clean.count())
    print("Book tags:", book_tags_clean.count())
    print("To read:", to_read_clean.count())
    spark.stop()

if __name__ == "__main__":
    main()
