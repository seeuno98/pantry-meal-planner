"""Spark ETL for enriching recipe data with normalized ingredients and macros."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import List

from pyspark.sql import DataFrame, SparkSession, functions as F, types as T

from src.utils.text import normalize_ingredient_list, normalize_token


def _normalize_ingredients(values: List[str]) -> List[str]:
    if not values:
        return []
    str_values = [str(v) for v in values]
    return normalize_ingredient_list(str_values)


def _normalize_single(value: str) -> str:
    if not value:
        return ""
    return normalize_token(str(value))


normalize_ingredients_udf = F.udf(_normalize_ingredients, T.ArrayType(T.StringType()))
normalize_single_udf = F.udf(_normalize_single, T.StringType())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enrich recipe data for retrieval.")
    parser.add_argument("--recipes", required=True, help="Path to recipes_sample.json")
    parser.add_argument("--usda", required=True, help="Path to USDA lookup CSV")
    parser.add_argument(
        "--out", required=True, help="Output directory for processed data"
    )
    return parser.parse_args()


def build_spark() -> SparkSession:
    return (
        SparkSession.builder.appName("pantry_meal_planner_recipes_etl")
        .master("local[*]")
        .getOrCreate()
    )


def _write_single_file(df: DataFrame, destination: Path, fmt: str) -> None:
    tmp_dir = destination.parent / f".tmp_{destination.stem}_{fmt}"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    if fmt == "parquet":
        df.coalesce(1).write.mode("overwrite").parquet(str(tmp_dir))
    elif fmt == "json":
        df.coalesce(1).write.mode("overwrite").json(str(tmp_dir))
    else:
        raise ValueError(f"Unsupported format {fmt}")
    part_files = list(tmp_dir.glob("part-*"))
    if not part_files:
        raise FileNotFoundError(f"No part files created under {tmp_dir}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        destination.unlink()
    part_files[0].rename(destination)
    shutil.rmtree(tmp_dir)


def _collect_to_json(df: DataFrame, destination: Path) -> None:
    records = [row.asDict(recursive=True) for row in df.collect()]
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)


def run_etl(recipes_path: str, usda_path: str, output_dir: str) -> None:
    spark = build_spark()
    try:
        recipes_df = (
            spark.read.option("multiline", True)
            .json(recipes_path)
            .withColumn("id", F.col("id"))
            .withColumn("title", F.coalesce(F.col("title"), F.lit("Untitled Recipe")))
            .withColumn(
                "ingredients_norm", normalize_ingredients_udf(F.col("ingredients"))
            )
            .withColumn(
                "primary_ingredient", F.element_at(F.col("ingredients_norm"), 1)
            )
            .withColumn("est_kcal", F.col("est_kcal").cast(T.IntegerType()))
            .withColumn("est_protein_g", F.col("est_protein_g").cast(T.IntegerType()))
        )

        usda_schema = T.StructType(
            [
                T.StructField("ingredient", T.StringType(), False),
                T.StructField("kcal_per_100g", T.DoubleType(), False),
                T.StructField("protein_g_per_100g", T.DoubleType(), False),
            ]
        )
        usda_df = (
            spark.read.option("header", True)
            .schema(usda_schema)
            .csv(usda_path)
            .withColumn("ingredient_norm", normalize_single_udf(F.col("ingredient")))
        )

        enriched = (
            recipes_df.join(
                usda_df,
                on=recipes_df.primary_ingredient == usda_df.ingredient_norm,
                how="left",
            )
            .withColumn(
                "est_kcal",
                F.coalesce(
                    F.col("est_kcal"),
                    F.round(F.col("kcal_per_100g")).cast(T.IntegerType()),
                ),
            )
            .withColumn(
                "est_protein_g",
                F.coalesce(
                    F.col("est_protein_g"),
                    F.round(F.col("protein_g_per_100g")).cast(T.IntegerType()),
                ),
            )
            .drop(
                "kcal_per_100g", "protein_g_per_100g", "ingredient", "ingredient_norm"
            )
        )

        final_df = enriched.select(
            F.col("id"),
            F.col("title"),
            F.col("ingredients"),
            F.col("instructions"),
            F.col("ingredients_norm"),
            F.col("est_kcal"),
            F.col("est_protein_g"),
        )

        out_dir = Path(output_dir)
        parquet_path = out_dir / "recipes_enriched.parquet"
        json_path = out_dir / "recipes_enriched.json"

        _write_single_file(final_df, parquet_path, "parquet")
        _collect_to_json(final_df, json_path)
    finally:
        spark.stop()


def main() -> None:
    args = parse_args()
    run_etl(args.recipes, args.usda, args.out)


if __name__ == "__main__":
    main()
