use std::env;
use std::fs;
use std::io::Write as IoWrite;
use std::time::Instant;

mod solver;

// ---------------------------------------------------------------------------
// Data structures — pub so solver.rs can use them via `use super::*`
// ---------------------------------------------------------------------------

#[derive(Debug, Clone)]
pub struct Customer {
    pub id: usize,
    pub x: f64,
    pub y: f64,
    pub demand: f64,
    pub ready: f64,
    pub due: f64,
    pub service: f64,
}

#[derive(Debug, Clone)]
pub struct Route {
    pub customers: Vec<usize>, // customer indices; depot (0) is implicit start/end
    pub load: f64,
}

pub struct Problem {
    pub customers: Vec<Customer>, // index 0 = depot
    pub capacity: f64,
    pub n: usize, // number of customers excluding depot
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
            continue;
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
// Utilities — pub so solver.rs can use them
// ---------------------------------------------------------------------------

#[inline]
pub fn dist(a: &Customer, b: &Customer) -> f64 {
    let dx = a.x - b.x;
    let dy = a.y - b.y;
    (dx * dx + dy * dy).sqrt()
}

pub fn route_distance(prob: &Problem, customers: &[usize]) -> f64 {
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

pub fn route_feasible(prob: &Problem, customers: &[usize], extra_load: f64) -> bool {
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

pub fn best_insertion_in_route(prob: &Problem, route: &Route, c_idx: usize) -> Option<(f64, usize)> {
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
        let delta = dist(prev, c) + dist(c, next) - dist(prev, next);
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
// Main — parse, solve, report, write solution file
// ---------------------------------------------------------------------------

fn main() {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        eprintln!("Usage: {} <instance_path> [solution_output_path]", args[0]);
        std::process::exit(1);
    }
    let solution_path = if args.len() >= 3 { args[2].as_str() } else { "solution.txt" };

    let start = Instant::now();
    let prob = parse_instance(&args[1]);
    let routes = solver::solve(&prob);
    let elapsed_ms = start.elapsed().as_secs_f64() * 1000.0;

    let vehicles = routes.len();
    let distance: f64 = routes.iter().map(|r| route_distance(&prob, &r.customers)).sum();

    // Machine-parseable output for the orchestrator
    println!("RESULT_VEHICLES: {}", vehicles);
    println!("RESULT_DISTANCE: {:.2}", distance);
    println!("RESULT_TIME_MS: {:.1}", elapsed_ms);

    // Solution file for the Python validator and auditing
    let mut sol = fs::File::create(solution_path).expect("Cannot create solution file");
    writeln!(sol, "VEHICLES: {}", vehicles).unwrap();
    writeln!(sol, "DISTANCE: {:.2}", distance).unwrap();
    writeln!(sol, "TIME_MS: {:.1}", elapsed_ms).unwrap();
    for (i, route) in routes.iter().enumerate() {
        let ids: Vec<String> = route.customers.iter().map(|c| c.to_string()).collect();
        writeln!(sol, "Route {}: {}", i + 1, ids.join(" ")).unwrap();
    }

    // Human-readable detail to stderr
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
