import json
from pyspark.sql.functions import col, count, desc, when, lit
from spark_common import create_spark_session, PROCESSED_DIR, ANALYTICS_DIR, ensure_dirs

def rows_to_dicts(rows):
    return [row.asDict(recursive=True) for row in rows]

def main():
    ensure_dirs()
    spark = create_spark_session("SmartLibraryExportDashboard")

    books = spark.read.parquet(str(PROCESSED_DIR / "books_enriched.parquet"))
    ratings = spark.read.parquet(str(PROCESSED_DIR / "ratings_clean.parquet"))
    to_read = spark.read.parquet(str(PROCESSED_DIR / "to_read_clean.parquet"))
    tag_usage = spark.read.parquet(str(PROCESSED_DIR / "tag_usage.parquet"))
    user_profiles = spark.read.parquet(str(PROCESSED_DIR / "user_profiles.parquet"))

    popularity = books.withColumn(
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
)

    summary = {
        "total_books": books.count(),
        "total_ratings": ratings.count(),
        "total_users": ratings.select("user_id").distinct().count(),
        "total_to_read": to_read.count(),
        "total_tags_used": tag_usage.count(),
        "top_books": rows_to_dicts(
            books.select("book_id", "title", "authors", "rating_count", "avg_user_rating", "to_read_count")
            .orderBy(desc("rating_count"))
            .limit(10)
            .collect()
        ),
        "top_tags": rows_to_dicts(
            tag_usage.select("tag_name", "usage_count")
            .orderBy(desc("usage_count"))
            .limit(10)
            .collect()
        ),
        "rating_distribution": rows_to_dicts(
            ratings.groupBy("rating").agg(count("*").alias("count")).orderBy("rating").collect()
        ),
        "user_activity": rows_to_dicts(
            user_profiles.orderBy(desc("ratings_given")).limit(10).collect()
        ),
        "popularity_levels": rows_to_dicts(
            popularity.groupBy("popularity_level").agg(count("*").alias("count")).collect()
        )
    }

    output = ANALYTICS_DIR / "dashboard_summary.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"Dashboard exporté : {output}")
    spark.stop()

if __name__ == "__main__":
    main()
