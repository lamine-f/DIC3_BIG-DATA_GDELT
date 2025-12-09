from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

spark = SparkSession.builder \
    .appName("GDELTEventCounter") \
    .master("spark://spark-master:7077") \
    .getOrCreate()

data_path = "/data/20251208.export.CSV"

output_path = "/output/event_counts_by_country"

print("=" * 60)
print("GDELT Event Counter - Comptage des événements par pays")
print("=" * 60)

try:
    print(f"\nLecture des données depuis: {data_path}")
    df = spark.read.csv(
        data_path,
        sep='\t',
        header=False,
        inferSchema=True
    )

    total_events = df.count()
    print(f"Nombre total d'événements chargés: {total_events}")

    COUNTRY_CODE_COL_INDEX = 50
    country_df = df.withColumnRenamed(f"_c{COUNTRY_CODE_COL_INDEX}", "CountryCode")

    filtered_df = country_df.filter(
        col("CountryCode").isNotNull() & (col("CountryCode") != "")
    )

    event_counts = filtered_df.groupBy("CountryCode") \
        .agg(count("*").alias("EventCount")) \
        .orderBy(col("EventCount").desc())

    print("\n" + "=" * 60)
    print("TOP 30 des pays par nombre d'événements:")
    print("=" * 60)
    event_counts.show(30, truncate=False)

    print(f"\nSauvegarde des résultats vers: {output_path}")
    event_counts.coalesce(1).write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(output_path)

    print("Sauvegarde terminée avec succès!")
    print("=" * 60)

except Exception as e:
    print(f"ERREUR lors du traitement: {e}")
    import traceback
    traceback.print_exc()

spark.stop()