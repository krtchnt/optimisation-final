# Quantum-Inspired Cosmological Optimisation (QICO) for Maximum Cut

Author: _6814001748 Kritchanat Thanapiphatsiri_

<!-- prettier-ignore -->
> [!IMPORTANT]
> This report was made under the **01204596 Optimisation** course of
> **Department of Computer Engineering**, **Faculty of Engineering**,
> **Kasetsart University**.

## Problem: Maximum Cut (Max-Cut)

Given a weighted undirected graph $G = (V, E, w)$, the **Maximum Cut** problem
asks for a partition of the vertex set $V$ into two disjoint sets $S$ and
$\bar{S} = V \setminus S$ that maximises the total weight of edges crossing the
partition:

$$\text{Cut}(S) = \sum_{\substack{(u,v) \in E \\ u \in S,\, v \in \bar{S}}} w(u, v)$$

Max-Cut is **NP-hard** (one of Karp's 21 NP-complete problems in its decision
form) and is the canonical benchmark for quantum optimisation algorithms such as
QAOA. The problem naturally maps to an **Ising Hamiltonian**, connecting it
directly to quantum computing and statistical physics.

## Algorithm: QICO

**Quantum-Inspired Cosmological Optimisation** is a novel population-based
metaheuristic inspired by the evolution of the universe and quantum mechanical
phenomena. It consists of the following phases:

1. **Big Bang Initialisation** -- random population generation
2. **Gravitational Attraction** -- solutions are drawn towards high-fitness
   regions, weighted by fitness-proportional "mass" and modulated by a decaying
   Hubble parameter $H(t) = H_0 \cdot \alpha^t$
3. **Quantum Tunnelling** -- probabilistic barrier-crossing with
   energy-barrier-aware probability
   $P_{\text{tunnel}} = \exp(-\Delta E / T_q(t))$, enabling escape from local
   optima
4. **Dark Energy Perturbation** -- small stochastic perturbations scaled by
   $H(t)$ to prevent premature convergence
5. **Cosmic Inflation Restart** -- when population diversity drops below a
   threshold, the bottom half is re-initialised while preserving elites
6. **Gravitational Collapse** -- periodic one-flip local search on elite
   solutions with efficient $O(|E|)$ delta evaluation
7. **CMB Memory** -- an archive of historically best solutions, periodically
   re-injected to preserve discovered structure

### Key Innovations

- **Adaptive quantum tunnelling**: tunnelling probability and magnitude adapt
  based on the energy barrier between a solution and the current best
- **Hubble parameter**: a single decaying parameter that simultaneously controls
  gravitational force, tunnelling magnitude, and dark energy -- providing a
  smooth exploration-to-exploitation transition
- **Diversity-triggered inflation**: automatic detection and correction of
  premature convergence

## Results

Experiments on random Erdos-Renyi weighted graphs with 10 independent trials per
configuration:

| $n$ | $\|E\|$ | QICO (mean) | GA (mean) | SA (mean) | SQA (mean) |
| --- | ------- | ----------- | --------- | --------- | ---------- |
| 20  | 105     | 397.3       | 391.5     | 398.0     | 391.8      |
| 50  | 486     | **1740.7**  | 1736.7    | 1737.2    | 1714.3     |
| 100 | 1523    | 5184.6      | 5146.8    | 5187.0    | 5072.8     |

QICO consistently ranks among the top two algorithms across all problem sizes,
achieving the **best mean and lowest variance** on medium-sized instances.

## Usage

```bash
uv run -m src.main
```

This runs the full comparison experiment and saves convergence plots to
`slides/assets/`.

## Attributions

- The slide [KU logo](./slides/assets/KU_Logo_PNG.png) is owned by
  [Kasetsart University](https://ku.ac.th/th/kulogo).
