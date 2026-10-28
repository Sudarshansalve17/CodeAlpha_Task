"""Analyze the scraped quotes dataset: top tags, quotes per author, quote length."""

import argparse
from pathlib import Path

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize data/quotes.csv")
    parser.add_argument("--input", type=Path, default=Path("data/quotes.csv"))
    parser.add_argument("--outdir", type=Path, default=Path("data"))
    args = parser.parse_args()

    df = pd.read_csv(args.input, encoding="utf-8-sig").fillna("")
    args.outdir.mkdir(parents=True, exist_ok=True)

    print(f"Dataset: {len(df)} quotes, {df['author'].nunique()} authors\n")

    # 1. Top 10 tags (tags are stored as 'a;b;c' in one column)
    tags = (
        df["tags"].str.split(";").explode().str.strip().replace("", pd.NA).dropna()
    )
    top_tags = tags.value_counts().head(10).rename_axis("tag").reset_index(name="count")
    print("Top 10 tags:")
    print(top_tags.to_string(index=False), "\n")

    # 2. Quotes per author (top 10)
    per_author = (
        df["author"].value_counts().head(10).rename_axis("author").reset_index(name="quotes")
    )
    print("Top 10 authors by number of quotes:")
    print(per_author.to_string(index=False), "\n")

    # 3. Quote length statistics (words)
    df["word_count"] = df["quote"].str.split().str.len()
    print("Quote length (words):")
    print(df["word_count"].describe().round(1).to_string(), "\n")

    longest = df.loc[df["word_count"].idxmax()]
    print(f"Longest quote ({longest['word_count']} words) by {longest['author']}")

    # Save summaries so they can be included in the report
    top_tags.to_csv(args.outdir / "top_tags.csv", index=False)
    per_author.to_csv(args.outdir / "quotes_per_author.csv", index=False)
    print(f"\nSaved summaries to {args.outdir}")


if __name__ == "__main__":
    main()
