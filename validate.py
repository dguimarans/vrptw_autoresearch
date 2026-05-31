#!/usr/bin/env python3
"""
VRPTW feasibility validator.
Usage: python3 validate.py <instance_path> <solution_path>
Exit 0 + prints FEASIBLE if all constraints satisfied.
Exit 1 + prints INFEASIBLE with a violation report if any constraint fails.
"""
import sys
import math


def parse_instance(path):
    customers = []
    capacity = None
    past_vehicle = False
    vehicle_read = False
    past_cust_header = False

    with open(path) as f:
        for line in f:
            t = line.strip()
            if not t:
                continue
            if t.startswith("VEHICLE"):
                past_vehicle = True
                continue
            if past_vehicle and not vehicle_read and t.startswith("NUMBER"):
                continue
            if past_vehicle and not vehicle_read:
                parts = t.split()
                if len(parts) >= 2:
                    try:
                        capacity = float(parts[1])
                        vehicle_read = True
                    except ValueError:
                        pass
                continue
            if t.startswith("CUST"):
                past_cust_header = True
                continue
            if not past_cust_header:
                continue
            parts = t.split()
            if len(parts) < 7:
                continue
            try:
                customers.append({
                    "id":      int(float(parts[0])),
                    "x":       float(parts[1]),
                    "y":       float(parts[2]),
                    "demand":  float(parts[3]),
                    "ready":   float(parts[4]),
                    "due":     float(parts[5]),
                    "service": float(parts[6]),
                })
            except ValueError:
                pass

    if capacity is None:
        raise ValueError("Capacity not found in instance file")
    return customers, capacity


def parse_solution(path):
    routes = []
    reported_vehicles = None
    reported_distance = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("VEHICLES:"):
                reported_vehicles = int(line.split(":", 1)[1].strip())
            elif line.startswith("DISTANCE:"):
                reported_distance = float(line.split(":", 1)[1].strip())
            elif line.startswith("Route "):
                parts = line.split(":", 1)
                if len(parts) == 2 and parts[1].strip():
                    ids = [int(x) for x in parts[1].strip().split()]
                    routes.append(ids)

    return reported_vehicles, reported_distance, routes


def _dist(a, b):
    return math.sqrt((a["x"] - b["x"]) ** 2 + (a["y"] - b["y"]) ** 2)


def validate(customers, capacity, routes):
    """Return list of violation strings; empty list means feasible."""
    depot = customers[0]
    n = len(customers) - 1
    violations = []

    # --- Coverage ---
    visit_count = {}
    for ri, route in enumerate(routes, 1):
        for cid in route:
            if cid == 0:
                violations.append(f"Route {ri}: depot (id 0) appears as a mid-route stop")
            elif cid < 0 or cid > n:
                violations.append(f"Route {ri}: customer id {cid} out of range [1, {n}]")
            else:
                visit_count[cid] = visit_count.get(cid, 0) + 1

    for cid, cnt in visit_count.items():
        if cnt > 1:
            violations.append(f"Customer {cid} visited {cnt} times (must be exactly once)")

    for cid in range(1, n + 1):
        if visit_count.get(cid, 0) == 0:
            violations.append(f"Customer {cid} never visited")

    # --- Per-route checks ---
    for ri, route in enumerate(routes, 1):
        if not route:
            violations.append(f"Route {ri}: empty (no customers)")
            continue

        # Capacity
        load = sum(
            customers[cid]["demand"]
            for cid in route
            if 0 < cid <= n
        )
        if load > capacity + 1e-9:
            violations.append(
                f"Route {ri}: capacity exceeded ({load:.1f} > {capacity:.1f})"
            )

        # Time windows — simulate route execution
        t = 0.0
        prev = depot
        for cid in route:
            if cid <= 0 or cid > n:
                continue
            c = customers[cid]
            travel = _dist(prev, c)
            t += travel
            if t < c["ready"]:
                t = c["ready"]          # wait at customer until window opens
            if t > c["due"] + 1e-9:
                violations.append(
                    f"Route {ri}: TW violated at customer {cid} "
                    f"(service starts {t:.2f}, due {c['due']:.2f})"
                )
            t += c["service"]
            prev = c

        # Depot return within depot's time window
        t_return = t + _dist(prev, depot)
        if t_return > depot["due"] + 1e-9:
            violations.append(
                f"Route {ri}: depot return at {t_return:.2f} exceeds depot due {depot['due']:.2f}"
            )

    return violations


def compute_distance(customers, routes):
    depot = customers[0]
    total = 0.0
    for route in routes:
        if not route:
            continue
        total += _dist(depot, customers[route[0]])
        for i in range(1, len(route)):
            total += _dist(customers[route[i - 1]], customers[route[i]])
        total += _dist(customers[route[-1]], depot)
    return total


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: validate.py <instance_path> <solution_path>")
        sys.exit(2)

    customers, capacity = parse_instance(sys.argv[1])
    reported_vehicles, reported_distance, routes = parse_solution(sys.argv[2])

    violations = validate(customers, capacity, routes)

    if violations:
        print("INFEASIBLE")
        for v in violations:
            print(f"  {v}")
        sys.exit(1)

    computed_dist = round(compute_distance(customers, routes), 2)
    note = ""
    if reported_distance is not None and abs(computed_dist - reported_distance) > 0.11:
        note = f"  [WARNING: solver reported {reported_distance:.2f}, validator computed {computed_dist:.2f}]"
    print(f"FEASIBLE  vehicles={len(routes)}  distance={computed_dist:.2f}{note}")
    sys.exit(0)
