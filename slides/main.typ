#import "@preview/touying:0.6.3": *
#import themes.university: *
#import "@preview/cetz:0.4.2"
#import "@preview/fletcher:0.5.8" as fletcher: edge, node
#import "@preview/numbly:0.1.0": numbly
#import "@preview/theorion:0.4.1": *
#import cosmos.clouds: *
#show: show-theorion

// cetz and fletcher bindings for touying
#let cetz-canvas = touying-reducer.with(
  reduce: cetz.canvas,
  cover: cetz.draw.hide.with(bounds: true),
)
#let fletcher-diagram = touying-reducer.with(
  reduce: fletcher.diagram,
  cover: fletcher.hide,
)

#show: university-theme.with(
  aspect-ratio: "16-9",
  config-common(frozen-counters: (theorem-counter,)),
  config-info(
    title: [Quantum-Inspired Cosmological Optimisation],
    subtitle: [A Novel Metaheuristic for the Maximum Cut Problem],
    author: [Kritchanat Thanapiphatsiri],
    date: datetime(year: 2026, month: 3, day: 13),
    institution: [Department of Computer Engineering \ Kasetsart University],
    logo: box(image("assets/KU_Logo_PNG.png"), width: 1.25cm, baseline: 60%),
  ),
)

#set heading(numbering: numbly("{1}.", default: "1.1"))

#title-slide()

== Outline <touying:hidden>

#columns(2, outline(title: none, indent: 1em))

// ========================================================================
= The Maximum Cut Problem
// ========================================================================

== Problem Definition

#speaker-note[
  Max-Cut is one of the most studied combinatorial optimisation problems. The
  Goemans-Williamson algorithm uses semidefinite programming relaxation and
  random hyperplane rounding to achieve a 0.878 approximation ratio, which is
  optimal assuming the Unique Games Conjecture. QAOA by Farhi et al. (2014) was
  specifically designed for Max-Cut on bounded-degree graphs.
]

#[
  #set text(size: 0.85em)

  #definition[
    Given a weighted undirected graph $G = (V, E, w)$, the *Maximum Cut*
    (Max-Cut) problem asks for a partition of $V$ into two disjoint sets $S$ and
    $overline(S) = V without S$ that maximises the total weight of edges
    crossing the partition:
    $ "Cut"(S) = sum_((u,v) in E \ u in S, v in overline(S)) w(u, v) $
  ]

  #pause

  - *NP-hard* -- one of Karp's 21 NP-complete problems (decision version)
  - Best known polynomial approximation: *Goemans--Williamson*
    (0.878-approximation via SDP)
  - Canonical benchmark for *QAOA* (Quantum Approximate Optimisation Algorithm)
]

== Max-Cut Example

#slide(composer: (1fr, 1fr))[
  #fletcher.diagram(
    node-stroke: 2pt,
    spacing: (2em, 4em),
    label-sep: 0pt,

    let s = black,
    let s_bar = white,
    // Nodes - S = {0, 3, 6} (blue), S_bar = {1, 2, 4, 5} (orange)
    node(
      (1, 0),
      text(fill: white, weight: "bold")[0],
      fill: black,
      inset: 5pt,
    ),
    node(
      (3, 0),
      [*1*],
      fill: white,
      inset: 5pt,
    ),
    node(
      (0, 1),
      [*2*],
      fill: white,
      inset: 5pt,
    ),
    node(
      (2, 1),
      text(fill: white, weight: "bold")[3],
      fill: black,
      inset: 5pt,
    ),
    node(
      (4, 1),
      [*4*],
      fill: white,
      inset: 5pt,
    ),
    node(
      (1, 2),
      [*5*],
      fill: white,
      inset: 5pt,
    ),
    node(
      (3, 2),
      text(fill: white, weight: "bold")[6],
      fill: black,
      inset: 5pt,
    ),

    // Cut edges (red, thick)
    edge((1, 0), (3, 0), "-", stroke: 5pt + red, label: [4]),
    edge((1, 0), (0, 1), "-", stroke: 5pt + red, label: [3]),
    edge(
      (3, 0),
      (2, 1),
      "-",
      stroke: 5pt + red,
      label: [2],
      label-side: right,
    ),
    edge((0, 1), (2, 1), "-", stroke: 5pt + red, label: [7]),
    edge((2, 1), (4, 1), "-", stroke: 5pt + red, label: [3]),
    edge(
      (2, 1),
      (1, 2),
      "-",
      stroke: 5pt + red,
      label: [4],
      label-side: right,
    ),
    edge((4, 1), (3, 2), "-", stroke: 5pt + red, label: [5]),
    edge((1, 2), (3, 2), "-", stroke: 5pt + red, label: [3]),

    // Non-cut edges (gray)
    edge(
      (1, 0),
      (2, 1),
      "-",
      stroke: 2pt + black,
      label: [5],
      label-side: left,
    ),
    edge((3, 0), (4, 1), "-", stroke: 2pt + black, label: [6]),
    edge((0, 1), (1, 2), "-", stroke: 2pt + black, label: [1]),
    edge(
      (2, 1),
      (3, 2),
      "-",
      stroke: 2pt + black,
      label: [2],
      label-side: left,
    ),
  )
][
  *Partition*: $S = {0, 3, 6}$

  #v(0.5em)

  Cut edges (#text(fill: red)[red]):

  #set text(size: 0.85em)

  $(0,1): 4, quad (0,2): 3$ \
  $(1,3): 2, quad (2,3): 7$ \
  $(3,4): 3, quad (3,5): 4$ \
  $(4,6): 5, quad (5,6): 3$

  #v(0.5em)

  $
    #strong("Cut value") & = 2(4)+3(3)+2+7+5 \
                         & = 31
  $
]

== Why Max-Cut?

#[
  #set text(size: 0.95em)

  / Graph Theory: Fundamental graph partitioning problem with applications in
    VLSI design, statistical physics, and network analysis

  / Quantum Computing: The problem naturally maps to an \ *Ising Hamiltonian*:
    $ H = sum_((i,j) in E) w_(i j) dot sigma_i^z sigma_j^z $
    making it the primary benchmark for quantum optimisation (QAOA, quantum
    annealing)

  / Difficulty: NP-hard even for unweighted graphs; no PTAS unless P $=$ NP
]

#speaker-note[
  The Ising formulation: each vertex i gets a spin variable s_i in {-1, +1}. The
  partition is S = {i : s_i = +1}. The cut value is (1/2) sum w_ij (1 - s_i
  s_j), so maximising the cut is equivalent to minimising the Ising Hamiltonian
  H = -sum w_ij s_i s_j. This is exactly the cost function used in quantum
  annealing hardware like D-Wave systems and in QAOA circuits.
]

// ========================================================================
= The QICO Algorithm
// ========================================================================

== Motivation

The evolution of the universe naturally balances *exploration* and
*exploitation*:

#pause

#table(
  columns: (1fr, 1fr),
  inset: 8pt,
  stroke: 0.5pt,
  table.header[*Cosmological Phenomenon*][*Optimisation Analogue*],
  [Big Bang], [Random initialisation],
  [Cosmic expansion (Hubble flow)], [Exploration of search space],
  [Gravitational attraction], [Exploitation towards good regions],
  [Quantum tunnelling], [Escaping local optima],
  [Dark energy], [Preventing premature convergence],
  [Structure formation], [Local search refinement],
  [CMB radiation], [Memory of best configurations],
)

== Algorithm Overview

#fletcher-diagram(
  node-stroke: 0.8pt,
  spacing: (1.5em, 2.5em),
  node-corner-radius: 4pt,

  node(
    (0, 0),
    [*Big Bang* \ Init.],
    shape: fletcher.shapes.pill,
    fill: blue.lighten(80%),
    inset: 15pt,
  ),
  edge("-|>"),
  node((1, 0), [Gravitational \ Attraction], fill: green.lighten(80%)),
  edge("-|>"),
  node((2, 0), [Quantum \ Tunnelling], fill: purple.lighten(80%)),
  edge("-|>"),
  node((3, 0), [Dark Energy \ Perturb.], fill: orange.lighten(80%)),
  pause,
  edge((3, 0), (3, 1), "-|>"),
  node((3, 1), [Selection], fill: gray.lighten(80%)),
  edge((3, 1), (3, 2), "-|>", [Every $k$ gen.], label-side: left),
  node((3, 2), [Gravitational \ Collapse], fill: yellow.lighten(60%)),
  pause,
  edge(
    (3, 1),
    (0, 0),
    "-|>",
    bend: 60deg,
    [Next generation],
    label-side: auto,
  ),
  node((1, 1), [Inflation \ Restart], fill: red.lighten(80%)),
  edge((3, 1), (1, 1), "..|>", [Low diversity?], label-side: right),
  edge((1, 1), (1, 0), "..|>"),
)

#speaker-note[
  The algorithm flow:
  1. Big Bang creates the initial random population
  2. Each generation: gravitational attraction pulls solutions toward
    high-fitness "massive" solutions, then quantum tunnelling randomly flips
    bits to escape local optima, then dark energy adds small random
    perturbations
  3. Greedy selection keeps the better of parent/offspring
  4. Every k generations, local search (gravitational collapse) refines the top
    solutions
  5. If diversity drops too low, cosmic inflation re-diversifies the bottom half
    of the population
]

== Gravitational Attraction

#[
  #set text(size: 0.9em)

  Each solution $x_i$ has a *mass* proportional to its fitness:

  $ m_i = (f(x_i) - f_"min") / (f_"max" - f_"min") $

  #pause

  For each solution, select an *attractor* $x_j$ from the top-$k$ solutions with
  probability $prop m_j$.

  #pause

  For each bit $b$ where $x_i^((b)) eq.not x_j^((b))$, flip $x_i^((b))$ towards
  the attractor with probability:

  $ P_"grav" = (1 - H(t)) dot m_j $

  where $H(t) = H_0 dot alpha^t$ is the *Hubble parameter* that decays over time
  (from exploration to exploitation).
]

#speaker-note[
  The Hubble parameter H(t) starts high (around 0.85), meaning that
  gravitational attraction is weak initially -- solutions explore freely. As H
  decays with factor alpha = 0.997 per generation, the gravitational force
  increases and solutions converge toward the best regions. This mirrors how the
  universe transitions from rapid expansion to gravitational structure
  formation.
]

== Quantum Tunnelling

#[
  #set text(size: 0.82em)

  Solutions can *tunnel through energy barriers* to escape local optima.

  #pause

  The tunnelling probability depends on the *energy barrier* and \
  *quantum temperature*:

  $ Delta E_i = (f^* - f(x_i)) / f^* , quad quad T_q (t) = T_0 dot beta^t $

  $ P_"tunnel" = exp(- Delta E_i / T_q (t)) $

  #pause

  When tunnelling occurs, $n_"flip"$ random bits are flipped, where:

  $ n_"flip" tilde "Geometric"(p = max(0.3, 1 - H(t))) $

  #pause

  *Key insight*: better solutions (low $Delta E$) tunnel more often but flip
  fewer bits, while poor solutions occasionally make large jumps.
]

== Dark Energy & Inflation

#[
  #set text(size: 0.88em)

  === Dark Energy Perturbation

  Each bit is randomly flipped with probability $p_"DE" dot H(t)$, where
  $p_"DE"$ is a small constant.

  - Prevents premature convergence by maintaining diversity
  - Effect diminishes naturally as $H(t)$ decays

  #pause

  === Cosmic Inflation Restart

  When the population *diversity* (mean pairwise Hamming distance) drops below a
  threshold:

  - Retain the *elite* (top 50% by fitness)
  - Replace the *bottom 50%* with fresh random solutions

  This is analogous to cosmic inflation -- a rapid expansion event that
  re-introduces diversity into a stagnating universe.
]

== Gravitational Collapse

#[
  #set text(size: 0.92em)

  Periodically (every $k$ generations), the *top-$K$* elite solutions undergo
  *local search*:

  #pause

  #block(
    width: 100%,
    inset: 10pt,
    stroke: 0.5pt + gray,
    radius: 4pt,
    fill: gray.lighten(95%),
  )[
    *Gravitational Collapse (1-flip local search)* \
    For each elite solution $x$: \
    #h(1em) *repeat*: \
    #h(2em) For each vertex $v in V$ (random order): \
    #h(3em) Compute
    $Delta = sum_(u in N(v)) w(v,u) dot cases(+1 &"if " x_u = x_v, -1 &"if " x_u eq.not x_v)$
    \
    #h(3em) If $Delta > 0$: flip $x_v$ \
    #h(1em) *until* no improvement found
  ]

  #pause

  This is $O(|E|)$ per pass and converges to a *local optimum* with respect to
  single-vertex moves.
]

#speaker-note[
  The delta evaluation is efficient: instead of recomputing the entire cut
  value, we only check the neighbours of the vertex being flipped. If the vertex
  and its neighbour are in the same partition, flipping the vertex would cut
  that edge (gaining weight). If they are in different partitions, flipping
  would uncut it (losing weight). The net delta tells us whether the flip
  improves the cut.
]

== CMB Memory Archive

The *Cosmic Microwave Background* (CMB) memory preserves the best solutions
discovered throughout the search:

- Maintains an archive of the top-$M$ historically best solutions
- Every $K$ generations, a random archived solution replaces the *worst*
  individual in the population

#pause

*Purpose*: prevents the loss of high-quality genetic material during cosmic
inflation restarts or stagnation periods.

This is analogous to the CMB -- a relic radiation from the early universe that
carries information about initial conditions.

// ========================================================================
= What Makes QICO Novel?
// ========================================================================

== Related Methods

#[
  #set text(size: 0.92em)

  #table(
    columns: (1.5fr, 1fr, 1fr, 1fr),
    inset: 7pt,
    stroke: 0.5pt,
    table.header[*Feature*][*GSA*][*BB-BC*][*QICO*],
    [Domain], [Continuous], [Continuous], [*Combinatorial*],
    [Quantum tunnelling], [No], [No], [*Adaptive*],
    [Diversity restart], [No], [Big Crunch], [*Inflation trigger*],
    [Local search], [No], [No], [*Grav. collapse*],
    [Solution archive], [No], [No], [*CMB memory*],
    [Parameter adaptation], [Fixed $G$], [Fixed], [*Hubble decay*],
  )

  #v(0.5em)

  / GSA: Gravitational Search Algorithm (Rashedi et al., 2009)
  / BB-BC: Big Bang--Big Crunch (Erol & Eksin, 2006)
]

#speaker-note[
  GSA uses Newtonian gravity in continuous space -- masses attract each other
  based on fitness and distance. QICO adapts this to combinatorial space using
  Hamming distance and bit-level gravitational attraction.

  BB-BC uses a contraction (big crunch) to find a centre of mass, then
  re-explodes (big bang) around it. QICO's cosmic inflation restart is
  different: it is triggered by low diversity, preserves elites, and is combined
  with quantum tunnelling for barrier crossing.
]

== Key Innovations

#[
  #set text(size: 0.82em)

  + *Adaptive quantum tunnelling* with energy-barrier-aware probability
    - Solutions near the optimum tunnel frequently (fine-tuning)
    - Distant solutions occasionally make large jumps (exploration)

  #pause

  + *Hubble parameter* for smooth exploration $arrow.r$ exploitation transition
    - Controls gravitational force, tunnelling magnitude, and dark energy
      simultaneously
    - Single parameter governs the entire search dynamics

  #pause

  + *Diversity-triggered cosmic inflation*
    - Automatic detection of premature convergence
    - Targeted re-diversification preserving elite knowledge

  #pause

  + *Integrated local search* (gravitational collapse)
    - Efficient $O(|E|)$ delta evaluation
    - Applied selectively to top solutions only
]


// ========================================================================
= Experimental Evaluation
// ========================================================================

== Experimental Setup

#[
  #set text(size: 0.92em)

  *Problem instances*: Random Erdos--Renyi weighted graphs $G(n, p)$ with
  weights $w in [1, 10]$

  #table(
    columns: (1fr, 1fr, 1fr, 1fr),
    inset: 6pt,
    stroke: 0.5pt,
    table.header[$n$][Density][$ |E| $][Budget],
    [20], [0.5], [$approx$ 105], [10 000],
    [50], [0.4], [$approx$ 486], [30 000],
    [100], [0.3], [$approx$ 1523], [60 000],
  )

  #v(0.5em)

  *Algorithms compared* (10 independent trials each):
  - *QICO* -- proposed method (pop. size = 50)
  - *GA* -- Genetic algorithm (tournament, uniform crossover, bit-flip mutation)
  - *SA* -- Simulated annealing (geometric cooling)
  - *SQA* -- Simulated quantum annealing (path-integral Monte Carlo, 8 replicas)
]

== Results: Small Graphs ($n = 20$)

#slide(composer: (1fr, 1fr))[
  #image("assets/convergence_n20.png", width: 100%)
][
  #table(
    columns: (1.2fr, 1fr, 1fr),
    inset: 6pt,
    stroke: 0.5pt,
    table.header[*Algorithm*][*Mean*][*Std*],
    [*QICO*], [*397.3*], [3.2],
    [GA], [391.5], [6.1],
    [SA], [398.0], [2.8],
    [SQA], [391.8], [6.6],
  )

  #v(0.5em)

  - All methods find the optimum (399.4) at least once
  - SA and QICO are most consistent
  - GA and SQA show higher variance
]

== Results: Med Graphs ($n=50$)

#slide(composer: (1fr, 1fr))[
  #image("assets/convergence_n50.png", width: 100%)
][
  #table(
    columns: (1.2fr, 1fr, 1fr),
    inset: 6pt,
    stroke: 0.5pt,
    table.header[*Algorithm*][*Mean*][*Std*],
    [*QICO*], [*1740.7*], [*7.3*],
    [GA], [1736.7], [9.0],
    [SA], [1737.2], [11.0],
    [SQA], [1714.3], [19.1],
  )

  #v(0.5em)

  - QICO achieves the *best mean* and *lowest variance*
  - SQA falls behind due to limited per-replica budget
  - QICO's local search gives it an edge
]

== Results: Large Graphs ($n = 100$)

#slide(composer: (1fr, 1fr))[
  #image("assets/convergence_n100.png", width: 100%)
][
  #[
    #set text(size: 0.95em)

    #table(
      columns: (1.1fr, 1fr, 1fr),
      inset: 6pt,
      stroke: 0.5pt,
      table.header[*Algorithm*][*Mean*][*Std*],
      [*QICO*], [*5184.6*], [22.5],
      [GA], [5146.8], [40.3],
      [SA], [5187.0], [25.5],
      [SQA], [5072.8], [42.4],
    )

    #v(0.5em)

    - QICO and SA are close; both significantly outperform GA and SQA
    - QICO's strength: *population diversity* + *local search*
    - SQA struggles with the evaluation budget split across replicas
  ]
]

== Summary of Results

#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  inset: 7pt,
  stroke: 0.5pt,
  table.header[*Metric*][$n = 20$][$n = 50$][$n = 100$],
  [Best mean], [SA (398.0)], [*QICO (1740.7)*], [SA (5187.0)],
  [Lowest std], [SA (2.8)], [*QICO (7.3)*], [*QICO (22.5)*],
  [2nd best mean], [*QICO (397.3)*], [SA (1737.2)], [*QICO (5184.6)*],
)

#v(0.5em)

- QICO is *consistently among the top 2* across all problem sizes
- Most reliable (lowest or near-lowest variance)
- Combines the population diversity of GA with the local refinement of SA
- Significantly outperforms SQA under fixed evaluation budgets

== Strengths and Limitations

#[
  #set text(size: 0.95em)

  === Strengths

  - *Robust*: low variance across independent runs
  - *Adaptive*: Hubble parameter smoothly transitions search behaviour
  - *Modular*: each cosmological phase addresses a specific optimisation need
  - Quantum tunnelling provides *principled* barrier crossing

  #pause

  === Limitations

  - More *hyperparameters* than SA (though defaults work well)
  - Local search dominates on small instances (the metaheuristic overhead is
    less impactful)
  - *Population-based*: higher per-generation cost than single-solution methods
]

// ========================================================================

#focus-slide([Thank you! \ #text(0.67em, [Any questions?])])
