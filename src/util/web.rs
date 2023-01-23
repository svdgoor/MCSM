use std::cmp::min;
use std::fs::File;
use std::io::Write;

use async_std::{path::Path, fs};
use reqwest::Client;
use indicatif::{ProgressBar, ProgressStyle};

pub async fn download_file_progress_bar(client: &Client, url: &str, path: &Path) -> Result<(), String> {
    // Start time
    let start = std::time::Instant::now();

    // Make folder
    if let Some(parent) = path.parent() {
        match fs::create_dir_all(parent).await {
            Ok(_) => {}
            Err(e) => {
                return Err(format!("Failed to create folder '{}': {}", parent.to_string_lossy(), e));
            }
        }
    }

    // Reqwest setup
    let mut res = match client
            .get(url)
            .send()
            .await {
        Ok(res) => res,
        Err(e) => return Err(format!("Failed to download file '{}': {}", url, e)),
    };
    let total_size = res
        .content_length().unwrap_or(u64::MAX);
    
    // Indicatif setup
    let pb = ProgressBar::new(total_size);
    pb.set_style(ProgressStyle::default_bar()
        .template("{msg}\n{spinner:.green} [{elapsed_precise}] [{wide_bar:.cyan/blue}] {bytes}/{total_bytes} ({bytes_per_sec}, {eta})").unwrap()
        .progress_chars("#>-"));

    // File setup
    let mut file = match File::create(&path) {
        Ok(file) => file,
        Err(e) => {
            if e.kind() != std::io::ErrorKind::NotFound {
                return Err(format!("Failed to create file '{}': {}", &path.to_string_lossy(), e));
            }
            return Ok(());
        }
    };
    let mut downloaded: u64 = 0;

    while let Some(item) = res.chunk().await.unwrap() {
        match file.write_all(&item) {
            Ok(_) => {}
            Err(e) => return Err(format!("Failed to write to file '{}': {}", &path.to_string_lossy(), e)),
        }
        let new = min(downloaded + (item.len() as u64), total_size);
        downloaded = new;
        pb.set_position(new);
    }

    pb.finish_with_message(format!("Downloaded to '{}' ({} bytes) in {} seconds", path.to_string_lossy(), total_size, start.elapsed().as_secs()));

    Ok(())
}