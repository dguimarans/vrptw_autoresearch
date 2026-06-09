from vrptw import *
import numpy as np

# DEPENDENCY: numpy

# ---------------------------------------------------------------------------
# Distance matrix — precomputed once per solve() call.
# Shadows route_distance, route_feasible, and best_insertion_in_route from
# vrptw.py with versions that use O(1) array lookups instead of math.sqrt.
# ---------------------------------------------------------------------------

_dist_matrix: "np.ndarray | None" = None


def _init_dist_matrix(prob: Problem) -> None:
    global _dist_matrix
    coords = np.array([(c.x, c.y) for c in prob.customers])
    diff = coords[:, None, :] - coords[None, :, :]
    _dist_matrix = np.sqrt((diff ** 2).sum(axis=2))


def route_distance(prob: Problem, customers: list) -> float:
    if not customers:
        return 0.0
    d = _dist_matrix[0, customers[0]]
    for i in range(1, len(customers)):
        d += _dist_matrix[customers[i - 1], customers[i]]
    d += _dist_matrix[customers[-1], 0]
    return float(d)


def route_feasible(prob: Problem, customers: list, extra_load: float = 0.0) -> bool:
    if not customers:
        return True
    t = 0.0
    load = extra_load
    prev_id = 0
    for cid in customers:
        c = prob.customers[cid]
        load += c.demand
        if load > prob.capacity + 1e-9:
            return False
        t += _dist_matrix[prev_id, cid]
        if t < c.ready:
            t = c.ready
        if t > c.due + 1e-9:
            return False
        t += c.service
        prev_id = cid
    return t + _dist_matrix[prev_id, 0] <= prob.customers[0].due + 1e-9


def best_insertion_in_route(prob: Problem, route: Route, c_idx: int):
    c = prob.customers[c_idx]
    if route.load + c.demand > prob.capacity + 1e-9:
        return None
    best = None
    customers = route.customers
    for pos in range(len(customers) + 1):
        prev_id = 0 if pos == 0 else customers[pos - 1]
        nxt_id  = 0 if pos == len(customers) else customers[pos]
        delta = (_dist_matrix[prev_id, c_idx] + _dist_matrix[c_idx, nxt_id]
                 - _dist_matrix[prev_id, nxt_id])
        candidate = customers[:pos] + [c_idx] + customers[pos:]
        if route_feasible(prob, candidate, 0.0):
            if best is None or delta < best[0]:
                best = (delta, pos)
    return best


# ---------------------------------------------------------------------------
# Regret-2 construction heuristic
# ---------------------------------------------------------------------------

def regret2_construction(prob: Problem) -> list:
    routes = []
    unrouted = list(range(1, prob.n + 1))
    depot = prob.customers[0]

    while unrouted:
        best_ui = 0
        best_regret = float('-inf')
        best_route_idx = None
        best_pos = 0

        for ui, c_idx in enumerate(unrouted):
            options = []
            for ri, route in enumerate(routes):
                result = best_insertion_in_route(prob, route, c_idx)
                if result is not None:
                    cost, pos = result
                    options.append((cost, ri, pos))

            c = prob.customers[c_idx]
            new_route_cost = dist(depot, c) + dist(c, depot)
            options.append((new_route_cost, None, 0))

            options.sort(key=lambda x: x[0])

            cost1 = options[0][0]
            cost2 = options[1][0] if len(options) >= 2 else cost1 + 1e9
            regret = cost2 - cost1

            if regret > best_regret:
                best_regret = regret
                best_ui = ui
                best_route_idx = options[0][1]
                best_pos = options[0][2]

        c_idx = unrouted.pop(best_ui)

        if best_route_idx is None:
            routes.append(Route(customers=[c_idx], load=prob.customers[c_idx].demand))
        else:
            routes[best_route_idx].customers.insert(best_pos, c_idx)
            routes[best_route_idx].load += prob.customers[c_idx].demand

    return routes


# ---------------------------------------------------------------------------
# 2-opt within each route
# ---------------------------------------------------------------------------

def apply_2opt_intra(prob: Problem, routes: list) -> bool:
    any_improved = False
    for route in routes:
        n = len(route.customers)
        if n < 3:
            continue
        improved = True
        while improved:
            improved = False
            found = False
            for i in range(n - 1):
                if found:
                    break
                for j in range(i + 2, n):
                    ci  = route.customers[i]
                    ci1 = route.customers[i + 1]
                    cj  = route.customers[j]
                    cj1 = route.customers[j + 1] if j + 1 < n else 0

                    old_d = (dist(prob.customers[ci],  prob.customers[ci1]) +
                             dist(prob.customers[cj],  prob.customers[cj1]))
                    new_d = (dist(prob.customers[ci],  prob.customers[cj]) +
                             dist(prob.customers[ci1], prob.customers[cj1]))

                    if new_d < old_d - 1e-9:
                        route.customers[i + 1:j + 1] = route.customers[i + 1:j + 1][::-1]
                        if route_feasible(prob, route.customers, 0.0):
                            improved = True
                            any_improved = True
                            found = True
                            break
                        else:
                            route.customers[i + 1:j + 1] = route.customers[i + 1:j + 1][::-1]
    return any_improved


# ---------------------------------------------------------------------------
# Or-opt: move a segment of 1, 2, or 3 customers (intra- and inter-route)
# ---------------------------------------------------------------------------

def apply_or_opt(prob: Problem, routes: list) -> bool:
    improved = True
    any_improved = False
    while improved:
        improved = False
        n_routes = len(routes)
        found = False
        for seg_len in range(1, 4):
            if found:
                break
            for ri in range(n_routes):
                if found:
                    break
                if len(routes[ri].customers) < seg_len:
                    continue
                ri_len = len(routes[ri].customers)
                for seg_start in range(ri_len - seg_len + 1):
                    if found:
                        break
                    seg = routes[ri].customers[seg_start:seg_start + seg_len]
                    for rj in range(n_routes):
                        if found:
                            break
                        rj_len = len(routes[rj].customers)
                        for ins_pos in range(rj_len + 1):
                            same = (ri == rj)
                            if same and seg_start <= ins_pos <= seg_start + seg_len:
                                continue

                            new_ri = routes[ri].customers[:]
                            del new_ri[seg_start:seg_start + seg_len]

                            new_rj = new_ri[:] if same else routes[rj].customers[:]
                            adj = min(ins_pos, len(new_rj))
                            new_rj[adj:adj] = seg

                            if not route_feasible(prob, new_rj, 0.0):
                                continue
                            if same and not route_feasible(prob, new_ri, 0.0):
                                continue

                            old_d = route_distance(prob, routes[ri].customers)
                            if not same:
                                old_d += route_distance(prob, routes[rj].customers)
                            new_d = route_distance(prob, new_rj)
                            if not same:
                                new_d += route_distance(prob, new_ri)

                            if new_d < old_d - 1e-9:
                                routes[ri].customers = new_rj if same else new_ri
                                routes[ri].load = sum(
                                    prob.customers[c].demand for c in routes[ri].customers
                                )
                                if not same:
                                    routes[rj].customers = new_rj
                                    routes[rj].load = sum(
                                        prob.customers[c].demand for c in routes[rj].customers
                                    )
                                improved = True
                                any_improved = True
                                found = True
                                break
    return any_improved


# ---------------------------------------------------------------------------
# Try to reduce vehicle count by relocating all customers from smallest route
# ---------------------------------------------------------------------------

def try_reduce_vehicles(prob: Problem, routes: list) -> bool:
    routes.sort(key=lambda r: len(r.customers))
    for ri in range(len(routes)):
        if not routes[ri].customers:
            continue
        candidates = routes[ri].customers[:]

        scratch = [Route(customers=r.customers[:], load=r.load) for r in routes]
        scratch[ri].customers = []
        scratch[ri].load = 0.0

        all_placed = True
        for c_idx in candidates:
            placed = False
            for rj in range(len(scratch)):
                if rj == ri:
                    continue
                result = best_insertion_in_route(prob, scratch[rj], c_idx)
                if result is not None:
                    _, pos = result
                    scratch[rj].customers.insert(pos, c_idx)
                    scratch[rj].load += prob.customers[c_idx].demand
                    placed = True
                    break
            if not placed:
                all_placed = False
                break

        if all_placed:
            routes[:] = [r for r in scratch if r.customers]
            return True
    return False


# ---------------------------------------------------------------------------
# Inter-route 3-opt: swap three consecutive customers between different routes
# ---------------------------------------------------------------------------

def apply_inter_route_2opt(prob: Problem, routes: list) -> bool:
    improved = False
    for i in range(len(routes)):
        for j in range(i + 1, len(routes)):
            ri_len = len(routes[i].customers)
            rj_len = len(routes[j].customers)
            if ri_len < 3 or rj_len < 3:
                continue
            for x in range(ri_len - 2):
                for y in range(rj_len - 2):
                    ci  = routes[i].customers[x]
                    ci1 = routes[i].customers[x + 1]
                    ci2 = routes[i].customers[x + 2]
                    cj  = routes[j].customers[y]
                    cj1 = routes[j].customers[y + 1]
                    cj2 = routes[j].customers[y + 2]

                    old_d = (route_distance(prob, routes[i].customers) +
                             route_distance(prob, routes[j].customers))

                    new_ri = routes[i].customers[:]
                    new_ri[x:x + 3] = [cj, cj1, cj2]
                    new_rj = routes[j].customers[:]
                    new_rj[y:y + 3] = [ci, ci1, ci2]

                    if not route_feasible(prob, new_ri, 0.0) or not route_feasible(prob, new_rj, 0.0):
                        continue

                    new_d = route_distance(prob, new_ri) + route_distance(prob, new_rj)
                    if new_d < old_d - 1e-9:
                        routes[i].customers = new_ri
                        routes[j].customers = new_rj
                        improved = True
    return improved


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def solve(prob: Problem) -> list:
    _init_dist_matrix(prob)
    routes = regret2_construction(prob)
    routes = [r for r in routes if r.customers]

    while try_reduce_vehicles(prob, routes):
        pass

    apply_2opt_intra(prob, routes)

    while True:
        imp   = apply_or_opt(prob, routes)
        red   = try_reduce_vehicles(prob, routes)
        inter = apply_inter_route_2opt(prob, routes)
        if not imp and not red and not inter:
            break

    return [r for r in routes if r.customers]