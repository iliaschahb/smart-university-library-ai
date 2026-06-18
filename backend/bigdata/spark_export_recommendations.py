import json
from pyspark.sql import Window
from pyspark.sql.functions import col, desc, row_number, collect_list, struct, when, lit
from spark_common import create_spark_session, PROCESSED_DIR, ANALYTICS_DIR, ensure_dirs


def main():
    ensure_dirs()
    spark = create_spark_session("SmartLibraryRecommendationExport")

    books = spark.read.parquet(str(PROCESSED_DIR / "books_enriched.parquet"))
    tags = spark.read.parquet(str(PROCESSED_DIR / "tags_clean.parquet"))
    book_tags = spark.read.parquet(str(PROCESSED_DIR / "book_tags_clean.parquet"))

    catalog = books.withColumn(
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
        col("book_id").cast("int").alias("book_id"),
        col("goodreads_book_id").cast("double").alias("goodreads_book_id"),
        col("title").cast("string").alias("title"),
        col("authors").cast("string").alias("authors"),
        col("goodreads_average_rating").cast("double").alias("goodreads_average_rating"),
        col("goodreads_ratings_count").cast("double").alias("goodreads_ratings_count"),
        col("rating_count").cast("int").alias("rating_count"),
        col("avg_user_rating").cast("double").alias("avg_user_rating"),
        col("to_read_count").cast("int").alias("to_read_count"),
        col("tag_count").cast("int").alias("tag_count"),
        col("popularity_score").cast("double").alias("popularity_score"),
        col("popularity_level").cast("string").alias("popularity_level")
    )

    tag_join = (
        book_tags.alias("bt")
        .join(tags.alias("t"), col("bt.tag_id") == col("t.tag_id"), "left")
        .join(catalog.select("book_id", "goodreads_book_id").alias("b"), col("bt.goodreads_book_id") == col("b.goodreads_book_id"), "inner")
        .select(
            col("b.book_id"),
            col("t.tag_name"),
            col("bt.count").alias("tag_weight")
        )
        .filter(col("tag_name").isNotNull())
    )

    window = Window.partitionBy("book_id").orderBy(desc("tag_weight"))
    top_tags = (
        tag_join.withColumn("rn", row_number().over(window))
        .filter(col("rn") <= 8)
        .groupBy("book_id")
        .agg(collect_list(struct("tag_name", "tag_weight")).alias("tags"))
    )

    catalog_with_tags = (
        catalog.alias("c")
        .join(top_tags.alias("tt"), col("c.book_id") == col("tt.book_id"), "left")
        .select(
            col("c.book_id"),
            col("c.goodreads_book_id"),
            col("c.title"),
            col("c.authors"),
            col("c.goodreads_average_rating"),
            col("c.goodreads_ratings_count"),
            col("c.rating_count"),
            col("c.avg_user_rating"),
            col("c.to_read_count"),
            col("c.tag_count"),
            col("c.popularity_score"),
            col("c.popularity_level"),
            col("tt.tags")
        )
    )

    catalog_json = []
    for row in catalog_with_tags.collect():
        item = row.asDict(recursive=True)
        item["tags"] = item.get("tags") or []
        catalog_json.append(item)

    output_file = ANALYTICS_DIR / "recommendation_catalog.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(catalog_json, f, ensure_ascii=False, indent=2)

    print(f"Catalogue de recommandation exporté : {output_file}")
    print(f"Nombre de livres exportés : {len(catalog_json)}")
    spark.stop()


if __name__ == "__main__":
    main()
