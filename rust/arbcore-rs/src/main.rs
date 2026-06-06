fn calculate_metadata_depth(value: &serde_json::Value) -> usize {
    match value {
        serde_json::Value::Object(map) => {
            if map.is_empty() {
                return 1;
            }
            let max_child_depth = map.values()
                .map(calculate_metadata_depth)
                .max()
                .unwrap_or(0);
            1 + max_child_depth
        }
        serde_json::Value::Array(arr) => {
            if arr.is_empty() {
                return 1;
            }
            let max_child_depth = arr.iter()
                .map(calculate_metadata_depth)
                .max()
                .unwrap_or(0);
            1 + max_child_depth
        }
        _ => 0,
    }
}