use regex::Regex;
use async_std::{fs, stream::StreamExt, path::Path};

pub async fn find_files_regex(path: &str, regex: &str) -> Result<Vec<String>, String> {
    let mut files: Vec<String> = Vec::new();
    let re = match Regex::new(regex) {
        Ok(re) => re,
        Err(e) => return Err(e.to_string()),
    };
    match fs::read_dir(path).await {
        Ok(entries) => {
            let mut entries = entries;
            while let Some(res) = entries.next().await {
                match res {
                    Ok(entry) => {
                        let file = match entry.file_name().into_string() {
                            Ok(res) => res,
                            Err(_) => continue,
                        };
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
    Ok(files)
}

pub async fn delete_file(file: &Path) -> Result<(), String> {
    match fs::remove_file(file).await {
        Ok(_) => {}
        Err(e) => {
            if e.kind() != std::io::ErrorKind::NotFound {
                return Err(format!("Failed to delete file '{}': {}", file.to_string_lossy(), e));
            }
        }
    }
    Ok(())
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
    Ok(())
}

pub async fn delete_files(files: &Vec<String>) -> Result<(), String> {
    for file in files {
        delete_file(Path::new(file)).await?;
    }
    Ok(())
}

pub async fn move_file(from: &Path, to: &Path) -> Result<(), String> {
    match fs::rename(from, to).await {
        Ok(_) => {}
        Err(e) => {
            if e.kind() != std::io::ErrorKind::NotFound {
                return Err(format!("Failed to move file '{}' to '{}': {}", from.to_string_lossy(), to.to_string_lossy(), e));
            }
        }
    }
    Ok(())
}