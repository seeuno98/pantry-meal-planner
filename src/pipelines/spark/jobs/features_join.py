from pyspark.sql import SparkSession, functions as F
spark = SparkSession.builder.appName("features_join").getOrCreate()
recipes = spark.read.parquet("data/processed/recipes/")
usda = spark.read.parquet("data/processed/usda_lookup/")

# naive join: ingredient string contains usda name
expl = recipes.withColumn("ingredient", F.explode_outer("ingredients")).withColumn("ingredient", F.lower(F.col("ingredient")))
joined = (expl.crossJoin(usda)
    .where(F.locate(usda.name, F.col("ingredient")) > 0)
    .groupBy("recipe_id")
    .agg(
        F.first("title").alias("title"),
        F.first("time_minutes").alias("time_minutes"),
        F.collect_set("ingredient").alias("ingredients"),
        F.sum("calories").alias("calories_est"),
        F.sum("protein_g").alias("protein_est_g"),
        F.sum("fat_g").alias("fat_est_g"),
        F.sum("carbs_g").alias("carbs_est_g")
    ))
joined.write.mode("overwrite").parquet("data/processed/recipes_enriched/")
print("Wrote enriched recipes to data/processed/recipes_enriched")
