use super::*;

// ---------------------------------------------------------------------------
// Regret-2 construction heuristic
// ---------------------------------------------------------------------------

fn regret2_construction(prob: &Problem) -> Vec<Route> {
    let mut routes: Vec<Route> = Vec::new();
    let mut unrouted: Vec<usize> = (1..=prob.n).collect();
    let depot = &prob.customers[0];

    while !unrouted.is_empty() {
        let mut best_ui = 0usize;
        let mut best_regret = f64::NEG_INFINITY;
        let mut best_route_idx: Option<usize> = None;
        let mut best_pos = 0usize;

        for (ui, &c_idx) in unrouted.iter().enumerate() {
            let mut options: Vec<(f64, usize, usize)> = Vec::new();
            for (ri, route) in routes.iter().enumerate() {
                if let Some((cost, pos)) = best_insertion_in_route(prob, route, c_idx) {
                    options.push((cost, ri, pos));
                }
            }

            let c = &prob.customers[c_idx];
            let new_route_cost = dist(depot, c) + dist(c, depot);
            options.push((new_route_cost, usize::MAX, 0));

            options.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

            let cost1 = options[0].0;
            let cost2 = if options.len() >= 2 { options[1].0 } else { cost1 + 1e9 };
            let regret = cost2 - cost1;

            if regret > best_regret {
                best_regret = regret;
                best_ui = ui;
                best_route_idx = if options[0].1 == usize::MAX { None } else { Some(options[0].1) };
                best_pos = options[0].2;
            }
        }

        let c_idx = unrouted.remove(best_ui);

        match best_route_idx {
            None => {
                routes.push(Route {
                    customers: vec![c_idx],
                    load: prob.customers[c_idx].demand,
                });
            }
            Some(ri) => {
                routes[ri].customers.insert(best_pos, c_idx);
                routes[ri].load += prob.customers[c_idx].demand;
            }
        }
    }

    routes
}

// ---------------------------------------------------------------------------
// 2-opt within each route
// ---------------------------------------------------------------------------

fn apply_2opt_intra(prob: &Problem, routes: &mut Vec<Route>) -> bool {
    let mut any = false;
    for route in routes.iter_mut() {
        let n = route.customers.len();
        if n < 3 {
            continue;
        }
        let mut improved = true;
        while improved {
            improved = false;
            'swap: for i in 0..n - 1 {
                for j in i + 2..n {
                    let ci = route.customers[i];
                    let ci1 = route.customers[i + 1];
                    let cj = route.customers[j];
                    let cj1 = if j + 1 < n { route.customers[j + 1] } else { 0 };
                    let old_d = dist(&prob.customers[ci], &prob.customers[ci1])
                        + dist(&prob.customers[cj], &prob.customers[cj1]);
                    let new_d = dist(&prob.customers[ci], &prob.customers[cj])
                        + dist(&prob.customers[ci1], &prob.customers[cj1]);
                    if new_d < old_d - 1e-9 {
                        route.customers[i + 1..=j].reverse();
                        if route_feasible(prob, &route.customers, 0.0) {
                            improved = true;
                            any = true;
                            break 'swap;
                        } else {
                            route.customers[i + 1..=j].reverse();
                        }
                    }
                }
            }
        }
    }
    any
}

// ---------------------------------------------------------------------------
// Or-opt: move a segment of 1, 2, or 3 customers (intra- and inter-route)
// ---------------------------------------------------------------------------

fn apply_or_opt(prob: &Problem, routes: &mut Vec<Route>) -> bool {
    let mut improved = true;
    let mut any = false;
    while improved {
        improved = false;
        let n_routes = routes.len();
        'outer: for seg_len in 1usize..=3 {
            for ri in 0..n_routes {
                if routes[ri].customers.len() < seg_len {
                    continue;
                }
                let ri_len = routes[ri].customers.len();
                for seg_start in 0..=ri_len - seg_len {
                    let seg: Vec<usize> =
                        routes[ri].customers[seg_start..seg_start + seg_len].to_vec();

                    for rj in 0..n_routes {
                        let rj_len = routes[rj].customers.len();
                        for ins_pos in 0..=rj_len {
                            let same = ri == rj;
                            if same && ins_pos >= seg_start && ins_pos <= seg_start + seg_len {
                                continue;
                            }

                            let mut new_ri: Vec<usize> = routes[ri].customers.clone();
                            new_ri.drain(seg_start..seg_start + seg_len);

                            let mut new_rj: Vec<usize> = if same {
                                new_ri.clone()
                            } else {
                                routes[rj].customers.clone()
                            };
                            let adj = if same {
                                if ins_pos > seg_start {
                                    ins_pos.saturating_sub(seg_len)
                                } else {
                                    ins_pos
                                }
                                .min(new_rj.len())
                            } else {
                                ins_pos.min(new_rj.len())
                            };
                            for (k, &s) in seg.iter().enumerate() {
                                new_rj.insert(adj + k, s);
                            }
                            if same {
                                new_ri = new_rj.clone();
                            }

                            if !route_feasible(prob, &new_rj, 0.0) {
                                continue;
                            }
                            if !same && !route_feasible(prob, &new_ri, 0.0) {
                                continue;
                            }

                            let old_d = route_distance(prob, &routes[ri].customers)
                                + if same { 0.0 } else { route_distance(prob, &routes[rj].customers) };
                            let new_d_ri = if same { 0.0 } else { route_distance(prob, &new_ri) };
                            let new_d_rj = route_distance(prob, &new_rj);
                            let new_d = if same { new_d_rj } else { new_d_ri + new_d_rj };

                            if new_d < old_d - 1e-9 {
                                routes[ri].customers = if same { new_rj.clone() } else { new_ri };
                                routes[ri].load = routes[ri]
                                    .customers
                                    .iter()
                                    .map(|&c| prob.customers[c].demand)
                                    .sum();
                                if !same {
                                    routes[rj].customers = new_rj;
                                    routes[rj].load = routes[rj]
                                        .customers
                                        .iter()
                                        .map(|&c| prob.customers[c].demand)
                                        .sum();
                                }
                                improved = true;
                                any = true;
                                break 'outer;
                            }
                        }
                    }
                }
            }
        }
    }
    any
}

// ---------------------------------------------------------------------------
// Try to reduce vehicle count by relocating all customers from the smallest
// route into other routes.
// ---------------------------------------------------------------------------

fn try_reduce_vehicles(prob: &Problem, routes: &mut Vec<Route>) -> bool {
    // Attempt to eliminate exactly one route per call (the smallest).
    // Insertions are tested and committed on a scratch copy so each successive
    // placement sees the route already modified by prior insertions in this
    // attempt — preventing the infeasibility that arose from checking positions
    // against the original route and then applying all changes at once.
    routes.sort_by_key(|r| r.customers.len());
    for ri in 0..routes.len() {
        if routes[ri].customers.is_empty() {
            continue;
        }
        let candidates: Vec<usize> = routes[ri].customers.clone();

        let mut scratch = routes.clone();
        scratch[ri].customers.clear();
        scratch[ri].load = 0.0;

        let mut all_placed = true;
        for &c_idx in &candidates {
            let mut placed = false;
            for rj in 0..scratch.len() {
                if rj == ri {
                    continue;
                }
                if let Some((_, pos)) = best_insertion_in_route(prob, &scratch[rj], c_idx) {
                    scratch[rj].customers.insert(pos, c_idx);
                    scratch[rj].load += prob.customers[c_idx].demand;
                    placed = true;
                    break;
                }
            }
            if !placed {
                all_placed = false;
                break;
            }
        }

        if all_placed {
            *routes = scratch;
            routes.retain(|r| !r.customers.is_empty());
            return true;
        }
    }
    false
}

// ---------------------------------------------------------------------------
// Public entry point called by main()
// ---------------------------------------------------------------------------

pub fn solve(prob: &Problem) -> Vec<Route> {
    let mut routes = regret2_construction(prob);
    routes.retain(|r| !r.customers.is_empty());

    loop {
        if !try_reduce_vehicles(prob, &mut routes) {
            break;
        }
    }

    apply_2opt_intra(prob, &mut routes);

    loop {
        let imp = apply_or_opt(prob, &mut routes);
        let red = try_reduce_vehicles(prob, &mut routes);
        if !imp && !red {
            break;
        }
    }

    routes.retain(|r| !r.customers.is_empty());
    routes
}
