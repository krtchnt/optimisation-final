"""Driver for Max-Cut optimisation experiments.

Compares Quantum-Inspired Cosmological Optimisation (QICO) against baseline
algorithms (Genetic Algorithm, Simulated Annealing, Simulated Quantum
Annealing) on random weighted graph instances.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .baselines import (
    OptResult,
    genetic_algorithm,
    simulated_annealing,
    simulated_quantum_annealing,
)
from .problem import MaxCutProblem
from .qico import QICO, QICOResult

# ---------------------------------------------------------------------------
# Experiment configuration
# ---------------------------------------------------------------------------

GRAPH_CONFIGS: list[dict[str, int | float]] = [
    {"n": 20, "density": 0.5, "max_evals": 10000},
    {"n": 50, "density": 0.4, "max_evals": 30000},
    {"n": 100, "density": 0.3, "max_evals": 60000},
]

N_TRIALS = 10
BASE_SEED = 42


def run_experiment(
    problem: MaxCutProblem,
    max_evals: int,
    seed: int,
) -> dict[str, OptResult | QICOResult]:
    """Run all algorithms on a single instance with a given seed."""
    results: dict[str, OptResult | QICOResult] = {}

    results["QICO"] = QICO(
        pop_size=50,
        max_evals=max_evals,
        seed=seed,
    ).optimize(problem)

    results["GA"] = genetic_algorithm(
        problem,
        pop_size=50,
        max_evals=max_evals,
        seed=seed,
    )

    results["SA"] = simulated_annealing(
        problem,
        max_evals=max_evals,
        seed=seed,
    )

    results["SQA"] = simulated_quantum_annealing(
        problem,
        max_evals=max_evals,
        seed=seed,
    )

    return results


def print_table(
    all_results: dict[str, list[float]],
    n: int,
    n_edges: int,
) -> None:
    """Print a formatted comparison table."""
    header = f"{'Algorithm':<10} {'Mean':>10} {'Std':>10} {'Best':>10} {'Worst':>10}"
    print(f"\n  n={n}, |E|={n_edges}")
    print(f"  {header}")
    print(f"  {'-' * len(header)}")
    for name, fits in all_results.items():
        arr = np.array(fits)
        line = (
            f"  {name:<10} {arr.mean():>10.2f} {arr.std():>10.2f}"
            + f" {arr.max():>10.2f} {arr.min():>10.2f}"
        )
        print(line)


def plot_convergence(
    histories: dict[str, list[list[float]]],
    n: int,
    output_dir: Path,
) -> None:
    """Plot mean convergence curves across trials."""
    fig, ax = plt.subplots(figsize=(8, 5))  # pyright: ignore[reportUnknownMemberType]
    colours = {"QICO": "#e63946", "GA": "#457b9d", "SA": "#2a9d8f", "SQA": "#e9c46a"}

    for name, trial_histories in histories.items():
        # Align histories to same length (shortest)
        min_len = min(len(h) for h in trial_histories)
        aligned = np.array([h[:min_len] for h in trial_histories])
        mean_curve = aligned.mean(axis=0)
        std_curve = aligned.std(axis=0)
        x = np.arange(min_len)

        colour = colours.get(name, "#333333")
        _ = ax.plot(x, mean_curve, label=name, color=colour, linewidth=2)  # pyright: ignore[reportUnknownMemberType]
        _ = ax.fill_between(  # pyright: ignore[reportUnknownMemberType]
            x,
            mean_curve - std_curve,
            mean_curve + std_curve,
            alpha=0.15,
            color=colour,
        )

    _ = ax.set_xlabel("Generation / Checkpoint")  # pyright: ignore[reportUnknownMemberType]
    _ = ax.set_ylabel("Best Cut Value")  # pyright: ignore[reportUnknownMemberType]
    _ = ax.set_title(f"Convergence Comparison (n = {n})")  # pyright: ignore[reportUnknownMemberType]
    _ = ax.legend()  # pyright: ignore[reportUnknownMemberType]
    ax.grid(alpha=0.3)  # pyright: ignore[reportUnknownMemberType]
    fig.tight_layout()

    output_path = output_dir / f"convergence_n{n}.png"
    fig.savefig(output_path, dpi=150)  # pyright: ignore[reportUnknownMemberType]
    plt.close(fig)
    print(f"  Saved: {output_path}")


def main() -> None:
    output_dir = Path(__file__).resolve().parent.parent / "slides" / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  Max-Cut Optimisation: QICO vs Baselines")
    print("=" * 60)

    for cfg in GRAPH_CONFIGS:
        n = int(cfg["n"])
        density = float(cfg["density"])
        max_evals = int(cfg["max_evals"])

        # Generate a fixed problem instance for this size
        problem = MaxCutProblem.random_instance(n, density=density, seed=BASE_SEED)
        n_edges = len(problem.edges)

        print(f"\n{'-' * 60}")
        print(f"  Graph: n={n}, density={density}, |E|={n_edges}")
        print(f"  Budget: {max_evals} evaluations, {N_TRIALS} trials")
        print(f"{'-' * 60}")

        all_fits: dict[str, list[float]] = {
            "QICO": [],
            "GA": [],
            "SA": [],
            "SQA": [],
        }
        all_histories: dict[str, list[list[float]]] = {
            "QICO": [],
            "GA": [],
            "SA": [],
            "SQA": [],
        }

        for trial in range(N_TRIALS):
            trial_seed = BASE_SEED + trial + 1
            t0 = time.perf_counter()
            results = run_experiment(problem, max_evals, trial_seed)
            elapsed = time.perf_counter() - t0

            for name, res in results.items():
                all_fits[name].append(res.best_fitness)
                all_histories[name].append(res.history)

            best_this = max(res.best_fitness for res in results.values())
            msg = (
                f"  Trial {trial + 1:>2}/{N_TRIALS}:"
                + f" best={best_this:.2f} ({elapsed:.2f}s)"
            )
            print(msg, file=sys.stderr)

        print_table(all_fits, n, n_edges)
        plot_convergence(all_histories, n, output_dir)


if __name__ == "__main__":
    main()
