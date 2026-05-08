use serde::{Deserialize, Serialize};
use std::collections::{BTreeMap, BTreeSet};
use std::env;
use std::fs;

const MAX_REASONABLE_HOPS: usize = 8;
const MAX_REASONABLE_RESULTS: usize = 1000;
const MAX_ASSET_SYMBOL_LENGTH: usize = 32;
const MAX_VENUE_LENGTH: usize = 80;
const MAX_SOURCE_LENGTH: usize = 120;
const MAX_NETWORK_LENGTH: usize = 64;

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
struct Edge {
    source: String,
    target: String,
    rate: f64,
    #[serde(default = "default_venue")]
    venue: String,
    #[serde(default)]
    fee_bps: f64,
    #[serde(default)]
    liquidity: Option<f64>,
    #[serde(default = "default_metadata")]
    metadata: serde_json::Value,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
struct Snapshot {
    #[serde(default)]
    source: Option<String>,
    #[serde(default = "default_network")]
    network: String,
    #[serde(default)]
    timestamp: Option<String>,
    edges: Vec<Edge>,
}

#[derive(Debug, Serialize)]
struct Opportunity {
    network: String,
    path: Vec<String>,
    venues: Vec<String>,
    gross_return: f64,
    profit_bps: f64,
    limiting_liquidity: Option<f64>,
    estimated_capacity: f64,
}

#[derive(Debug, Clone)]
struct Policy {
    min_profit_bps: f64,
    max_hops: usize,
    min_liquidity: f64,
    max_notional: f64,
    max_results: usize,
}

fn default_venue() -> String {
    "unknown".to_string()
}

fn default_metadata() -> serde_json::Value {
    serde_json::json!({})
}

fn default_network() -> String {
    "polygon".to_string()
}

fn main() {
    if let Err(err) = run() {
        eprintln!("defi-arbitrage-core-rs: {err}");
        std::process::exit(2);
    }
}

fn run() -> Result<(), String> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 || args.iter().any(|arg| arg == "--help" || arg == "-h") {
        print_usage();
        return Ok(());
    }
    let snapshot_path = &args[1];
    let policy = parse_policy(&args[2..])?;
    validate_policy(&policy)?;
    let raw = fs::read_to_string(snapshot_path)
        .map_err(|_| format!("snapshot file does not exist or cannot be read: {snapshot_path}"))?;
    let snapshot: Snapshot = serde_json::from_str(&raw)
        .map_err(|_| format!("snapshot file is not valid JSON: {snapshot_path}"))?;
    let snapshot = normalize_snapshot(snapshot)?;
    validate_snapshot_metadata(&snapshot)?;
    let mut edges = Vec::new();
    for edge in snapshot.edges {
        edges.push(normalize_edge(edge)?);
    }
    if edges.is_empty() {
        return Err("market snapshot must contain at least one edge".to_string());
    }
    let opportunities = analyze(&snapshot.network, &edges, &policy);
    let output = serde_json::to_string_pretty(&opportunities)
        .map_err(|_| "failed to serialize opportunities".to_string())?;
    println!("{output}");
    Ok(())
}

fn print_usage() {
    println!("Usage: defi-arbitrage-core-rs <snapshot.json> [--min-profit-bps N] [--max-hops N] [--min-liquidity N] [--max-notional N] [--max-results N]");
}

fn parse_policy(args: &[String]) -> Result<Policy, String> {
    let mut policy = Policy {
        min_profit_bps: 5.0,
        max_hops: 4,
        min_liquidity: 0.0,
        max_notional: 10_000.0,
        max_results: 25,
    };
    let mut index = 0;
    while index < args.len() {
        let key = &args[index];
        let value = args
            .get(index + 1)
            .ok_or_else(|| format!("missing value for {key}"))?;
        match key.as_str() {
            "--min-profit-bps" => policy.min_profit_bps = parse_f64(key, value)?,
            "--max-hops" => policy.max_hops = parse_usize(key, value)?,
            "--min-liquidity" => policy.min_liquidity = parse_f64(key, value)?,
            "--max-notional" => policy.max_notional = parse_f64(key, value)?,
            "--max-results" => policy.max_results = parse_usize(key, value)?,
            _ => return Err(format!("unknown argument: {key}")),
        }
        index += 2;
    }
    Ok(policy)
}

fn parse_f64(name: &str, value: &str) -> Result<f64, String> {
    value
        .parse::<f64>()
        .map_err(|_| format!("{name} must be a number"))
}

fn parse_usize(name: &str, value: &str) -> Result<usize, String> {
    value
        .parse::<usize>()
        .map_err(|_| format!("{name} must be an integer"))
}

fn validate_policy(policy: &Policy) -> Result<(), String> {
    if !policy.min_profit_bps.is_finite() || policy.min_profit_bps < 0.0 {
        return Err("min_profit_bps must be a finite non-negative number".to_string());
    }
    if policy.max_hops < 2 {
        return Err("max_hops must be at least 2".to_string());
    }
    if policy.max_hops > MAX_REASONABLE_HOPS {
        return Err(format!("max_hops must be at most {MAX_REASONABLE_HOPS}"));
    }
    if !policy.min_liquidity.is_finite() || policy.min_liquidity < 0.0 {
        return Err("min_liquidity must be a finite non-negative number".to_string());
    }
    if !policy.max_notional.is_finite() || policy.max_notional <= 0.0 {
        return Err("max_notional must be a finite positive number".to_string());
    }
    if policy.max_results < 1 {
        return Err("max_results must be at least 1".to_string());
    }
    if policy.max_results > MAX_REASONABLE_RESULTS {
        return Err(format!("max_results must be at most {MAX_REASONABLE_RESULTS}"));
    }
    Ok(())
}

fn validate_snapshot_metadata(snapshot: &Snapshot) -> Result<(), String> {
    if let Some(source) = &snapshot.source {
        if source.trim().is_empty() {
            return Err("market snapshot source must be a non-empty string".to_string());
        }
        if source.trim().len() > MAX_SOURCE_LENGTH {
            return Err(format!("market snapshot source must be {MAX_SOURCE_LENGTH} characters or fewer"));
        }
    }
    if snapshot.network.trim().is_empty() {
        return Err("market snapshot network must be a non-empty string".to_string());
    }
    if snapshot.network.trim().len() > MAX_NETWORK_LENGTH {
        return Err(format!(
            "market snapshot network must be {MAX_NETWORK_LENGTH} characters or fewer"
        ));
    }
    if let Some(timestamp) = &snapshot.timestamp {
        if !is_utc_rfc3339_seconds(timestamp) {
            return Err("market snapshot timestamp must use UTC RFC3339 form YYYY-MM-DDTHH:MM:SSZ".to_string());
        }
    }
    Ok(())
}

fn normalize_snapshot(snapshot: Snapshot) -> Result<Snapshot, String> {
    let network = snapshot.network.trim().to_lowercase();
    if network.is_empty() {
        return Err("market snapshot network must be a non-empty string".to_string());
    }
    Ok(Snapshot {
        source: snapshot.source.map(|value| value.trim().to_string()),
        network,
        timestamp: snapshot.timestamp,
        edges: snapshot.edges,
    })
}

fn is_utc_rfc3339_seconds(value: &str) -> bool {
    let bytes = value.as_bytes();
    if bytes.len() != 20 {
        return false;
    }
    for (index, expected) in [(4, b'-'), (7, b'-'), (10, b'T'), (13, b':'), (16, b':'), (19, b'Z')] {
        if bytes[index] != expected {
            return false;
        }
    }
    bytes.iter().enumerate().all(|(index, byte)| {
        matches!(index, 4 | 7 | 10 | 13 | 16 | 19) || byte.is_ascii_digit()
    })
}

fn normalize_edge(edge: Edge) -> Result<Edge, String> {
    let normalized = Edge {
        source: edge.source.trim().to_uppercase(),
        target: edge.target.trim().to_uppercase(),
        rate: edge.rate,
        venue: if edge.venue.trim().is_empty() {
            default_venue()
        } else {
            edge.venue.trim().to_string()
        },
        fee_bps: edge.fee_bps,
        liquidity: edge.liquidity,
        metadata: edge.metadata,
    };
    if normalized.source.is_empty() || normalized.target.is_empty() {
        return Err("edge source and target are required".to_string());
    }
    if normalized.source.len() > MAX_ASSET_SYMBOL_LENGTH || normalized.target.len() > MAX_ASSET_SYMBOL_LENGTH {
        return Err(format!("edge source and target must be {MAX_ASSET_SYMBOL_LENGTH} characters or fewer"));
    }
    if normalized.source == normalized.target {
        return Err("edge source and target must differ".to_string());
    }
    if normalized.venue.len() > MAX_VENUE_LENGTH {
        return Err(format!("edge venue must be {MAX_VENUE_LENGTH} characters or fewer"));
    }
    if !normalized.metadata.is_object() {
        return Err("edge metadata must be an object".to_string());
    }
    if !normalized.rate.is_finite() || normalized.rate <= 0.0 {
        return Err("edge rate must be a finite positive number".to_string());
    }
    if !normalized.fee_bps.is_finite() || normalized.fee_bps < 0.0 || normalized.fee_bps >= 10_000.0
    {
        return Err("edge fee_bps must be a finite number in [0, 10000)".to_string());
    }
    if let Some(liquidity) = normalized.liquidity {
        if !liquidity.is_finite() || liquidity < 0.0 {
            return Err("edge liquidity must be a finite non-negative number".to_string());
        }
    }
    Ok(normalized)
}

fn analyze(network: &str, edges: &[Edge], policy: &Policy) -> Vec<Opportunity> {
    let mut graph: BTreeMap<String, Vec<Edge>> = BTreeMap::new();
    for edge in edges {
        if edge
            .liquidity
            .is_some_and(|value| value < policy.min_liquidity)
        {
            continue;
        }
        graph
            .entry(edge.source.clone())
            .or_default()
            .push(edge.clone());
    }
    let mut opportunities: BTreeMap<Vec<String>, Opportunity> = BTreeMap::new();
    for start in graph.keys() {
        walk(
            network,
            start,
            start,
            &graph,
            Vec::new(),
            1.0,
            policy,
            &mut opportunities,
        );
    }
    let mut ranked: Vec<Opportunity> = opportunities.into_values().collect();
    ranked.sort_by(|a, b| {
        b.profit_bps
            .partial_cmp(&a.profit_bps)
            .unwrap_or(std::cmp::Ordering::Equal)
    });
    ranked.truncate(policy.max_results);
    ranked
}

fn walk(
    network: &str,
    start: &str,
    current: &str,
    graph: &BTreeMap<String, Vec<Edge>>,
    route: Vec<Edge>,
    gross_return: f64,
    policy: &Policy,
    opportunities: &mut BTreeMap<Vec<String>, Opportunity>,
) {
    if route.len() >= policy.max_hops {
        return;
    }
    let Some(edges) = graph.get(current) else {
        return;
    };
    for edge in edges {
        let mut next_route = route.clone();
        next_route.push(edge.clone());
        let next_return = gross_return * effective_rate(edge);
        if edge.target == start && next_route.len() >= 2 {
            let opportunity = to_opportunity(network, start, &next_route, next_return, policy);
            if opportunity.profit_bps >= policy.min_profit_bps
                && opportunity.estimated_capacity >= policy.min_liquidity
            {
                let key = canonical_key(&opportunity.path);
                let replace = opportunities
                    .get(&key)
                    .is_none_or(|existing| opportunity.profit_bps > existing.profit_bps);
                if replace {
                    opportunities.insert(key, opportunity);
                }
            }
            continue;
        }
        let visited: BTreeSet<String> = next_route.iter().map(|hop| hop.source.clone()).collect();
        if !visited.contains(&edge.target) {
            walk(
                network,
                start,
                &edge.target,
                graph,
                next_route,
                next_return,
                policy,
                opportunities,
            );
        }
    }
}

fn effective_rate(edge: &Edge) -> f64 {
    edge.rate * (1.0 - edge.fee_bps / 10_000.0)
}

fn to_opportunity(network: &str, start: &str, route: &[Edge], gross_return: f64, policy: &Policy) -> Opportunity {
    let mut path = vec![start.to_string()];
    let mut venues = Vec::new();
    let mut limiting_liquidity: Option<f64> = None;
    for edge in route {
        path.push(edge.target.clone());
        venues.push(edge.venue.clone());
        if let Some(liquidity) = edge.liquidity {
            limiting_liquidity =
                Some(limiting_liquidity.map_or(liquidity, |current| current.min(liquidity)));
        }
    }
    let estimated_capacity = policy
        .max_notional
        .min(limiting_liquidity.unwrap_or(policy.max_notional));
    Opportunity {
        network: network.to_string(),
        path,
        venues,
        gross_return,
        profit_bps: (gross_return - 1.0) * 10_000.0,
        limiting_liquidity,
        estimated_capacity,
    }
}

fn canonical_key(path: &[String]) -> Vec<String> {
    let cycle = &path[..path.len() - 1];
    let mut best: Option<Vec<String>> = None;
    for index in 0..cycle.len() {
        let mut rotated = Vec::with_capacity(cycle.len() + 1);
        rotated.extend_from_slice(&cycle[index..]);
        rotated.extend_from_slice(&cycle[..index]);
        rotated.push(rotated[0].clone());
        if best.as_ref().is_none_or(|current| rotated < *current) {
            best = Some(rotated);
        }
    }
    best.unwrap_or_else(|| path.to_vec())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn policy() -> Policy {
        Policy {
            min_profit_bps: 1.0,
            max_hops: 3,
            min_liquidity: 0.0,
            max_notional: 10_000.0,
            max_results: 25,
        }
    }

    #[test]
    fn effective_rate_subtracts_fees() {
        let edge = Edge {
            source: "A".to_string(),
            target: "B".to_string(),
            rate: 2.0,
            venue: "x".to_string(),
            fee_bps: 100.0,
            liquidity: None,
            metadata: serde_json::json!({}),
        };
        assert_eq!(effective_rate(&edge), 1.98);
    }

    #[test]
    fn policy_rejects_too_few_hops() {
        let invalid = Policy { max_hops: 1, ..policy() };
        assert!(validate_policy(&invalid).is_err());
    }

    #[test]
    fn policy_rejects_unbounded_hops_and_results() {
        assert!(validate_policy(&Policy { max_hops: 99, ..policy() }).is_err());
        assert!(validate_policy(&Policy { max_results: 10_001, ..policy() }).is_err());
    }

    #[test]
    fn normalize_edge_uppercases_symbols_and_rejects_bad_rate() {
        let normalized = normalize_edge(Edge {
            source: " usdc ".to_string(),
            target: " weth ".to_string(),
            rate: 1.0,
            venue: "".to_string(),
            fee_bps: 0.0,
            liquidity: None,
            metadata: serde_json::json!({}),
        })
        .unwrap();
        assert_eq!(normalized.source, "USDC");
        assert_eq!(normalized.target, "WETH");
        assert_eq!(normalized.venue, "unknown");
        assert!(normalize_edge(Edge { rate: -1.0, ..normalized }).is_err());
    }

    #[test]
    fn canonical_key_is_rotation_stable() {
        let a = vec!["A".to_string(), "B".to_string(), "C".to_string(), "A".to_string()];
        let b = vec!["B".to_string(), "C".to_string(), "A".to_string(), "B".to_string()];
        assert_eq!(canonical_key(&a), canonical_key(&b));
    }

    #[test]
    fn analyze_finds_expected_cycle() {
        let edges = vec![
            Edge { source: "A".to_string(), target: "B".to_string(), rate: 2.0, venue: "one".to_string(), fee_bps: 0.0, liquidity: Some(100.0), metadata: serde_json::json!({}) },
            Edge { source: "B".to_string(), target: "C".to_string(), rate: 2.0, venue: "two".to_string(), fee_bps: 0.0, liquidity: Some(80.0), metadata: serde_json::json!({}) },
            Edge { source: "C".to_string(), target: "A".to_string(), rate: 0.26, venue: "three".to_string(), fee_bps: 0.0, liquidity: Some(60.0), metadata: serde_json::json!({}) },
        ];
        let opportunities = analyze("polygon", &edges, &policy());
        assert_eq!(opportunities.len(), 1);
        assert_eq!(opportunities[0].network, "polygon");
        assert_eq!(opportunities[0].path, vec!["A", "B", "C", "A"]);
        assert!(opportunities[0].profit_bps > 399.0);
    }
}
