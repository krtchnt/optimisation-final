"""Maximum Cut Problem on weighted undirected graphs."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


class MaxCutProblem:
    """Maximum Cut Problem.

    Given a weighted undirected graph G = (V, E, w), partition the vertex set V
    into two disjoint sets S and V\\S to maximise the total weight of edges
    crossing the partition (the cut).
    """

    def __init__(
        self,
        n_vertices: int,
        edges: list[tuple[int, int]],
        weights: list[float] | None = None,
    ) -> None:
        self.n: int = n_vertices
        self.edges: list[tuple[int, int]] = edges
        self.weights: list[float] = (
            weights if weights is not None else [1.0] * len(edges)
        )

        # Adjacency matrix for vectorised evaluation
        self.adj: NDArray[np.float64] = np.zeros((self.n, self.n))
        for (u, v), w in zip(self.edges, self.weights):
            self.adj[u, v] = w
            self.adj[v, u] = w

        # Adjacency list for efficient delta evaluation
        self.adj_list: list[list[tuple[int, float]]] = [[] for _ in range(self.n)]
        for (u, v), w in zip(self.edges, self.weights):
            self.adj_list[u].append((v, w))
            self.adj_list[v].append((u, w))

    def evaluate(self, partition: NDArray[np.int8]) -> float:
        """Compute the cut value for a binary partition vector."""
        cut = 0.0
        for (u, v), w in zip(self.edges, self.weights):
            if partition[u] != partition[v]:
                cut += w
        return cut

    def evaluate_batch(self, population: NDArray[np.int8]) -> NDArray[np.float64]:
        """Evaluate multiple partitions simultaneously."""
        result = np.zeros(population.shape[0])
        for (u, v), w in zip(self.edges, self.weights):
            result += w * np.abs(population[:, u].astype(float) - population[:, v])
        return result

    def delta_flip(self, partition: NDArray[np.int8], vertex: int) -> float:
        """Compute change in cut value if a single vertex is flipped.

        Returns a positive value if the flip improves the cut.
        """
        delta = 0.0
        for neighbour, weight in self.adj_list[vertex]:
            if partition[neighbour] == partition[vertex]:
                delta += weight  # edge becomes cut
            else:
                delta -= weight  # edge becomes uncut
        return delta

    @staticmethod
    def random_instance(
        n: int,
        density: float = 0.5,
        weight_range: tuple[float, float] = (1.0, 10.0),
        seed: int | None = None,
    ) -> MaxCutProblem:
        """Generate a random Erdos-Renyi weighted graph."""
        rng = np.random.default_rng(seed)
        edges: list[tuple[int, int]] = []
        weights: list[float] = []
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < density:
                    edges.append((i, j))
                    weights.append(float(rng.uniform(*weight_range)))
        return MaxCutProblem(n, edges, weights)
