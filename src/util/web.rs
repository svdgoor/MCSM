use std::cmp::min;
use std::fs::File;
use std::io::Write;

use reqwest::Client;
use indicatif::{ProgressBar, ProgressStyle};

pub async fn download_file_progress_bar(client: &Client, url: &str, path: &str, show_result: bool) -> Result<(), String> {
    // Start time
    let start = std::time::Instant::now();

    // Reqwest setup
    let mut res = client
        .get(url)
        .send()
        .await
        .or(Err(format!("Failed to GET from '{}'", &url)))?;
    let total_size = res
        .content_length().or(Some(u64::MAX)).unwrap();
    let name = res.url().path_segments()
        .and_then(|segments| segments.last())
        .and_then(|s| if s.is_empty() { None } else { Some(s) })
        .unwrap_or("");
    
    // Indicatif setup
    let pb = ProgressBar::new(total_size);
    pb.set_style(ProgressStyle::default_bar()
        .template("{msg}\n{spinner:.green} [{elapsed_precise}] [{wide_bar:.cyan/blue}] {bytes}/{total_bytes} ({bytes_per_sec}, {eta})").unwrap()
        .progress_chars("#>-"));

    // download chunks
    let target = path.to_owned() + "/" + url.split('/').last().unwrap();
    let mut file = File::create(&target).or(Err(format!("Failed to create file '{}'", &target)))?;
    let mut downloaded: u64 = 0;

    while let Some(item) = res.chunk().await.unwrap() {
        file.write_all(&item)
            .or(Err(format!("Error while writing to file")))?;
        let new = min(downloaded + (item.len() as u64), total_size);
        downloaded = new;
        pb.set_position(new);
    }

    pb.finish_with_message("Download complete");

    if show_result {
        println!("Downloaded to '{}' ({} bytes) in {} seconds", path, total_size, start.elapsed().as_secs());
    }

    return Ok(());
}