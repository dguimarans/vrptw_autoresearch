"""
vrptw.py — Read-only infrastructure for the VRPTW auto-research loop.
Defines all data structures, instance parsing, utility functions, and the main entry point.
The AI-managed heuristics live in solver.py, which imports everything from here via:
    from vrptw import *
"""

from __future__ import annotations
import math
import sys
import time
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Customer:
    id: int
    x: float
    y: float
    demand: float
    ready: float
    due: float
    service: float


@dataclass
class Route:
    customers: list  # list[int] — customer indices; depot (0) is implicit start/end
    load: float = 0.0


class Problem:
    def __init__(self, customers: list, capacity: float):
        self.customers = customers  # index 0 = depot
        self.capacity = capacity
        self.n = len(customers) - 1  # number of customers excluding depot


# ---------------------------------------------------------------------------
# Parsing (Homberger / Solomon format)
# ---------------------------------------------------------------------------

def parse_instance(path: str) -> Problem:
    with open(path) as f:
        lines = f.readlines()

    capacity = 200.0
    customers: list = []
    past_vehicle = False
    vehicle_read = False
    past_cust_header = False

    for line in lines:
        trimmed = line.strip()
        if not trimmed:
            continue
        if trimmed.startswith("VEHICLE"):
            past_vehicle = True
            continue
        if past_vehicle and not vehicle_read and trimmed.startswith("NUMBER"):
            continue
        if past_vehicle and not vehicle_read:
            nums = []
            for p in trimmed.split():
                try:
                    nums.append(float(p))
                except ValueError:
                    pass
            if len(nums) >= 2:
                capacity = nums[1]
                vehicle_read = True
            continue
        if trimmed.startswith("CUST"):
            past_cust_header = True
            continue
        if not past_cust_header:
            continue
        parts = trimmed.split()
        if len(parts) < 7:
            continue
        try:
            nums = [float(p) for p in parts[:7]]
        except ValueError:
            continue
        customers.append(Customer(
            id=int(nums[0]),
            x=nums[1], y=nums[2],
            demand=nums[3],
            ready=nums[4], due=nums[5],
            service=nums[6],
        ))

    return Problem(customers, capacity)


# ---------------------------------------------------------------------------
# Utility functions — available to solver.py via `from vrptw import *`
# ---------------------------------------------------------------------------

def dist(a: Customer, b: Customer) -> float:
    dx = a.x - b.x
    dy = a.y - b.y
    return math.sqrt(dx * dx + dy * dy)


def route_distance(prob: Problem, customers: list) -> float:
    if not customers:
        return 0.0
    depot = prob.customers[0]
    d = dist(depot, prob.customers[customers[0]])
    for i in range(1, len(customers)):
        d += dist(prob.customers[customers[i - 1]], prob.customers[customers[i]])
    d += dist(prob.customers[customers[-1]], depot)
    return d


def route_feasible(prob: Problem, customers: list, extra_load: float = 0.0) -> bool:
    if not customers:
        return True
    depot = prob.customers[0]
    t = 0.0
    load = extra_load
    prev = depot
    for cid in customers:
        c = prob.customers[cid]
        load += c.demand
        if load > prob.capacity + 1e-9:
            return False
        t += dist(prev, c)
        if t < c.ready:
            t = c.ready
        if t > c.due + 1e-9:
            return False
        t += c.service
        prev = c
    return t + dist(prev, depot) <= depot.due + 1e-9


def best_insertion_in_route(prob: Problem, route: Route, c_idx: int) -> Optional[tuple]:
    """Return (cost_delta, position) for cheapest feasible insertion, or None."""
    c = prob.customers[c_idx]
    if route.load + c.demand > prob.capacity + 1e-9:
        return None
    depot = prob.customers[0]
    best: Optional[tuple] = None
    for pos in range(len(route.customers) + 1):
        prev = depot if pos == 0 else prob.customers[route.customers[pos - 1]]
        nxt  = depot if pos == len(route.customers) else prob.customers[route.customers[pos]]
        delta = dist(prev, c) + dist(c, nxt) - dist(prev, nxt)
        candidate = route.customers[:pos] + [c_idx] + route.customers[pos:]
        if route_feasible(prob, candidate, 0.0):
            if best is None or delta < best[0]:
                best = (delta, pos)
    return best


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def write_solution(prob: Problem, routes: list, vehicles: int, distance: float,
                   elapsed_ms: float, solution_path: str = "solution.txt") -> None:
    with open(solution_path, "w") as f:
        f.write(f"VEHICLES: {vehicles}\n")
        f.write(f"DISTANCE: {distance:.2f}\n")
        f.write(f"TIME_MS: {elapsed_ms:.1f}\n")
        for i, route in enumerate(routes):
            ids = " ".join(str(c) for c in route.customers)
            f.write(f"Route {i + 1}: {ids}\n")


# ---------------------------------------------------------------------------
# Main entry point — imports solve() from solver.py
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <instance_path> [solution_output_path]", file=sys.stderr)
        sys.exit(1)

    solution_path = sys.argv[2] if len(sys.argv) >= 3 else "solution.txt"

    from solver import solve

    start = time.time()
    prob = parse_instance(sys.argv[1])
    routes = solve(prob)
    elapsed_ms = (time.time() - start) * 1000.0

    routes = [r for r in routes if r.customers]
    vehicles = len(routes)
    distance = sum(route_distance(prob, r.customers) for r in routes)

    print(f"RESULT_VEHICLES: {vehicles}")
    print(f"RESULT_DISTANCE: {distance:.2f}")
    print(f"RESULT_TIME_MS: {elapsed_ms:.1f}")

    write_solution(prob, routes, vehicles, distance, elapsed_ms, solution_path)

    print("\n--- Solution Detail ---", file=sys.stderr)
    for i, route in enumerate(routes):
        d = route_distance(prob, route.customers)
        ids = "->".join(str(c) for c in route.customers)
        print(f"Route {i+1:3d}: [{ids}]  dist={d:.2f}", file=sys.stderr)
    print(
        f"Vehicles: {vehicles}  Total distance: {distance:.2f}  Time: {elapsed_ms:.1f}ms",
        file=sys.stderr,
    )
