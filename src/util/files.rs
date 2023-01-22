use regex::Regex;
use walkdir::WalkDir;

pub async fn find_files_regex(path: &str, regex: &str) -> Result<Vec<String>, String> {
    let mut files: Vec<String> = Vec::new();
    let re = Regex::new(regex).or(Err(format!("Failed to compile regex '{}'", regex)))?;
    for entry in WalkDir::new(path) {
        let entry = entry.or(Err(format!("Failed to read directory '{}'", path)))?;
        let path = entry.path();
        if path.is_file() {
            let path = path.to_str().unwrap();
            if re.is_match(path) {
                files.push(path.to_string());
            }
        }
    }
    return Ok(files);
}