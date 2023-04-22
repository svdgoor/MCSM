/// Git utility functions.

use std::process::Command;

// Clone a git repository
pub async fn clone(url: &str, path: &str) -> Result<(), String> {
    match Command::new("git")
        .arg("clone")
        .arg(url)
        .arg(path)
        .output() {
        Ok(output) => {
            match output.status.success() {
                true => Ok(()),
                false => Err(format!("Failed to clone repository: {}", String::from_utf8_lossy(&output.stderr))),
            }
        },
        Err(e) => Err(format!("Failed to execute git clone command: {}", e)),
    }
}

// Switch to a git branch
pub fn checkout(path: &str, branch: &str) -> Result<(), String> {
    match Command::new("git")
        .arg("checkout")
        .arg(branch)
        .current_dir(path)
        .output() {
        Ok(output) => {
            match output.status.success() {
                true => Ok(()),
                false => Err(format!("Failed to checkout branch: {}", String::from_utf8_lossy(&output.stderr))),
            }
        },
        Err(e) => Err(format!("Failed to execute git checkout command: {}", e)),
    }
}

// Pull the latest changes from a git repository
pub fn pull(path: &str) -> Result<(), String> {
    match Command::new("git")
        .arg("pull")
        .arg("master")
        .current_dir(path)
        .output() {
        Ok(output) => {
            match output.status.success() {
                true => Ok(()),
                false => Err(format!("Failed to pull changes: {}", String::from_utf8_lossy(&output.stderr))),
            }
        },
        Err(e) => Err(format!("Failed to execute git pull command: {}", e)),
    }
}