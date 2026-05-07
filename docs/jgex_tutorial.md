# JGEX tutorial

To use Newclid, each geometry problem must first be written in the JGEX format. This tutorial explains the basic structure of a JGEX file and how to describe a geometric construction and its goal step by step.

JGEX is the language Newclid uses to represent a geometry problem in a structured way. It converts the natural-language description of a figure into explicit constructions and a goal that the system can check. JGEX covers the standard objects and relations of Euclidean geometry, but some problems cannot be expressed if they rely on concepts outside this vocabulary.

A JGEX file consists of a sequence of constructions that build the objects of the problem, optionally followed by helper constructions, and ends with a goal line that specifies what to prove. The definitions of all available constructors and predicates can be found in the [online manual](https://newclid.github.io/Newclid/manual/building_a_problem_setup/jgex/databases/index.html).

---

## A minimal example

Here is a small JGEX script showing a triangle, a point on a side, and the goal of proving collinearity:

```
a b c = triangle a b c; p = on_line p b c ? coll p b c
```

This illustrates the basic pattern: constructions that define the figure, followed by a single goal to be verified by Newclid.

---

## 1. Constructions

Each construction has the form:

```
name = constructor args
```

Names can be chosen freely and are usually short labels. The number of names on the left must match the number of objects created by the constructor.

Multiple constructions are separated by semicolons `;`. A single construction may contain several conditions, separated by commas `,`, when the object is defined by more than one requirement.

**Example 1 — triangle:**

```
a b c = triangle a b c
```

This creates a triangle ABC.

**Example 2 — midpoint and circle:**

```
a b = segment a b; o = midpoint o a b; c = on_circle c o a
```

Here AB is a segment, O is its midpoint, and C lies on the circle centered at O with radius OA.

**Example 3 — intersection defined by two conditions:**

```
z = on_line z x y, on_line z b c
```

The comma means that Z satisfies both conditions: it lies on line XY and on line BC. So Z is the intersection point of the two lines.

---

## 2. Helper constructions

If the problem needs extra elements to make the configuration complete, they are written after a vertical bar `|`. Helper constructions follow the same format as regular constructions. They are not part of the original problem statement but are added to help JGEX process the goal — for example, to introduce points needed to construct a line or direction required to express the final predicate.

**Example:**

```
a b c = triangle a b c;
d e f i = incenter2 d e f i a b c;
...
t = on_line t p q, on_line t i d
| n = orthocenter n c a i;
  g = on_pline g c a b, on_pline g a c n
? perp a t a i
```

Here the points `n` and `g` do not appear in the original problem. They are helper constructions added so that JGEX can explicitly form a line through A perpendicular to AI, allowing the system to check the goal `perp a t a i`. A full explanation of this example is given in [walkthrough_examples.md](./walkthrough_examples.md).

---

## 3. Goal line

The goal line has the form:

```
? predicate args
```

It starts with a question mark `?` and is followed by a predicate such as `coll`, `cong`, `cyclic`, or `eqangle`. It expresses what needs to be proved. Multiple goals are separated by semicolons `;`.

**Example 1 — collinearity:**

```
? coll p b c
```

This states that points P, B, and C are collinear.

**Example 2 — segment equality:**

```
? cong p q q r
```

This states that segments PQ and QR are equal in length.

**Example 3 — cyclicity:**

```
? cyclic p q r m
```

This states that points P, Q, R, and M lie on the same circle.

**Example 4 — angle equality:**

```
? eqangle e c e j e j e f
```

This states that ∠CEJ = ∠JEF, i.e., two directed angles are equal.

---

## 4. Minimal template

The full structure of a JGEX file is:

```
<constructions>
| <helper constructions>        (optional)
? <predicate> <args>            (goal)
```

More precisely:

| Part | Syntax |
|---|---|
| Construction | `name = constructor args` |
| Multiple constructions | separated by `;` |
| Multiple conditions on one object | separated by `,` |
| Helper constructions | prefixed with `\|` |
| Goal | `? predicate args` |

A complete minimal example bringing all parts together:

```
a b c = triangle a b c;
d e f i = incenter2 d e f i a b c;
t = on_line t p q, on_line t i d
| n = orthocenter n c a i;
  g = on_pline g c a b, on_pline g a c n
? perp a t a i
```
