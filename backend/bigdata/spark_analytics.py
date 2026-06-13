from pyspark.sql.functions import col, count, desc
from spark_common import create_spark_session, PROCESSED_DIR, ANALYTICS_DIR, ensure_dirs

def main():
    ensure_dirs()
    spark = create_spark_session("SmartLibraryAnalytics")

    books = spark.read.parquet(str(PROCESSED_DIR / "books_enriched.parquet"))
    ratings = spark.read.parquet(str(PROCESSED_DIR / "ratings_clean.parquet"))
    tag_usage = spark.read.parquet(str(PROCESSED_DIR / "tag_usage.parquet"))
    user_profiles = spark.read.parquet(str(PROCESSED_DIR / "user_profiles.parquet"))

    top_books = books.orderBy(desc("rating_count"), desc("avg_user_rating")).limit(50)
    top_tags = tag_usage.orderBy(desc("usage_count")).limit(50)
    rating_distribution = ratings.groupBy("rating").agg(count("*").alias("count")).orderBy("rating")
    user_activity = user_profiles.orderBy(desc("ratings_given")).limit(50)

    top_books.coalesce(1).write.mode("overwrite").csv(str(ANALYTICS_DIR / "top_books_csv"), header=True)
    top_tags.coalesce(1).write.mode("overwrite").csv(str(ANALYTICS_DIR / "top_tags_csv"), header=True)
    rating_distribution.coalesce(1).write.mode("overwrite").csv(str(ANALYTICS_DIR / "rating_distribution_csv"), header=True)
    user_activity.coalesce(1).write.mode("overwrite").csv(str(ANALYTICS_DIR / "user_activity_csv"), header=True)

    print("Analyses générées dans data/analytics/")
    spark.stop()

if __name__ == "__main__":
    main()
