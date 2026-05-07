import polars as pl
from pathlib import Path
from itertools import product, combinations

# Load CSV
GSHEET_CSV = Path("gjgex_dataset.csv")
jgex_dataset = pl.read_csv(GSHEET_CSV)

if "" in jgex_dataset.columns:
    jgex_dataset = jgex_dataset.rename({"": "name"})

# --------------------------------------------------
# Normalize polygon tokens -> "polygon"
# --------------------------------------------------
POLYGON_TOKENS = {"triangle", "quadrilateral", "square", "pentagon", "hexagon", "trapezoid"}

# --------------------------------------------------
# Co-occurrence rules: bisector requires line, polygon requires segment
# --------------------------------------------------
REQUIRED_CO_OCCURRENCE = [
    ("bisector", "line"),
    ("polygon", "segment"),
]

def is_valid_combination(toks):
    s = set(toks)
    for a, b in REQUIRED_CO_OCCURRENCE:
        if a in s and b not in s:
            return False
    return True

# --------------------------------------------------
# 1) Observed construction frequencies
# --------------------------------------------------
construction_freqs = (
    jgex_dataset
    .select("NL_construction_in_statement", "numerical_concept")
    .filter(pl.col("NL_construction_in_statement").is_not_null())
    .filter(pl.col("NL_construction_in_statement").str.strip_chars() != "")
    .with_columns(
        tokens=(
            pl.col("NL_construction_in_statement")
            .str.replace_all(r"[()\d,]", "")
            .str.to_lowercase()
            .str.split(" ")
            .list.eval(pl.element().filter(pl.element() != ""))
        )
    )
    .with_columns(
        tokens=pl.col("tokens").map_elements(
            lambda toks: sorted(set(
                ("polygon" if t in POLYGON_TOKENS else t)
                for t in toks
                if t and t != "none" and t != "point"
            )),
            return_dtype=pl.List(pl.Utf8),
        )
    )
    .with_columns(constructions=pl.col("tokens").list.join(","))
    .filter(pl.col("constructions") != "")
    .drop(["NL_construction_in_statement", "tokens"])
    .group_by("numerical_concept", "constructions")
    .len(name="count")
    .sort(["count", "constructions"], descending=[True, False])
)

# --------------------------------------------------
# 2) Build the universe of construction tokens
# --------------------------------------------------
concepts = ["yes", "no"]

construction_components = [
    x for x in (
        construction_freqs["constructions"]
        .str.split(",")
        .explode()
        .unique()
        .to_list()
    )
    if x not in ("", "none", "point")
]

# --------------------------------------------------
# 3) Generate all valid combinations
# --------------------------------------------------
combs = [
    {
        "numerical_concept": concept,
        "constructions": ",".join(sorted(tokens)),
    }
    for r in range(1, len(construction_components) + 1)
    for concept, tokens in product(concepts, combinations(construction_components, r))
    if is_valid_combination(list(tokens))
]

combs_df = pl.from_dicts(combs)

# --------------------------------------------------
# 4) Fill missing combos with count=0
# --------------------------------------------------
final = (
    pl.concat(
        [
            combs_df.with_columns(count=pl.lit(0, dtype=pl.UInt32)),
            construction_freqs,
        ]
    )
    .group_by("numerical_concept", "constructions")
    .agg(pl.all().sort_by("count").last())
    .sort(["count", "constructions"], descending=[True, False])
)

# --------------------------------------------------
# 5) Coverage summary
# --------------------------------------------------
summary = final.select(
    pl.len().alias("possible"),
    (pl.col("count") > 0).sum().alias("observed"),
    ((pl.col("count") > 0).sum() / pl.len()).alias("fill_ratio"),
)

print(summary)

final.write_csv("construction_coverage.csv")
print("Wrote construction_coverage.csv")
