use std::env;
use std::fs;
use std::time::Instant;

// ---------------------------------------------------------------------------
// Data structures
// ---------------------------------------------------------------------------

#[derive(Debug, Clone)]
struct Customer {
    id: usize,
    x: f64,
    y: f64,
    demand: f64,
    ready: f64,
    due: f64,
    service: f64,
}

#[derive(Debug, Clone)]
struct Route {
    customers: Vec<usize>, // customer indices (depot = 0 not stored; implicit start/end)
    load: f64,
}

struct Problem {
    customers: Vec<Customer>, // index 0 = depot
    capacity: f64,
    n: usize, // number of customers (excluding depot)
}

// ---------------------------------------------------------------------------
// Parsing (Homberger / Solomon format)
// ---------------------------------------------------------------------------

fn parse_instance(path: &str) -> Problem {
    let text = fs::read_to_string(path).expect("Cannot read instance file");
    let mut capacity = 200.0f64;
    let mut customers: Vec<Customer> = Vec::new();
    let mut past_vehicle = false;
    let mut vehicle_read = false;
    let mut past_cust_header = false;

    for line in text.lines() {
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }
        if trimmed.starts_with("VEHICLE") {
            past_vehicle = true;
            continue;
        }
        if past_vehicle && !vehicle_read && trimmed.starts_with("NUMBER") {
            continue; // skip the column header
        }
        if past_vehicle && !vehicle_read {
            let parts: Vec<f64> = trimmed.split_whitespace().filter_map(|v| v.parse().ok()).collect();
            if parts.len() >= 2 {
                capacity = parts[1];
                vehicle_read = true;
            }
            continue;
        }
        if trimmed.starts_with("CUST") {
            past_cust_header = true;
            continue;
        }
        if !past_cust_header {
            continue;
        }
        let parts: Vec<f64> = trimmed.split_whitespace().filter_map(|v| v.parse().ok()).collect();
        if parts.len() < 7 {
            continue;
        }
        customers.push(Customer {
            id: parts[0] as usize,
            x: parts[1],
            y: parts[2],
            demand: parts[3],
            ready: parts[4],
            due: parts[5],
            service: parts[6],
        });
    }

    let n = customers.len().saturating_sub(1);
    Problem { customers, capacity, n }
}

// ---------------------------------------------------------------------------
// Euclidean distance
// ---------------------------------------------------------------------------

#[inline]
fn dist(a: &Customer, b: &Customer) -> f64 {
    let dx = a.x - b.x;
    let dy = a.y - b.y;
    (dx * dx + dy * dy).sqrt()
}

// ---------------------------------------------------------------------------
// Route utilities
// ---------------------------------------------------------------------------

fn route_distance(prob: &Problem, customers: &[usize]) -> f64 {
    if customers.is_empty() {
        return 0.0;
    }
    let depot = &prob.customers[0];
    let mut d = dist(depot, &prob.customers[customers[0]]);
    for i in 1..customers.len() {
        d += dist(&prob.customers[customers[i - 1]], &prob.customers[customers[i]]);
    }
    d += dist(&prob.customers[*customers.last().unwrap()], depot);
    d
}

// Returns false if TW or capacity violated.
fn route_feasible(prob: &Problem, customers: &[usize], extra_load: f64) -> bool {
    if customers.is_empty() {
        return true;
    }
    let depot = &prob.customers[0];
    let mut t = 0.0f64;
    let mut load = extra_load;
    let mut prev = depot;
    for &cid in customers {
        let c = &prob.customers[cid];
        load += c.demand;
        if load > prob.capacity + 1e-9 {
            return false;
        }
        t += dist(prev, c);
        if t < c.ready {
            t = c.ready;
        }
        if t > c.due + 1e-9 {
            return false;
        }
        t += c.service;
        prev = c;
    }
    let depot_arrive = t + dist(prev, depot);
    depot_arrive <= depot.due + 1e-9
}

// ---------------------------------------------------------------------------
// Best feasible insertion position in a single route.
// Returns (cost_delta, position) or None.
// ---------------------------------------------------------------------------

fn best_insertion_in_route(prob: &Problem, route: &Route, c_idx: usize) -> Option<(f64, usize)> {
    let c = &prob.customers[c_idx];
    if route.load + c.demand > prob.capacity + 1e-9 {
        return None;
    }
    let mut best: Option<(f64, usize)> = None;
    let depot = &prob.customers[0];

    for pos in 0..=route.customers.len() {
        let prev = if pos == 0 { depot } else { &prob.customers[route.customers[pos - 1]] };
        let next = if pos < route.customers.len() {
            &prob.customers[route.customers[pos]]
        } else {
            depot
        };

        // Quick distance delta (no TW check yet)
        let delta = dist(prev, c) + dist(c, next) - dist(prev, next);

        // Build candidate and check feasibility
        let mut candidate: Vec<usize> = route.customers.clone();
        candidate.insert(pos, c_idx);
        if route_feasible(prob, &candidate, 0.0) {
            if best.is_none() || delta < best.unwrap().0 {
                best = Some((delta, pos));
            }
        }
    }
    best
}

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
            // Collect feasible insertions across all existing routes
            let mut options: Vec<(f64, usize, usize)> = Vec::new(); // (cost, route_idx, pos)
            for (ri, route) in routes.iter().enumerate() {
                if let Some((cost, pos)) = best_insertion_in_route(prob, route, c_idx) {
                    options.push((cost, ri, pos));
                }
            }

            // Cost of opening a new route (always feasible for a single customer
            // as long as [ready, due] is within depot horizon -- assumed true for valid instances)
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
                            route.customers[i + 1..=j].reverse(); // undo
                        }
                    }
                }
            }
        }
    }
    any
}

// ---------------------------------------------------------------------------
// Or-opt: move a segment of 1, 2, or 3 customers to a better position
// (intra- and inter-route).
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
                            // Skip no-op for same route
                            if same
                                && ins_pos >= seg_start
                                && ins_pos <= seg_start + seg_len
                            {
                                continue;
                            }

                            // Build new route ri (segment removed)
                            let mut new_ri: Vec<usize> = routes[ri].customers.clone();
                            new_ri.drain(seg_start..seg_start + seg_len);

                            // Build new route rj (segment inserted)
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
    routes.sort_by_key(|r| r.customers.len());
    let mut reduced = false;
    let mut ri = 0;
    while ri < routes.len() {
        if routes[ri].customers.is_empty() {
            ri += 1;
            continue;
        }
        let candidates: Vec<usize> = routes[ri].customers.clone();
        let mut all_placed = true;
        let mut placements: Vec<(usize, usize)> = Vec::new(); // (route_idx, pos)

        for &c_idx in &candidates {
            let mut placed = false;
            for rj in 0..routes.len() {
                if rj == ri {
                    continue;
                }
                if let Some((_, pos)) = best_insertion_in_route(prob, &routes[rj], c_idx) {
                    placements.push((rj, pos));
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
            // Apply placements in reverse insertion order to preserve positions
            for (k, &c_idx) in candidates.iter().enumerate() {
                let (rj, base_pos) = placements[k];
                // Adjust pos for previous insertions in the same route
                let extra = placements[..k].iter().filter(|&&(r, _)| r == rj).count();
                let pos = (base_pos + extra).min(routes[rj].customers.len());
                routes[rj].customers.insert(pos, c_idx);
                routes[rj].load += prob.customers[c_idx].demand;
            }
            routes[ri].customers.clear();
            routes[ri].load = 0.0;
            reduced = true;
        }
        ri += 1;
    }
    routes.retain(|r| !r.customers.is_empty());
    reduced
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <instance_path>", args[0]);
        std::process::exit(1);
    }

    let start = Instant::now();
    let prob = parse_instance(&args[1]);

    // Construction
    let mut routes = regret2_construction(&prob);
    routes.retain(|r| !r.customers.is_empty());

    // Reduce vehicles
    loop {
        if !try_reduce_vehicles(&prob, &mut routes) {
            break;
        }
    }

    // Intra-route 2-opt
    apply_2opt_intra(&prob, &mut routes);

    // Or-opt + vehicle reduction loop
    loop {
        let imp = apply_or_opt(&prob, &mut routes);
        let red = try_reduce_vehicles(&prob, &mut routes);
        if !imp && !red {
            break;
        }
    }

    routes.retain(|r| !r.customers.is_empty());

    let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;
    let vehicles = routes.len();
    let distance: f64 = routes.iter().map(|r| route_distance(&prob, &r.customers)).sum();

    // Machine-parseable output for orchestrator
    println!("RESULT_VEHICLES: {}", vehicles);
    println!("RESULT_DISTANCE: {:.2}", distance);
    println!("RESULT_TIME_MS: {:.1}", elapsed_ms);

    // Human-readable detail
    eprintln!("\n--- Solution Detail ---");
    for (i, route) in routes.iter().enumerate() {
        let d = route_distance(&prob, &route.customers);
        let ids: Vec<String> = route.customers.iter().map(|c| c.to_string()).collect();
        eprintln!("Route {:3}: [{}]  dist={:.2}", i + 1, ids.join("->"), d);
    }
    eprintln!(
        "Vehicles: {}  Total distance: {:.2}  Time: {:.1}ms",
        vehicles, distance, elapsed_ms
    );
}
