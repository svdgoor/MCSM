use std::process::Command;

use async_std::path::Path;

use crate::util::files;

use super::settings::CleanSettings;

/// Cleaner is a utility for cleaning up temporary files.
/// It uses the CleanSettings from settings.rs to determine what to delete.

pub async fn clean(settings: &CleanSettings) -> Result<(), String> {
    for folder in &settings.folders {
        match files::delete_folder(folder).await {
            Ok(_) => {}
            Err(e) => {
                println!("Failed to delete folder '{}': {}", folder, e);
            }
        }
    }
    for file in &settings.files {
        match files::delete_file(Path::new(file)).await {
            Ok(_) => {}
            Err(e) => {
                println!("Failed to delete file '{}': {}", file, e);
            }
        }
    }
    Ok(())
}

// Use git commands to clean up the repository
const EXE_PATH: &str = "/target/release/mcsm.exe";
pub fn clean_deep() -> Result<(), String> {
    // Negate current executable to .gitignore.
    Command::new("git")
        .arg("add")
        .arg("-f")
        .arg(EXE_PATH)
        .output()
        .map_err(|e| format!("Failed to run git add: {}", e))?;
    Command::new("git")
        .arg("clean")
        .arg("-fdX")
        .output()
        .map_err(|e| format!("Failed to run git clean: {}", e))?;
    // Remove the negation
    Command::new("git")
        .arg("restore")
        .arg("--staged")
        .arg(EXE_PATH)
        .output()
        .map_err(|e| format!("Failed to run git reset: {}", e))?;
    Ok(())
}