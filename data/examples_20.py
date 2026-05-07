# 20 curated in-context examples for the JGEX formalization pipeline
# Covers: segment, triangle, r_triangle, midpoint, foot, orthocenter, incenter2,
#         angle_bisector, reflect, mirror, on_circle, on_bline, on_tline, on_pline,
#         on_aline, on_line, lc_tangent, intersection_ll, intersection_lc,
#         eqdistance, parallelogram, centroid, ninepoints, iso_trapezoid, simtri, circle
# Goals:  perp, para, cong, coll, eqangle, eqratio, midp, cyclic, simtri

EXAMPLES = [
    {
        "nl": "Let $\\overline{AH_1}$, $\\overline{BH_2}$, and $\\overline{CH_3}$ be the altitudes of an acute triangle $ABC$.   The incircle $\\omega$ of triangle $ABC$ touches the sides $BC$, $CA$, and $AB$ at $T_1$, $T_2$, and $T_3$, respectively.   Consider the reflections of the lines $H_1H_2$, $H_2H_3$, and $H_3H_1$ with respect to the lines $T_1T_2$, $T_2T_3$, and $T_3T_1$.   Prove that these images form a triangle whose vertices lie on $\\omega$.",
        "jgex": "a b c = triangle a b c; h = orthocenter h a b c; t1 t2 t3 i = incenter2 t1 t2 t3 i a b c; h1 = foot h1 a b c; h2 = foot h2 b c a; h3 = foot h3 c a b; x1 = reflect x1 h1 t1 t2; x2 = reflect x2 h2 t1 t2; y2 = reflect y2 h2 t2 t3; y3 = reflect y3 h3 t2 t3; z = on_line z x1 x2, on_line z y2 y3 | q = midpoint q b i; s = midpoint s i h2 ? cong i z i t1"
    },
    {
        "nl": "Let $BC$ be a diameter of circle $\\omega$ with center $O$. Let $A$ be a point of circle $\\omega$ such that $0^\\circ < \\angle AOB < 120^\\circ$. Let $D$ be the midpoint of arc $AB$ not containing $C$. Line $\\ell$ passes through $O$ and is parallel to line $AD$. Line $\\ell$ intersects line $AC$ at $J$. The perpendicular bisector of segment $OA$ intersects circle $\\omega$ at $E$ and $F$. Prove that $J$ is the incenter of triangle $CEF$.",
        "jgex": "b c = segment b c; o = midpoint o b c; a = on_circle a o b; d = on_circle d o b, on_bline d a b; e = on_bline e o a, on_circle e o b; f = on_bline f o a, on_circle f o b; j = on_pline j o a d, on_line j a c ? eqangle e c e j e j e f"
    },
    {
        "nl": "Let $ABC$ be an acute-angled triangle with $AB \\ne AC$.   The circle with diameter $BC$ intersects the sides $AB$ and $AC$ at $M$ and $N$, respectively.   Denote by $O$ the midpoint of the side $BC$.   The bisectors of the angles $\\angle BAC$ and $\\angle MON$ intersect at $R$.   Prove that the circumcircles of the triangles $BMR$ and $CNR$ have a common point lying on the side $BC$.",
        "jgex": "a b c = triangle a b c; o = midpoint o b c; m = on_circle m o b, on_line m a b; n = on_circle n o b, on_line n a c; r = angle_bisector r b a c, angle_bisector r m o n; o1 = circle o1 b m r; o2 = circle o2 c n r; p = on_circle p o1 r, on_circle p o2 r | k = on_bline k m n; l = eqdistance l k k a, eqdistance l o o a ? coll p b c"
    },
    {
        "nl": "Consider the convex quadrilateral $ABCD$.   The point $P$ is in the interior of $ABCD$.   The following ratio equalities hold: $$ \\angle PAD : \\angle PBA : \\angle DPA = 1 : 2 : 3 = \\angle CBP : \\angle BAP : \\angle BPC. $$ Prove that the following three lines meet in a point:   the internal bisectors of angles $\\angle ADP$ and $\\angle PCB$ and the perpendicular bisector of segment $AB$.",
        "jgex": "p a b = triangle p a b; x = angle_bisector x p b a; y = angle_bisector y p a b; z = on_aline z a p a b x; t = on_aline t p a p a z; d = on_aline d p t p b a, on_line d a z; u = on_aline u b p b a y; v = on_aline v p b p b u; c = on_aline c p v p a b, on_line c b u; o = angle_bisector o a d p, angle_bisector o p c b | j = intersection_ll j o c a y; k = reflect k p j c ? cong o a o b"
    },
    {
        "nl": "Let $AB$ be a segment. If $M$ lies between $A$ and $B$ and $AM=MB$ then $M$ is the midpoint of $\\overline{AB}$.",
        "jgex": "a b = segment a b; m = midpoint m a b ? midp m a b"
    },
    {
        "nl": "If $D\\in AB$, $E\\in AC$, and $DE\\parallel BC$, then $\\triangle ADE\\sim\\triangle ABC$.",
        "jgex": "a b c = triangle a b c;d = on_line d a b;e = on_line e a c, on_pline e d b c ? simtri a d e a b c"
    },
    {
        "nl": "In $\\triangle ABC$, if $G$ is the centroid and $X$ is the midpoint of $BC$, then $A,G,X$ are collinear.",
        "jgex": "a b c = triangle a b c;x y z g = centroid x y z g a b c ? coll a x g"
    },
    {
        "nl": "In $\\triangle ABC$, let $X,Y,Z$ be the midpoints of the sides and let $I$ be the nine-point circle center. Prove that $IX = IY$.",
        "jgex": "a b c = triangle a b c; x y z i = ninepoints x y z i a b c ? cong i x i y"
    },
    {
        "nl": "If $X$ is constructed on the tangent at $A$ to the circle centered at $O$ (radius $OA$), prove $AX\\perp AO$.",
        "jgex": "o a = segment o a;x = lc_tangent x a o ? perp a x a o"
    },
    {
        "nl": "A straight line which bisects two sides of a triangle is parallel to the third side.",
        "jgex": "a b c = triangle a b c; d = midpoint d a b; e = midpoint e a c ? para d e b c"
    },
    {
        "nl": "The middle point of the hypotenuse of a right triangle is equidistant from the three vertices.",
        "jgex": "a b c = r_triangle a b c; m = midpoint m b c ? cong m a m b; cong m a m c"
    },
    {
        "nl": "The diagonals of an isosceles trapezoid are equal.",
        "jgex": "a b c d = iso_trapezoid a b c d ? eqratio a c b d a d b c; eqratio a d b c c d d c"
    },
    {
        "nl": "To inscribe a square in a given circle.",
        "jgex": "o a = segment o a; b = mirror b a o; t = on_tline t o o a; c = on_circle c o a, on_line c o t; d = mirror d c o ? cong o a o b; cong o a o c; cong o a o d; perp a b c d"
    },
    {
        "nl": "From external point $P$, a tangent $PT$ and a secant through $P$ cutting the circle at $A,B$: show $PT^2 = PA \\cdot PB$.",
        "jgex": "o a0 = segment o a0; t = on_circle t o a0; p = on_tline p t o t; b = on_circle b o a0; a = intersection_lc a p o b ? eqratio p t p a p b p t"
    },
    {
        "nl": "In a triangle, the angle bisector from vertex $A$ to side $BC$ divides $BC$ in the ratio $AB:AC$.",
        "jgex": "a b c = triangle a b c; x = angle_bisector x b a c; d = intersection_ll d a x b c ? eqratio b d d c a b a c"
    },
    {
        "nl": "In a parallelogram, opposite sides are equal and parallel; a diagonal cuts it into two congruent triangles.",
        "jgex": "a b c = triangle a b c; d = parallelogram d a b c ? para a b c d; para b c a d; cong a b c d; cong b c a d; eqangle a b b c c d d a"
    },
    {
        "nl": "Given triangle $ABC$, construct the angle bisectors of $\\angle A$ and $\\angle B$; let $I$ be their intersection. Construct the circle centred at $I$ tangent to side $BC$. Prove this circle is the incircle of $ABC$ (tangent to all three sides).",
        "jgex": "a b c = triangle a b c; x = angle_bisector x b a c; y = angle_bisector y a b c; i = intersection_ll i a x b y; p = on_tline p i b c; d = intersection_ll d i p b c; q = on_tline q i a b; e = intersection_ll e i q a b; r = on_tline r i a c; f = intersection_ll f i r a c ? perp i d b c; perp i e a b; perp i f a c; cong i d i e; cong i d i f"
    },
    {
        "nl": "Let $P,Q,K$ be non-collinear, and let $R$ be the midpoint of segment $PQ$. Let $K_1$ be the perpendicular foot of $K$ on line $PQ$. Construct a point $L$ such that its perpendicular distance to line $PQ$ equals the perpendicular distance of $K$ to line $PQ$. Prove that triangles $\\triangle RPK$ and $\\triangle RQL$ have equal area.",
        "jgex": "p q k = triangle p q k; r = midpoint r p q; k1 = foot k1 k p q; l1 = on_line l1 p q; l = on_tline l l1 p q, eqdistance l l1 k k1 ? eqratio k k1 l l1 r q r p"
    },
    {
        "nl": "If two straight lines cut one another, then they make the vertical angles equal to one another.",
        "jgex": "a b c = triangle a b c; d = on_tline d c a b; e = intersection_ll e a b c d ? eqangle e a e b e c e d"
    },
    {
        "nl": "Let $AB$ be a diameter of a circle $\\omega$, and let $C$ be a point on $\\omega$ different from $A,B$. Prove that $\\angle ACB=90^\\circ$.",
        "jgex": "a b = segment a b; o = midpoint o a b; c = on_circle c o a ? perp c a c b"
    },
]
