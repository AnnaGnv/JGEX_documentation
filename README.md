# A JGEX Dataset

A curated collection of 137 Euclidean geometry problems with released JGEX formalizations and run-status annotations under pinned Newclid v3.0.1.


## Dataset

**File:** `data/dataset.csv` — one row = one JGEX instance.

Each row pairs:

1. the **original natural-language** problem statement (LaTeX),
2. a **JGEX-oriented rewrite** (LaTeX) that makes construction steps explicit,
3. the **executable JGEX code** (construction sequence + goal),
4. metadata for filtering, benchmarking, and analysis.

### Column schema

| Column | Description |
|---|---|
| `problem_id` | Integer identifier. Repeats across rows when one problem is encoded as multiple JGEX instances (e.g., multi-goal encodings). |
| `original_NL_problem_statement` | Original problem statement in LaTeX (verbatim from source). |
| `statement_source` | Source citation (contest/year/problem number, or textbook/exercise reference). |
| `NL-JGEX_problem_statement` | LaTeX rewrite aligned to JGEX construction order; makes implicit assumptions explicit. |
| `JGEX_problem_statement` | Executable JGEX instance: constructions (`;`-separated), optional helper constructions after `\|`, goal(s) after `?`. |
| `problem_runs_on_Newclid_3_0_1` | Execution flag under Newclid v3.0.1 (`yes`/`no`). |
| `NL_reference_proof` | Reference proof identifier or link when available; otherwise `N/A`. |
| `NL_reference_proof_source` | Source for the reference proof (URL or citation); otherwise `N/A`. |
| `numerical_concept` | Whether the instance uses explicit numerical content (fixed angles/ratios/lengths) vs. purely qualitative relations. |
| `NL_construction_in_statement` | Counts of primitives needed to state the configuration (e.g., `point(7), segment(6), circle(1)`). |
| `NL_construction_for_proof` | Counts of auxiliary primitives introduced to enable the proof strategy; otherwise `N/A`. |
| `final_answer` | Machine-matchable answer token when applicable; typically `N/A` for theorem-style problems. |
| `comment` | Free-form notes on goal reformulations, helper constructions, multi-goal encodings, or caveats. |


### Quickstart

```python
import pandas as pd

df = pd.read_csv("data/dataset.csv")
print(df.columns.tolist())
print(df.head(3)[["problem_id", "statement_source", "JGEX_problem_statement"]])
```

---

## Predicate support

`data/predicate_support_matrix.csv` reports the support status of all 33 documented JGEX predicates under Newclid v3.0.1:

- **Supported (25):** runs end-to-end without errors.
- **Unsupported (5):** fails at build or runtime (e.g., `lequation`, `aequation`).
- **Unstable (3):** no accessible minimal example found; behavior cannot be reliably evaluated.

To regenerate the matrix from scratch:

```bash
python evaluation/generate_predicate_matrix.py
```

---

## NL→JGEX pipeline

`pipeline/pipeline.py` implements the LLM-assisted formalization pipeline from Section 4 of the paper: given a natural-language geometry statement, it proposes a JGEX encoding and validates it by executing Newclid.

```bash
python pipeline/pipeline.py --input data/dataset.csv --output results.csv
```

The predicate/constructor reference card injected into each prompt is in `pipeline/reference_card.py` and can be audited or updated independently.

---

## Pinned solver version

All executability results in this repository are tied to **Newclid v3.0.1**. 
