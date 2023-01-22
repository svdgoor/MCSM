use regex::Regex;
use async_std::{fs, stream::StreamExt};

pub async fn find_files_regex(path: &str, regex: &str) -> Result<Vec<String>, String> {
    let mut files: Vec<String> = Vec::new();
    let re = Regex::new(regex).or(Err(format!("Failed to compile regex '{}'", regex)))?;
    match fs::read_dir(path).await {
        Ok(entries) => {
            let mut entries = entries;
            while let Some(res) = entries.next().await {
                match res {
                    Ok(entry) => {
                        let file = entry.file_name().into_string().or(Err(format!("Failed to convert file name to string")))?;
                        if re.is_match(&file) {
                            files.push(file);
                        }
                    }
                    Err(e) => {
                        if e.kind() != std::io::ErrorKind::NotFound {
                            return Err(format!("Failed to read directory entry: {}", e));
                        }
                    }
                }
            }
        }
        Err(e) => {
            if e.kind() != std::io::ErrorKind::NotFound {
                return Err(format!("Failed to read directory '{}': {}", path, e));
            }
        }
    }
    return Ok(files);
}

pub async fn delete_file(file: &str) -> Result<(), String> {
    match fs::remove_file(file).await {
        Ok(_) => {}
        Err(e) => {
            if e.kind() != std::io::ErrorKind::NotFound {
                return Err(format!("Failed to delete file '{}': {}", file, e));
            }
        }
    }
    return Ok(());
}

pub async fn delete_folder(folder: &str) -> Result<(), String> {
    match fs::remove_dir_all(folder).await {
        Ok(_) => {}
        Err(e) => {
            if e.kind() != std::io::ErrorKind::NotFound {
                return Err(format!("Failed to delete folder '{}': {}", folder, e));
            }
        }
    }
    return Ok(());
}

pub async fn delete_files(files: &Vec<String>) -> Result<(), String> {
    for file in files {
        delete_file(file).await?;
    }
    return Ok(());
}