use crate::util::files;

use super::settings::CleanSettings;

/// Cleaner is a utility for cleaning up temporary files.
/// It uses the CleanSettings from settings.rs to determine what to delete.

pub async fn clean(settings: &CleanSettings) -> Result<(), String> {
    for folder in &settings.folders {
        match files::delete_folder(&folder).await {
            Ok(_) => {}
            Err(e) => {
                println!("Failed to delete folder '{}': {}", folder, e);
            }
        }
    }
    for file in &settings.files {
        match files::delete_file(&file).await {
            Ok(_) => {}
            Err(e) => {
                println!("Failed to delete file '{}': {}", file, e);
            }
        }
    }
    return Ok(());
}