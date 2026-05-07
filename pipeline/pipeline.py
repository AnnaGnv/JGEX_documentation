import numpy as np
import openai
import json
import csv
from pathlib import Path
from google.colab import userdata

from newclid.api import GeometricSolverBuilder
from newclid.jgex.problem_builder import JGEXProblemBuilder

# Load examples from uploaded file
import importlib.util, sys
spec = importlib.util.spec_from_file_location("examples_20", "/content/examples_20.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
EXAMPLES = mod.EXAMPLES

print(f"Loaded {len(EXAMPLES)} in-context examples")

client = openai.OpenAI(
    api_key=userdata.get('OPENROUTER_API_KEY'),
    base_url="https://openrouter.ai/api/v1"
)

MODEL = "openai/gpt-5.4-pro"

def build_prompt(nl_problem, examples, previous_attempt=None, error_message=None, k=20):
    """
    Build a prompt for NL -> JGEX translation with:
    - a compact but complete vocabulary card (definitions + predicates)
    - strict syntax/arity rules
    - up to k in-context examples (caller should ideally pass retrieved examples)
    """

    # Use at most k examples (assumes caller may already have done retrieval)
    exs = examples[:k] if (k is not None and len(examples) > k) else examples

    JGEX_REFERENCE_CARD = r"""
You are a geometry formalization expert for Newclid JGEX.
Return ONLY a valid JGEX program string (no explanation, no markdown, no backticks).

=== JGEX CORE SYNTAX ===
- Constructions are separated by ';'
- A construction line looks like:   <lhs> = <definition> <args>
- A point can satisfy multiple constraints by separating definitions with ',' meaning AND:
    x = on_line x a b, on_circle x o a
- Optional helper constructions come after '|' and before the goal:
    ... ; | <helper constructions> ? <single goal predicate>
- Exactly ONE goal predicate after '?'. (Do NOT output multiple goals separated by ';')

CRITICAL TOKEN POLICY:
- Use ONLY the exact predicate/definition tokens listed below.
- Do NOT invent aliases (e.g., 'ncollinear' is invalid; use 'ncoll').

ARITY / SIGNATURE PITFALLS:
- coll takes >= 3 points:   coll a b c ...
- cyclic takes >= 4 points: cyclic a b c d ...
- diff takes >= 2 points:   diff a b c ...
- perp / para / cong take exactly 4 points.
- eqangle takes exactly 8 points.
- eqratio takes exactly 8 points.
- eqangle is directed-angle equality modulo 180° (i.e., mod pi), not 360°.

COMMON CONFUSION:
- 'on_circle' is a DEFINITION (constructor). 'circle o a b c' is a PREDICATE.
- 'circle x a b c' also exists as a DEFINITION (constructor) that *builds* the circumcenter point.
  (Yes, token collision. Follow the signatures.)

=== GOAL PREDICATES (after '?') ===
Incidence / orientation:
  diff a b c...                  -- all listed points are distinct
  coll a b c...                  -- all listed points are collinear (>=3)
  ncoll a b c...                 -- NOT all collinear (>=3)
  midp m a b                     -- m is midpoint of segment ab
  obtuse_angle a b c             -- angle abc obtuse; for collinear a,b,c encodes betweenness

Parallel / perpendicular:
  perp a b c d                   -- line ab ⟂ line cd
  nperp a b c d                  -- not perpendicular
  para a b c d                   -- line ab ∥ line cd
  npara a b c d                  -- not parallel

Circles:
  circle o a b c                 -- o is center of circle through a,b,c
  cyclic a b c d...              -- concyclic (>=4)

Angles / lengths / ratios:
  eqangle a b c d e f g h         -- angle(ab,cd) = angle(ef,gh) mod 180°
  aconst a b c d r                -- directed angle from line ab to line cd equals r (e.g. 60o, 2pi/3)
  cong a b c d                    -- |ab| = |cd|
  lconst a b l                    -- |ab| = l  (l is numeric)
  l2const a b l                   -- |ab|^2 = l
  rconst a b c d r                -- |ab|/|cd| = r  (r is fraction m/n)
  r2const a b c d r               -- |ab|^2/|cd|^2 = r
  eqratio a b c d e f g h         -- |ab|/|cd| = |ef|/|gh|

Similarity / congruence:
  simtri a b c p q r              -- triangles abc and pqr similar (orientation-preserving)
  simtrir a b c p q r             -- similar with reflection (orientation-reversing)
  contri a b c p q r              -- congruent (orientation-preserving)
  contrir a b c p q r             -- congruent with reflection (orientation-reversing)

“Numerical/aux” predicates (still allowed as goals if supported):
  sameclock a b c x y z           -- orientations of (a,b,c) and (x,y,z) match
  sameside a b c x y z            -- same arc-type relation (as documented)
  nsameside a b c x y z           -- negation

Predicates documented but DO NOT USE here (unsupported/unstable in Newclid v3.0.1 in many setups):
  acompute ...
  lcompute ...
  rcompute ...
  pythagorean_premises ...
  pythagorean_conclusions ...
  lequation ...
  aequation ...

=== DEFINITIONS (CONSTRUCTORS) ===
BASIC (no-arg) shapes / points:
  segment a b
  triangle a b c
  quadrangle a b c d
  pentagon a b c d e
  trapezoid a b c d
  r_trapezoid a b c d
  iso_trapezoid a b c d
  rectangle a b c d
  isquare a b c d
  r_triangle a b c
  risos a b c
  iso_triangle a b c
  iso_triangle0 a b c
  ieq_triangle a b c
  eq_quadrangle a b c d
  eqdia_quadrangle a b c d
  acute_triangle a b c
  between c a b
  free a

Points from existing points:
  midpoint x a b
  mirror x a b
  reflect x a b c
  foot x a b c
  orthocenter x a b c
  incenter x a b c
  incenter2 x y z i a b c
  excenter x a b c
  excenter2 x y z i a b c
  centroid x y z i a b c
  ninepoints x y z i a b c
  parallelogram x a b c
  eq_triangle x b c
  shift x b c d
  nsquare x a b
  psquare x a b
  square x y a b

Points on lines / circles:
  on_line x a b
  on_circle x o a
  on_bline x a b
  on_pline x a b c                 -- requires a,b,c non-collinear
  on_pline0 x a b c                -- allows collinear a,b,c
  on_tline x a b c
  on_dia x a b
  on_circum x a b c
  lc_tangent x a o

Angle/ratio prescription (constructors):
  angle_bisector x a b c           -- x on internal bisector of angle abc (vertex b)
  angle_mirror x a b c
  on_aline x a b c d e             -- adds eqangle a x a b d c d e
  on_aline0 x a b c d e f g         -- adds eqangle a b c d e f g x
  eqangle2 x a b c
  eqangle3 x a b d e f
  eqdistance x a b c
  eqratio x a b c d e f g
  eqratio6 x a c e f g h
  rconst a b c x r
  rconst2 x a b r
  aconst a b c x r
  s_angle a b x y
  lconst x a l
  l2const x a l
  r2const a b c x r
  triangle12 a b c
  trisect x y a b c
  trisegment x y a b
  between_bound x a b
  iso_trapezoid2 x a b c

Intersections:
  intersection_ll x a b c d
  intersection_lc x a o b
  intersection_cc x o w a
  intersection_lp x a b c m n
  intersection_lt x a b c d e
  intersection_pp x a b c d e f
  intersection_tt x a b c d e f

Tangency / circle-circle tangents:
  tangent x y a o b
  cc_tangent x y z i o a w b
  cc_itangent x y z i o a w b
  2l1c x y z i a b c o

Opaque/special constructors (avoid unless needed; semantics are niche):
  e5128 ...
  3peq ...
  test_r20 ...
  test_r25 ...

=== MODELING TIPS ===
- Concurrency of three lines: build intersection of two lines, then prove third line passes through it using coll.
- “Point lies on angle bisector at A” can be encoded by eqangle (directed angles mod 180°).
- If Newclid complains about invalid predicate type or arity, fix token/argument count first.
"""

    examples_text = "\n\n".join(
        [f"NL: {ex['nl']}\nJGEX: {ex['jgex']}" for ex in exs]
    )

    system_msg = f"""You are a geometry formalization expert for the JGEX/Newclid system.
Given a natural-language geometry problem, produce a valid JGEX formalization that Newclid can build and run.
Respond with ONLY the JGEX string.

{JGEX_REFERENCE_CARD}

=== IN-CONTEXT EXAMPLES (NL -> JGEX) ===
{examples_text}
"""

    user_msg = f"Problem (NL): {nl_problem}"

    if previous_attempt and error_message:
        user_msg += f"""

Previous attempt (JGEX):
{previous_attempt}

Newclid error:
{error_message}

Fix the JGEX using ONLY allowed tokens/signatures from the reference card.
Common fixes:
- Unknown predicate/definition token -> replace with the exact allowed token (e.g., ncoll not ncollinear).
- Invalid construction/arity -> check argument counts (coll>=3, cyclic>=4, eqangle=8, eqratio=8, perp/para/cong=4).
- Builder degeneracy / 'Failed to build after 100 attempts' -> simplify constraints, avoid redundant intersections, avoid defining the same intersection twice, or change the construction order.
- Numerical instability / 'too far' -> avoid extreme intersection chains; prefer direct intersection_* constructors where possible.
"""

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]

def run_newclid(jgex_string, problem_name="tmp"):
    try:
        rng = np.random.default_rng(0)
        builder = (
            JGEXProblemBuilder(rng=rng)
            .include_auxiliary_clauses(True)
            .with_problem_from_txt(
                problem_txt=jgex_string,
                problem_name=problem_name,
            )
        )
        problem_setup = builder.build()
        solver = GeometricSolverBuilder(rng=rng).build(problem_setup)
        solver.run()
        return True, None
    except Exception as e:
        return False, str(e)

print("run_newclid() ready")



def formalize(nl_problem, examples, max_rounds=1):
    previous_attempt = None
    error_message = None
    history = []

    for round_num in range(max_rounds):
        messages = build_prompt(nl_problem, examples, previous_attempt, error_message)

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=3000,
        )

        # Guard against None content
        content = response.choices[0].message.content
        if content is None:
            print(f"  Round {round_num + 1}: API returned None content. Finish reason: {response.choices[0].finish_reason}")
            print(f"  Full response: {response}")
            history.append({
                "round": round_num + 1,
                "jgex_candidate": None,
                "success": False,
                "error": f"API returned None, finish_reason={response.choices[0].finish_reason}"
            })
            break

        jgex_candidate = content.strip().replace("```", "").strip()

        success, error = run_newclid(jgex_candidate)

        history.append({
            "round": round_num + 1,
            "jgex_candidate": jgex_candidate,
            "success": success,
            "error": error
        })

        print(f"  Round {round_num + 1}: {'✓' if success else '✗'}  {jgex_candidate[:80]}...")

        if success:
            return jgex_candidate, round_num + 1, history

        previous_attempt = jgex_candidate
        error_message = error

    return None, max_rounds, history

print("formalize() ready")
