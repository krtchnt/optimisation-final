"""Quantum-Inspired Cosmological Optimisation (QICO).

A novel metaheuristic for combinatorial optimisation inspired by the evolution
of the universe and quantum mechanical phenomena.

Cosmological phases:
    1. Big Bang Initialisation -- random population from a primordial singularity
    2. Gravitational Attraction -- solutions drawn toward high-mass (high-fitness)
       regions, weighted by an inverse-Hamming-distance gravitational force
    3. Quantum Tunnelling -- probabilistic barrier-crossing modulated by the
       energy gap and a decaying quantum temperature, enabling escape from
       local optima
    4. Dark Energy Perturbation -- small stochastic bit-flips scaled by the
       Hubble parameter to prevent premature convergence
    5. Cosmic Inflation Restart -- when population diversity drops below a
       threshold, the bottom fraction is re-initialised (a mini Big Bang)
    6. Gravitational Collapse -- periodic one-flip local search on elite
       solutions (analogous to gravitational collapse forming structure)
    7. CMB Memory -- an archive of historically best solutions, periodically
       re-injected to preserve discovered structure
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import final

import numpy as np
from numpy.typing import NDArray

from .problem import MaxCutProblem


@dataclass
class QICOResult:
    """Container for QICO optimisation results."""

    best_solution: NDArray[np.int8]
    best_fitness: float
    history: list[float] = field(default_factory=list)
    evals_used: int = 0


@final
class QICO:
    """Quantum-Inspired Cosmological Optimisation Algorithm."""

    def __init__(
        self,
        pop_size: int = 50,
        max_evals: int = 25000,
        hubble_init: float = 0.85,
        hubble_decay: float = 0.997,
        tunnel_temp_init: float = 1.0,
        tunnel_temp_decay: float = 0.995,
        dark_energy: float = 0.02,
        inflation_threshold: float = 0.08,
        local_search_freq: int = 10,
        local_search_top_k: int = 5,
        cmb_size: int = 10,
        cmb_inject_freq: int = 25,
        top_k_fraction: float = 0.2,
        seed: int | None = None,
    ) -> None:
        self.pop_size = pop_size
        self.max_evals = max_evals
        self.hubble_init = hubble_init
        self.hubble_decay = hubble_decay
        self.tunnel_temp_init = tunnel_temp_init
        self.tunnel_temp_decay = tunnel_temp_decay
        self.dark_energy = dark_energy
        self.inflation_threshold = inflation_threshold
        self.local_search_freq = local_search_freq
        self.local_search_top_k = local_search_top_k
        self.cmb_size = cmb_size
        self.cmb_inject_freq = cmb_inject_freq
        self.top_k_fraction = top_k_fraction
        self.seed = seed

    def optimize(self, problem: MaxCutProblem) -> QICOResult:
        """Run QICO on the given Max-Cut instance."""
        rng = np.random.default_rng(self.seed)
        n = problem.n

        # === BIG BANG INITIALISATION ===
        pop = rng.integers(0, 2, size=(self.pop_size, n)).astype(np.int8)
        fitness = problem.evaluate_batch(pop)
        evals = self.pop_size

        best_idx = int(np.argmax(fitness))
        best_sol = pop[best_idx].copy()
        best_fit = float(fitness[best_idx])

        # CMB Memory archive
        cmb: list[tuple[NDArray[np.int8], float]] = [(best_sol.copy(), best_fit)]

        hubble = self.hubble_init
        tunnel_temp = self.tunnel_temp_init
        history: list[float] = [best_fit]
        generation = 0

        while evals < self.max_evals:
            generation += 1

            # --- Compute gravitational masses ---
            f_min = float(fitness.min())
            f_max = float(fitness.max())
            if f_max > f_min:
                masses = (fitness - f_min) / (f_max - f_min)
            else:
                masses = np.ones(self.pop_size)
            mass_total = float(masses.sum())
            norm_masses = (
                masses / mass_total
                if mass_total > 0
                else np.full(self.pop_size, 1.0 / self.pop_size)
            )

            # Identify top-k attractors
            k = max(1, int(self.pop_size * self.top_k_fraction))
            top_k_idx = np.argsort(fitness)[-k:]
            attractor_masses = norm_masses[top_k_idx]
            am_sum = float(attractor_masses.sum())
            attractor_probs = (
                attractor_masses / am_sum if am_sum > 0 else np.full(k, 1.0 / k)
            )

            new_pop = pop.copy()

            for i in range(self.pop_size):
                # === GRAVITATIONAL ATTRACTION ===
                att_idx = rng.choice(top_k_idx, p=attractor_probs)
                attractor = pop[att_idx]
                diff_bits = np.where(new_pop[i] != attractor)[0]

                if len(diff_bits) > 0:
                    grav_force = (1.0 - hubble) * float(masses[att_idx])
                    flip_mask = rng.random(len(diff_bits)) < grav_force
                    new_pop[i, diff_bits[flip_mask]] = attractor[diff_bits[flip_mask]]

                # === QUANTUM TUNNELLING ===
                if best_fit > 0:
                    barrier = max(0.0, (best_fit - fitness[i]) / best_fit)
                else:
                    barrier = 0.5
                tunnel_prob = float(np.exp(-barrier / max(tunnel_temp, 1e-10)))

                if rng.random() < tunnel_prob:
                    n_flip = min(int(rng.geometric(p=max(0.3, 1.0 - hubble))), n)
                    flip_bits = rng.choice(n, size=n_flip, replace=False)
                    new_pop[i, flip_bits] = 1 - new_pop[i, flip_bits]

                # === DARK ENERGY PERTURBATION ===
                de_mask = rng.random(n) < self.dark_energy * hubble
                new_pop[i, de_mask] = 1 - new_pop[i, de_mask]

            # Evaluate offspring
            new_fitness = problem.evaluate_batch(new_pop)
            evals += self.pop_size

            # Greedy selection
            improved = new_fitness >= fitness
            pop[improved] = new_pop[improved]
            fitness[improved] = new_fitness[improved]

            # === GRAVITATIONAL COLLAPSE (Local Search) ===
            if generation % self.local_search_freq == 0:
                elite_count = min(self.local_search_top_k, self.pop_size)
                elite_indices = np.argsort(fitness)[-elite_count:]
                for idx in elite_indices:
                    if evals >= self.max_evals:
                        break
                    changed = True
                    while changed and evals < self.max_evals:
                        changed = False
                        for v in rng.permutation(n):
                            delta = problem.delta_flip(pop[idx], v)
                            evals += 1
                            if delta > 0:
                                pop[idx, v] = 1 - pop[idx, v]
                                fitness[idx] += delta
                                changed = True
                            if evals >= self.max_evals:
                                break

            # Update global best
            curr_best_idx = int(np.argmax(fitness))
            if fitness[curr_best_idx] > best_fit:
                best_sol = pop[curr_best_idx].copy()
                best_fit = float(fitness[curr_best_idx])
                cmb.append((best_sol.copy(), best_fit))
                if len(cmb) > self.cmb_size:
                    cmb.sort(key=lambda x: x[1])
                    _ = cmb.pop(0)

            # === COSMIC INFLATION RESTART ===
            diversity = self._population_diversity(pop, rng)
            if diversity < self.inflation_threshold:
                sort_idx = np.argsort(fitness)
                n_replace = self.pop_size // 2
                for ri in range(n_replace):
                    pop[sort_idx[ri]] = rng.integers(0, 2, size=n).astype(np.int8)
                    fitness[sort_idx[ri]] = problem.evaluate(pop[sort_idx[ri]])
                    evals += 1
                    if evals >= self.max_evals:
                        break

            # === CMB MEMORY INJECTION ===
            if generation % self.cmb_inject_freq == 0 and cmb:
                worst_idx = int(np.argmin(fitness))
                mem_sol, mem_fit = cmb[rng.integers(len(cmb))]
                pop[worst_idx] = mem_sol.copy()
                fitness[worst_idx] = mem_fit

            # Cosmic evolution: decay parameters
            hubble *= self.hubble_decay
            tunnel_temp *= self.tunnel_temp_decay

            history.append(best_fit)

        return QICOResult(
            best_solution=best_sol,
            best_fitness=best_fit,
            history=history,
            evals_used=evals,
        )

    @staticmethod
    def _population_diversity(
        pop: NDArray[np.int8],
        rng: np.random.Generator,
        n_samples: int = 20,
    ) -> float:
        """Normalised mean pairwise Hamming distance over a sample."""
        actual_samples = min(n_samples, pop.shape[0])
        indices = rng.choice(pop.shape[0], size=actual_samples, replace=False)
        sample = pop[indices]
        total = 0.0
        count = 0
        for i in range(actual_samples):
            for j in range(i + 1, actual_samples):
                total += float(np.mean(sample[i] != sample[j]))  # pyright: ignore[reportUnknownArgumentType]
                count += 1
        return total / max(count, 1)
