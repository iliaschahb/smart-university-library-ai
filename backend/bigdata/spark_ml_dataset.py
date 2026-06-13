from pyspark.sql.functions import col, when, lit
from spark_common import create_spark_session, PROCESSED_DIR, ANALYTICS_DIR, ensure_dirs


def main():
    ensure_dirs()
    spark = create_spark_session("SmartLibraryMLDataset")

    books = spark.read.parquet(str(PROCESSED_DIR / "books_enriched.parquet"))

    ml_dataset = books.withColumn(
        "popularity_score",
        (col("rating_count") * 0.4)
        + (col("to_read_count") * 0.3)
        + (col("tag_count") * 0.1)
        + (col("goodreads_ratings_count") * 0.2)
    ).withColumn(
        "popularity_level",
        when(col("popularity_score") >= 600000, lit("élevée"))
        .when(col("popularity_score") >= 100000, lit("moyenne"))
        .otherwise(lit("faible"))
    ).select(
        "book_id",
        "title",
        "authors",
        "goodreads_average_rating",
        "goodreads_ratings_count",
        "rating_count",
        "avg_user_rating",
        "to_read_count",
        "tag_count",
        "popularity_score",
        "popularity_level"
    )

    ml_dataset.write.mode("overwrite").parquet(str(PROCESSED_DIR / "ml_popularity_dataset.parquet"))

    # Export CSV correctement échappé pour consultation humaine.
    # L'entraînement IA utilise prioritairement le Parquet.
    ml_dataset.coalesce(1).write.mode("overwrite") \
        .option("header", True) \
        .option("quoteAll", True) \
        .option("escape", '"') \
        .csv(str(ANALYTICS_DIR / "popularity_prediction_dataset_csv"))

    print("Dataset IA généré avec succès.")
    print("Parquet :", PROCESSED_DIR / "ml_popularity_dataset.parquet")
    print("CSV :", ANALYTICS_DIR / "popularity_prediction_dataset_csv")
    print("Lignes:", ml_dataset.count())
    print("Distribution popularité :")
    ml_dataset.groupBy("popularity_level").count().show(truncate=False)

    spark.stop()


if __name__ == "__main__":
    main()
