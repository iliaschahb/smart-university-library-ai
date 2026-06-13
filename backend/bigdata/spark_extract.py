import json
from spark_common import create_spark_session, RAW_DIR, ANALYTICS_DIR, ensure_dirs, check_raw_files

def main():
    ensure_dirs()
    check_raw_files()
    spark = create_spark_session("SmartLibraryExtract")

    files = {
        "books": RAW_DIR / "books.csv",
        "ratings": RAW_DIR / "ratings.csv",
        "tags": RAW_DIR / "tags.csv",
        "book_tags": RAW_DIR / "book_tags.csv",
        "to_read": RAW_DIR / "to_read.csv",
    }

    metadata = {}
    for name, path in files.items():
        df = spark.read.csv(str(path), header=True, inferSchema=True)
        metadata[name] = {
            "file": str(path),
            "rows": df.count(),
            "columns": df.columns,
        }
        print(f"\n=== {name.upper()} ===")
        print("Rows:", metadata[name]["rows"])
        print("Columns:", metadata[name]["columns"])
        df.show(5, truncate=False)

    output = ANALYTICS_DIR / "extract_metadata.json"
    with open(output, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\nExtraction terminée. Métadonnées exportées : {output}")
    spark.stop()

if __name__ == "__main__":
    main()
