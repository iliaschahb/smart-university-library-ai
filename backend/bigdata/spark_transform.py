from pyspark.sql.functions import col, count, avg, desc, coalesce, lit
from spark_common import create_spark_session, PROCESSED_DIR, ensure_dirs


def main():
    """
    Transformation Big Data Goodbooks-10k.

    Points importants du dataset Goodbooks-10k :
    - books.id est l'identifiant interne utilisé par ratings.book_id et to_read.book_id.
    - books.book_id est l'identifiant Goodreads utilisé par book_tags.goodreads_book_id.

    Donc les jointures correctes sont :
    - books.id = ratings.book_id
    - books.id = to_read.book_id
    - books.book_id = book_tags.goodreads_book_id
    """

    ensure_dirs()
    spark = create_spark_session("SmartLibraryTransform")

    books = spark.read.parquet(str(PROCESSED_DIR / "books_clean.parquet"))
    ratings = spark.read.parquet(str(PROCESSED_DIR / "ratings_clean.parquet"))
    tags = spark.read.parquet(str(PROCESSED_DIR / "tags_clean.parquet"))
    book_tags = spark.read.parquet(str(PROCESSED_DIR / "book_tags_clean.parquet"))
    to_read = spark.read.parquet(str(PROCESSED_DIR / "to_read_clean.parquet"))

    print("Colonnes books :", books.columns)
    print("Colonnes ratings :", ratings.columns)
    print("Colonnes book_tags :", book_tags.columns)
    print("Colonnes to_read :", to_read.columns)

    # ------------------------------------------------------------------
    # 1. Statistiques des ratings
    # ratings.book_id correspond à books.id
    # ------------------------------------------------------------------
    rating_stats = (
        ratings
        .groupBy("book_id")
        .agg(
            count("*").alias("rating_count"),
            avg("rating").alias("avg_user_rating")
        )
    )

    # ------------------------------------------------------------------
    # 2. Statistiques des livres marqués "to read"
    # to_read.book_id correspond à books.id
    # ------------------------------------------------------------------
    to_read_stats = (
        to_read
        .groupBy("book_id")
        .agg(
            count("*").alias("to_read_count")
        )
    )

    # ------------------------------------------------------------------
    # 3. Statistiques des tags
    # book_tags.goodreads_book_id correspond à books.book_id
    # ------------------------------------------------------------------
    tag_stats_by_goodreads = (
        book_tags
        .groupBy("goodreads_book_id")
        .agg(
            count("tag_id").alias("tag_count")
        )
    )

    # ------------------------------------------------------------------
    # 4. Enrichissement des livres
    # ------------------------------------------------------------------
    books_enriched = (
        books.alias("b")
        .join(
            rating_stats.alias("r"),
            col("b.id") == col("r.book_id"),
            "left"
        )
        .join(
            to_read_stats.alias("tr"),
            col("b.id") == col("tr.book_id"),
            "left"
        )
        .join(
            tag_stats_by_goodreads.alias("tg"),
            col("b.book_id") == col("tg.goodreads_book_id"),
            "left"
        )
        .select(
            col("b.id").alias("book_id"),
            col("b.book_id").alias("goodreads_book_id"),
            col("b.best_book_id"),
            col("b.work_id"),
            col("b.title"),
            col("b.authors"),
            col("b.original_publication_year"),
            col("b.language_code"),
            col("b.average_rating").alias("goodreads_average_rating"),
            col("b.ratings_count").alias("goodreads_ratings_count"),
            coalesce(col("r.rating_count"), lit(0)).alias("rating_count"),
            coalesce(col("r.avg_user_rating"), lit(0.0)).alias("avg_user_rating"),
            coalesce(col("tr.to_read_count"), lit(0)).alias("to_read_count"),
            coalesce(col("tg.tag_count"), lit(0)).alias("tag_count")
        )
    )

    # ------------------------------------------------------------------
    # 5. Usage global des tags
    # ------------------------------------------------------------------
    tag_usage = (
        book_tags.alias("bt")
        .join(
            tags.alias("t"),
            col("bt.tag_id") == col("t.tag_id"),
            "left"
        )
        .groupBy("t.tag_name")
        .agg(
            count("*").alias("usage_count")
        )
        .orderBy(desc("usage_count"))
    )

    # ------------------------------------------------------------------
    # 6. Profils utilisateurs
    # ------------------------------------------------------------------
    user_profiles = (
        ratings
        .groupBy("user_id")
        .agg(
            count("*").alias("ratings_given"),
            avg("rating").alias("avg_rating_given")
        )
    )

    # ------------------------------------------------------------------
    # 7. Sauvegarde en Parquet
    # ------------------------------------------------------------------
    books_enriched.write.mode("overwrite").parquet(
        str(PROCESSED_DIR / "books_enriched.parquet")
    )

    tag_usage.write.mode("overwrite").parquet(
        str(PROCESSED_DIR / "tag_usage.parquet")
    )

    user_profiles.write.mode("overwrite").parquet(
        str(PROCESSED_DIR / "user_profiles.parquet")
    )

    print("Transformation terminée avec succès.")
    print("Books enriched:", books_enriched.count())
    print("Tag usage:", tag_usage.count())
    print("User profiles:", user_profiles.count())

    print("\nAperçu books_enriched :")
    books_enriched.show(10, truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
