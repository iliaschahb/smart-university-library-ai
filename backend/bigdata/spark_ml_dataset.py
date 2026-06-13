from pyspark.sql.functions import col, when, lit
from spark_common import create_spark_session, PROCESSED_DIR, ANALYTICS_DIR, ensure_dirs

def main():
    ensure_dirs()
    spark = create_spark_session("SmartLibraryMLDataset")

    books = spark.read.parquet(str(PROCESSED_DIR / "books_enriched.parquet"))

    ml_dataset = books.withColumn(
        "popularity_score",
        (col("rating_count") * 0.5) + (col("to_read_count") * 0.3) + (col("tag_count") * 0.2)
    ).withColumn(
        "popularity_level",
        when(col("rating_count") >= 1000, lit("élevée"))
        .when(col("rating_count") >= 300, lit("moyenne"))
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

    ml_dataset.coalesce(1).write.mode("overwrite").csv(
        str(ANALYTICS_DIR / "popularity_prediction_dataset_csv"),
        header=True
    )

    ml_dataset.write.mode("overwrite").parquet(str(PROCESSED_DIR / "ml_popularity_dataset.parquet"))

    print("Dataset IA généré : data/analytics/popularity_prediction_dataset_csv/")
    print("Lignes:", ml_dataset.count())
    spark.stop()

if __name__ == "__main__":
    main()
