from pyspark.sql.functions import col, trim, lower
from spark_common import create_spark_session, RAW_DIR, PROCESSED_DIR, ensure_dirs, check_raw_files


def read_csv_safe(spark, file_name):
    """
    Lecture CSV robuste pour Goodbooks-10k.
    Important pour books.csv : certains titres contiennent des guillemets et des virgules.
    """
    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .option("quote", '"')
        .option("escape", '"')
        .option("multiLine", True)
        .csv(str(RAW_DIR / file_name))
    )


def main():
    ensure_dirs()
    check_raw_files()
    spark = create_spark_session("SmartLibraryClean")

    books_df = read_csv_safe(spark, "books.csv")
    ratings_df = read_csv_safe(spark, "ratings.csv")
    tags_df = read_csv_safe(spark, "tags.csv")
    book_tags_df = read_csv_safe(spark, "book_tags.csv")
    to_read_df = read_csv_safe(spark, "to_read.csv")

    books_clean = books_df.dropna(subset=["id", "book_id"]).dropDuplicates(["id"])

    if "title" in books_clean.columns:
        books_clean = books_clean.withColumn("title", trim(col("title"))).fillna({"title": "Sans titre"})
    if "authors" in books_clean.columns:
        books_clean = books_clean.withColumn("authors", trim(col("authors"))).fillna({"authors": "Inconnu"})
    if "language_code" in books_clean.columns:
        books_clean = books_clean.withColumn("language_code", lower(trim(col("language_code")))).fillna({"language_code": "unknown"})

    for numeric_col in [
        "id", "book_id", "best_book_id", "work_id", "average_rating",
        "ratings_count", "work_ratings_count", "original_publication_year"
    ]:
        if numeric_col in books_clean.columns:
            books_clean = books_clean.withColumn(numeric_col, col(numeric_col).cast("double"))

    books_clean = books_clean.filter(col("average_rating").isNotNull())
    books_clean = books_clean.filter(col("ratings_count").isNotNull())

    ratings_clean = (
        ratings_df
        .dropna(subset=["user_id", "book_id", "rating"])
        .dropDuplicates()
        .withColumn("book_id", col("book_id").cast("int"))
        .withColumn("user_id", col("user_id").cast("int"))
        .withColumn("rating", col("rating").cast("int"))
        .filter((col("rating") >= 1) & (col("rating") <= 5))
    )

    tags_clean = tags_df.dropna(subset=["tag_id"]).dropDuplicates(["tag_id"])
    tags_clean = tags_clean.withColumn("tag_id", col("tag_id").cast("int"))
    if "tag_name" in tags_clean.columns:
        tags_clean = tags_clean.withColumn("tag_name", lower(trim(col("tag_name")))).fillna({"tag_name": "unknown"})

    book_tags_clean = (
        book_tags_df
        .dropna(subset=["goodreads_book_id", "tag_id"])
        .dropDuplicates()
        .withColumn("goodreads_book_id", col("goodreads_book_id").cast("double"))
        .withColumn("tag_id", col("tag_id").cast("int"))
        .withColumn("count", col("count").cast("int"))
    )

    to_read_clean = (
        to_read_df
        .dropna(subset=["user_id", "book_id"])
        .dropDuplicates()
        .withColumn("user_id", col("user_id").cast("int"))
        .withColumn("book_id", col("book_id").cast("int"))
    )

    books_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "books_clean.parquet"))
    ratings_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "ratings_clean.parquet"))
    tags_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "tags_clean.parquet"))
    book_tags_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "book_tags_clean.parquet"))
    to_read_clean.write.mode("overwrite").parquet(str(PROCESSED_DIR / "to_read_clean.parquet"))

    print("Nettoyage robuste terminé avec succès.")
    print("Livres:", books_clean.count())
    print("Ratings:", ratings_clean.count())
    print("Tags:", tags_clean.count())
    print("Book tags:", book_tags_clean.count())
    print("To read:", to_read_clean.count())
    spark.stop()


if __name__ == "__main__":
    main()
