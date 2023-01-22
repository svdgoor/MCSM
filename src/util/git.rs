/// Git utility functions.

use std::process::Command;

// Clone a git repository
pub fn clone(url: &str, path: &str) -> Result<(), String> {
    let output = Command::new("git")
        .arg("clone")
        .arg(url)
        .arg(path)
        .output()
        .or(Err(format!("Failed to execute git clone command")))?;
    if !output.status.success() {
        return Err(format!("Failed to clone repository: {}", String::from_utf8_lossy(&output.stderr)));
    }
    return Ok(());
}

// Switch to a git branch
pub fn checkout(path: &str, branch: &str) -> Result<(), String> {
    let output = Command::new("git")
        .arg("checkout")
        .arg(branch)
        .current_dir(path)
        .output()
        .or(Err(format!("Failed to execute git checkout command")))?;
    if !output.status.success() {
        return Err(format!("Failed to checkout branch: {}", String::from_utf8_lossy(&output.stderr)));
    }
    return Ok(());
}

// Pull the latest changes from a git repository
pub fn pull(path: &str) -> Result<(), String> {
    let output = Command::new("git")
        .arg("pull")
        .current_dir(path)
        .output()
        .or(Err(format!("Failed to execute git pull command")))?;
    if !output.status.success() {
        return Err(format!("Failed to pull repository: {}", String::from_utf8_lossy(&output.stderr)));
    }
    return Ok(());
}