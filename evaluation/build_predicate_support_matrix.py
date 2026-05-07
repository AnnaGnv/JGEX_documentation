try:
    import newclid
except ImportError:
    !pip install -q "newclid>=3" "py-yuclid"

import os
import re
import sys
import shutil
import tempfile
import subprocess
from dataclasses import dataclass, asdict
from typing import Literal

import pandas as pd

Status = Literal["OK", "FAIL", "SKIP"]

# -----------------------------
# Cases (fill with ALL predicates)
# -----------------------------
cases = [
    {"predicate": "diff", "jgex": "a b c = triangle a b c ? diff a b; diff a c; diff b c"},
    {"predicate": "midp", "jgex": "a = free a; b = free b; c = free c; e = midpoint e a b; f = midpoint f a c ? para e f b c"},
    {"predicate": "coll", "jgex": "a = free a; b = free b; c = on_pline0 c a b a ? coll a b c"},
    {"predicate": "ncoll", "jgex": "a b = segment a b; c = free c ? ncoll a b c"},
    {"predicate": "perp", "jgex": "a b = segment a b; c = on_tline c a a b ? perp a b a c"},
    {"predicate": "nperp", "jgex": "a b = segment a b; c d = segment c d ? nperp a b c d"},
    {"predicate": "para", "jgex": "a b c = triangle a b c; d = on_pline d c a b ? para a b c d"},
    {"predicate": "npara", "jgex": "a b = segment a b; c d = segment c d ? npara a b c d"},
    {"predicate": "circle", "jgex": "o a = segment o a; b = eqdistance b o o a; c = eqdistance c o o b ? circle o a b c"},
    {"predicate": "cyclic", "jgex": "a b c = triangle a b c; o = circle o a b c; d = on_circle d o a ? cyclic a b c d"},
    {"predicate": "aconst", "jgex": "a b = segment a b; c = on_circle c a b, on_circle c b a ? aconst a b a c 1/3"},
    {"predicate": "acompute", "jgex": "a = free a; b = lconst b a 4; c = eq_triangle c a b ? acompute b a b c; acompute a b b c"},
    {"predicate": "obtuse_angle", "jgex": "a c = segment a c; b = midpoint b a c ? obtuse_angle a b c"},
    {"predicate": "eqangle", "jgex": "a = free a; b = free b; p = free p; q = on_circum q a b p ? eqangle p a p b q a q b"},
    {"predicate": "lconst", "jgex": "a = free a; b = lconst b a 2 ? lconst a b 2"},
    {"predicate": "lcompute", "jgex": "a = free a; b = lconst b a 5 ? lcompute a b"},

    # l2const numeric variant will be tried automatically (see l2const_variants)
    {"predicate": "l2const", "jgex": "a = free a; b = lconst b a 2 ? l2const a b {VAL}"},

    {"predicate": "cong", "jgex": "a = free a; b = free b; c = free c; p = on_circum p a b c; r = on_circum r a b c; q = on_circum q a b c, on_aline q r p b c a ? cong a b p q"},
    {"predicate": "rconst", "jgex": "a b = segment a b; m = midpoint m a b ? rconst m a a b 1/2"},

    # You can add r2const/eqratio/simtri/... here with your known-working snippets.
    {"predicate": "lequation", "jgex": "c a b = between c a b ? lequation 1/1 a c 1/1 c b -1/1 a b 0/1"},
    {"predicate": "aequation", "jgex": "a b c = triangle a b c; o = circle o a b c ? aequation 1/1 a b b c 1/1 a c a o 90o"},
]

l2const_variants = ["4", "4/1", "4.0"]  # try these; doc suggests float-like

# -----------------------------
# Result schema
# -----------------------------
@dataclass
class Row:
    predicate: str
    yuclid_status: Status
    newclid_only_status: Status
    failure_mode: str
    short_error: str
    jgex_used: str  # store final concrete JGEX used (after {VAL} substitution)

def shorten(s: str, n: int = 220) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "..."

# -----------------------------
# Yuclid runner
# -----------------------------
def run_yuclid(problem_string: str) -> tuple[Status, str, str]:
    yuclid_bin = shutil.which("yuclid")
    if yuclid_bin is None:
        return "SKIP", "Y0_NO_YUCLID", "yuclid CLI not found"

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "case.jgex")
        with open(path, "w", encoding="utf-8") as f:
            f.write(problem_string)

        cmd = [yuclid_bin, "--err-on-failure", "--input-file", path, "--log-level", "warning"]
        p = subprocess.run(cmd, capture_output=True, text=True)
        out = (p.stdout or "") + "\n" + (p.stderr or "")

        if p.returncode == 0:
            return "OK", "", ""

        m = re.search(r"Unknown statement\s+([A-Za-z_][A-Za-z0-9_]*)", out)
        if m:
            return "FAIL", "Y1_UNKNOWN_STATEMENT", f"Unknown statement {m.group(1)}"
        return "FAIL", "Y2_YUCLID_FAILED", shorten(out, 240)

# -----------------------------
# Newclid-only runner in fresh subprocess
# -----------------------------
NEWCLID_SUBPROCESS = r"""
import sys
import numpy as np
from newclid.jgex.problem_builder import JGEXProblemBuilder
from newclid.api import GeometricSolverBuilder

name = sys.argv[1]
jgex = sys.argv[2]
rng = np.random.default_rng(0)

try:
    builder = (
        JGEXProblemBuilder(rng=rng)
        .include_auxiliary_clauses(True)
        .with_problem_from_txt(problem_txt=jgex, problem_name=name)
    )
    setup = builder.build()
    solver = GeometricSolverBuilder(rng=rng).build(setup)
    solver.run()
    print("OK")
except Exception as e:
    print(f"FAIL::{type(e).__name__}::{e}")
    raise
"""

def classify_newclid_out(out: str) -> tuple[Status, str, str]:
    if "OK" in out and "FAIL::" not in out:
        return "OK", "", ""

    m = re.search(r"FAIL::([A-Za-z0-9_]+)::(.*)", out)
    if not m:
        return "FAIL", "E_UNKNOWN", shorten(out, 240)

    etype, emsg = m.group(1), m.group(2)

    if etype == "NotImplementedError":
        if "LengthEquationPredicate" in emsg:
            return "FAIL", "N1_NOT_IMPLEMENTED_LENGTH_EQUATION", shorten(f"{etype}: {emsg}")
        if "AngleEquationPredicate" in emsg:
            return "FAIL", "N1_NOT_IMPLEMENTED_ANGLE_EQUATION", shorten(f"{etype}: {emsg}")
        return "FAIL", "N1_NOT_IMPLEMENTED", shorten(f"{etype}: {emsg}")

    if "Cannot justify predicate" in emsg and "through AR" in emsg:
        return "FAIL", "P1_AR_LIMITATION", shorten(f"{etype}: {emsg}")

    if etype == "TypeError" and "cannot unpack non-iterable" in emsg:
        return "FAIL", "N2_RUNTIME_BUG", shorten(f"{etype}: {emsg}")

    return "FAIL", "E_UNKNOWN", shorten(f"{etype}: {emsg}")

def run_newclid_only_case(case_id: str, jgex: str) -> tuple[Status, str, str]:
    p = subprocess.run([sys.executable, "-c", NEWCLID_SUBPROCESS, case_id, jgex], capture_output=True, text=True)
    out = (p.stdout or "") + "\n" + (p.stderr or "")
    return classify_newclid_out(out)

def pip_uninstall_py_yuclid():
    subprocess.run([sys.executable, "-m", "pip", "uninstall", "-y", "py-yuclid"], check=False, capture_output=True, text=True)

def pip_install_py_yuclid():
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "py-yuclid"], check=False, capture_output=True, text=True)

# -----------------------------
# Main
# -----------------------------
rows: list[Row] = []

# Phase A: Yuclid support
for i, c in enumerate(cases):
    pred = c["predicate"]
    if pred == "l2const":
        # just test one representative value for Yuclid (use float-like)
        jgex_used = c["jgex"].replace("{VAL}", "4.0")
    else:
        jgex_used = c["jgex"]

    st, mode, err = run_yuclid(jgex_used)
    rows.append(
        Row(
            predicate=pred,
            yuclid_status=st,
            newclid_only_status="SKIP",
            failure_mode=mode if st == "FAIL" else "",
            short_error=err if st == "FAIL" else "",
            jgex_used=jgex_used,
        )
    )

# Phase B: Newclid-only support (simulate by uninstalling py-yuclid)
pip_uninstall_py_yuclid()

for i, c in enumerate(cases):
    pred = c["predicate"]
    base_case_id = f"case_{i:03d}_{pred}"

    if pred == "l2const":
        # try multiple formats; keep the first that works
        best = None
        for val in l2const_variants:
            jgex_used = c["jgex"].replace("{VAL}", val)
            st, mode, err = run_newclid_only_case(base_case_id + f"_val_{val}", jgex_used)
            if st == "OK":
                best = (st, "", "", jgex_used)
                break
            best = (st, mode, err, jgex_used)
        st, mode, err, jgex_used = best
    else:
        jgex_used = c["jgex"]
        st, mode, err = run_newclid_only_case(base_case_id, jgex_used)

    rows[i].newclid_only_status = st
    rows[i].jgex_used = jgex_used

    # prefer Newclid-only failure if Newclid fails
    if st == "FAIL":
        rows[i].failure_mode = mode
        rows[i].short_error = err

# optional reinstall (so your notebook keeps working with Yuclid)
pip_install_py_yuclid()

df = pd.DataFrame([asdict(r) for r in rows])

# Export CSV with concrete JGEX used
df.to_csv("predicate_support_matrix.csv", index=False)

# Export LaTeX annex table WITHOUT JGEX
df_latex = df.drop(columns=["jgex_used"])
latex = df_latex.to_latex(index=False, longtable=True, escape=False)
with open("predicate_support_matrix.tex", "w", encoding="utf-8") as f:
    f.write(latex)

df_latex
