from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("etl_usda").getOrCreate()
usda = (spark.read.option("header","true").csv("data/raw/usda/*.csv")
    .select(
        F.col("fdc_id").cast("long").alias("fdc_id"),
        F.lower(F.col("description")).alias("name"),
        F.col("calories").cast("double"),
        F.col("protein_g").cast("double"),
        F.col("fat_g").cast("double"),
        F.col("carbs_g").cast("double")
    ).dropna(subset=["name"]))
usda.write.mode("overwrite").parquet("data/processed/usda_lookup/")
print("Wrote USDA lookup to data/processed/usda_lookup")
