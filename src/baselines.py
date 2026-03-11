"""Baseline optimisation algorithms for Max-Cut comparison."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

from .problem import MaxCutProblem


@dataclass
class OptResult:
    """Container for optimisation results."""

    best_solution: NDArray[np.int8]
    best_fitness: float
    history: list[float] = field(default_factory=list)
    evals_used: int = 0


# ---------------------------------------------------------------------------
# Genetic Algorithm
# ---------------------------------------------------------------------------


def genetic_algorithm(
    problem: MaxCutProblem,
    pop_size: int = 50,
    max_evals: int = 25000,
    crossover_rate: float = 0.9,
    mutation_rate: float = 0.02,
    tournament_size: int = 3,
    seed: int | None = None,
) -> OptResult:
    """Standard GA with tournament selection, uniform crossover, bit-flip mutation."""
    rng = np.random.default_rng(seed)
    n = problem.n

    pop = rng.integers(0, 2, size=(pop_size, n)).astype(np.int8)
    fitness = problem.evaluate_batch(pop)
    evals = pop_size

    best_idx = int(np.argmax(fitness))
    best_sol = pop[best_idx].copy()
    best_fit = float(fitness[best_idx])
    history: list[float] = [best_fit]

    while evals < max_evals:
        # Tournament selection
        offspring = np.empty_like(pop)
        for i in range(pop_size):
            candidates = rng.choice(pop_size, size=tournament_size, replace=False)
            winner = candidates[int(np.argmax(fitness[candidates]))]
            offspring[i] = pop[winner]

        # Uniform crossover
        for i in range(0, pop_size - 1, 2):
            if rng.random() < crossover_rate:
                mask = rng.random(n) < 0.5
                offspring[i, mask], offspring[i + 1, mask] = (
                    offspring[i + 1, mask].copy(),
                    offspring[i, mask].copy(),
                )

        # Bit-flip mutation
        for i in range(pop_size):
            mut_mask = rng.random(n) < mutation_rate
            offspring[i, mut_mask] = 1 - offspring[i, mut_mask]

        # Evaluate offspring
        off_fitness = problem.evaluate_batch(offspring)
        evals += pop_size

        # Elitist replacement: keep best from parent if better than worst offspring
        worst_off = int(np.argmin(off_fitness))
        if best_fit > off_fitness[worst_off]:
            offspring[worst_off] = best_sol.copy()
            off_fitness[worst_off] = best_fit

        pop = offspring
        fitness = off_fitness

        curr_best_idx = int(np.argmax(fitness))
        if fitness[curr_best_idx] > best_fit:
            best_sol = pop[curr_best_idx].copy()
            best_fit = float(fitness[curr_best_idx])

        history.append(best_fit)

    return OptResult(best_sol, best_fit, history, evals)


# ---------------------------------------------------------------------------
# Simulated Annealing
# ---------------------------------------------------------------------------


def simulated_annealing(
    problem: MaxCutProblem,
    max_evals: int = 25000,
    temp_init: float = 100.0,
    temp_min: float = 0.01,
    cooling_rate: float = 0.9995,
    seed: int | None = None,
) -> OptResult:
    """Classic SA with geometric cooling and single-bit-flip neighbourhood."""
    rng = np.random.default_rng(seed)
    n = problem.n

    current = rng.integers(0, 2, size=n).astype(np.int8)
    current_fit = problem.evaluate(current)
    evals = 1

    best_sol = current.copy()
    best_fit = current_fit
    history: list[float] = [best_fit]

    temp = temp_init

    while evals < max_evals:
        vertex = int(rng.integers(n))
        delta = problem.delta_flip(current, vertex)
        evals += 1

        if delta > 0 or rng.random() < np.exp(delta / max(temp, 1e-10)):
            current[vertex] = 1 - current[vertex]
            current_fit += delta
            if current_fit > best_fit:
                best_sol = current.copy()
                best_fit = current_fit

        temp = max(temp * cooling_rate, temp_min)
        if evals % 100 == 0:
            history.append(best_fit)

    return OptResult(best_sol, best_fit, history, evals)


# ---------------------------------------------------------------------------
# Simulated Quantum Annealing (SQA)
# ---------------------------------------------------------------------------


def simulated_quantum_annealing(
    problem: MaxCutProblem,
    max_evals: int = 25000,
    n_replicas: int = 8,
    temp: float = 2.0,
    gamma_init: float = 3.0,
    gamma_final: float = 0.01,
    seed: int | None = None,
) -> OptResult:
    """Simulated Quantum Annealing using path-integral Monte Carlo.

    Uses the Suzuki-Trotter decomposition with P replicas coupled along
    the imaginary-time dimension.  The transverse field Gamma decreases
    from gamma_init to gamma_final, simulating quantum annealing.
    """
    rng = np.random.default_rng(seed)
    n = problem.n
    p = n_replicas

    # Initialise replicas
    replicas = rng.integers(0, 2, size=(p, n)).astype(np.int8)
    replica_fits = np.array([problem.evaluate(replicas[k]) for k in range(p)])
    evals = p

    best_sol = replicas[int(np.argmax(replica_fits))].copy()
    best_fit = float(np.max(replica_fits))
    history: list[float] = [best_fit]

    # Total Monte Carlo steps
    total_steps = max_evals - evals
    gamma = gamma_init

    for step in range(total_steps):
        if evals >= max_evals:
            break

        # Anneal transverse field
        progress = step / max(total_steps - 1, 1)
        gamma = gamma_init * (1.0 - progress) + gamma_final * progress

        # Inter-replica coupling strength
        j_perp = -0.5 * temp * np.log(max(np.tanh(gamma / (p * temp)), 1e-10))

        # Pick a random replica and vertex
        k = int(rng.integers(p))
        v = int(rng.integers(n))

        # Classical energy change (within replica)
        delta_classical = problem.delta_flip(replicas[k], v) / p
        evals += 1

        # Quantum coupling energy change (between adjacent replicas)
        k_prev = (k - 1) % p
        k_next = (k + 1) % p
        spin = 2 * int(replicas[k, v]) - 1  # map {0,1} -> {-1,+1}
        spin_prev = 2 * int(replicas[k_prev, v]) - 1
        spin_next = 2 * int(replicas[k_next, v]) - 1
        # Flipping spin: coupling changes by -2 * spin * j_perp * (spin_prev + spin_next)
        delta_quantum = 2.0 * spin * j_perp * (spin_prev + spin_next)

        delta_total = delta_classical + delta_quantum

        if delta_total > 0 or rng.random() < np.exp(delta_total / max(temp, 1e-10)):
            replicas[k, v] = 1 - replicas[k, v]
            replica_fits[k] += problem.delta_flip(
                replicas[k], v
            )  # note: already flipped, so negate
            # Recompute properly
            replica_fits[k] = problem.evaluate(replicas[k])
            evals += 1

            if replica_fits[k] > best_fit:
                best_sol = replicas[k].copy()
                best_fit = float(replica_fits[k])

        if step % 200 == 0:
            history.append(best_fit)

    return OptResult(best_sol, best_fit, history, evals)
