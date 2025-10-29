from pyspark.sql import SparkSession, functions as F, types as T
spark = SparkSession.builder.appName("etl_recipes").getOrCreate()
df = spark.read.json("data/raw/recipes/*.json")
to_arr = F.udf(lambda x: x if isinstance(x, list) else [], T.ArrayType(T.StringType()))
clean = (df
    .withColumn("recipe_id", F.coalesce(F.col("id"), F.monotonically_increasing_id()))
    .withColumn("title", F.coalesce(F.col("title"), F.lit("")))
    .withColumn("ingredients", to_arr(F.col("ingredients")))
    .withColumn("instructions", F.coalesce(F.col("instructions"), F.lit("")))
    .withColumn("time_minutes", F.coalesce(F.col("time_minutes"), F.lit(30)))
    .select("recipe_id","title","ingredients","instructions","time_minutes")
    .dropDuplicates(["title"]))
clean.write.mode("overwrite").parquet("data/processed/recipes/")
print("Wrote recipes to data/processed/recipes")
