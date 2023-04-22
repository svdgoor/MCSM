pub mod util;

use std::process::{Command, Stdio};

use async_std::fs::File;
use async_std::io::WriteExt;
use async_std::path::Path;
use async_std::task::{self, JoinHandle};
use clap::Parser;
use reqwest::Client;
use util::settings::{default_settings, PluginSettings, CleanSettings, ServerSoftwareSettings, IrisSettings};
use util::{cleaner, files};
use walkdir::WalkDir;

use crate::util::git;
use crate::util::settings::Settings;
use crate::util::web::download_file_progress_bar;

#[derive(Parser)]
struct Cli {
    /// Full update
    #[arg(short, long, default_value_t = false)]
    update: bool,
    /// Clean up temporary files
    #[arg(short, long, default_value_t = false)]
    clean: bool,
    /// Clean exclusively, without updating
    #[arg(short, long, default_value_t = false)]
    excl_clean: bool,
    /// Clean exclusively deep, removing all gitignored files
    #[arg(short, long, default_value_t = false)]
    deep_excl_clean: bool,
    /// Re-build Iris distr
    #[arg(long, default_value_t = false)]
    update_iris: bool,
    /// Update to latest server version
    #[arg(long, default_value_t = false)]
    update_server: bool,
    /// Update plugins
    #[arg(long, default_value_t = false)]
    update_plugins: bool,
    /// Settings file location
    #[arg(short, long, default_value_t = default_settings())]
    settings: String,
}

struct ServerTask {
    task: JoinHandle<()>,
    name: String,
}

#[tokio::main]
async fn main() {
    // Load command line arguments
    let args = Cli::parse();

    // Load settings
    let settings = Settings::load(&args.settings);

    if args.deep_excl_clean {
        println!("Deep cleaning files... ");
        cleaner::clean_deep().unwrap();
        return;
    } else if args.excl_clean {
        println!("Cleaning up temporary files... ");
        cleaner::clean(&settings.clean).await.unwrap();
        return;
    }

    // Tasks
    let mut tasks: Vec<ServerTask> = Vec::new();

    // Server task
    tasks.push(task_server(settings.server.clone(), args.update || args.update_server));

    // EULA task
    tasks.push(task_eula());

    // Plugins task
    tasks.append(&mut task_plugins(settings.plugins, args.update || args.update_plugins));

    // Iris task
    tasks.push(task_iris(settings.iris, args.update || args.update_iris));

    // Clean task
    tasks.push(task_clean(settings.clean.clone(), args.clean));

    // Print task details
    println!(
        "Scheduled {} tasks: {}",
        tasks.len(),
        tasks
            .iter()
            .map(|t| t.name.as_str())
            .collect::<Vec<&str>>()
            .join(", ")
    );

    // Wait for tasks to finish
    while let Some(task) = tasks.pop() {
        task.task.await;
    }

    // Start server
    // Run a command prompt with `java -jar <server_jar> flags nogui`
    loop {
        println!("Starting server");
        let mut command = Command::new("java");
        command.args(&settings.server.flags);
        command.arg("-jar");
        command.arg(&settings.server.name);
        command.arg("nogui");
        println!("Running command: {:?}", command);
        command.spawn().unwrap().wait().unwrap();
        println!("Server stopped. Rebooting in {} seconds", settings.server.reboot_delay);
        // Sleep
        task::sleep(std::time::Duration::from_secs(settings.server.reboot_delay.into())).await;
        // Clean if needed
        if settings.clean.also_on_reboot && settings.clean.enabled {
            cleaner::clean(&settings.clean).await.unwrap();
        }
    }
}

fn task_server(settings: ServerSoftwareSettings, always_update: bool) -> ServerTask {
    ServerTask {
        task: task::spawn(async move {
            let path = Path::new(settings.name.as_str());
            if always_update || !path.exists().await {
                println!("Updating server");
                if !path.exists().await {
                    files::delete_file(path).await.unwrap();
                }
                download_file_progress_bar(
                    &Client::new(),
                    &settings.download_url,
                    path
                )
                .await
                .unwrap();
            }
        }),
        name: "Server".to_string(),
    }
}

fn task_eula() -> ServerTask {
    ServerTask {
        task: task::spawn(async move {
            let path = Path::new("eula.txt");
            if !path.exists().await {
                let mut file = File::create(path).await.unwrap();
                file.write_all(b"eula=true").await.unwrap();
            }
        }),
        name: "EULA".to_string(),
    }
}

fn task_plugins(settings: Vec<PluginSettings>, always_update: bool) -> Vec<ServerTask>{
    let mut tasks = Vec::new();
    for plugin in settings {
        let plugin_settings = plugin.clone();
        if !plugin_settings.enabled {
            continue;
        }
        tasks.push(ServerTask {
            task: task::spawn(async move {
                let ps = "./plugins/".to_string() + &plugin_settings.name + ".jar";
                let path = Path::new(&ps);
                if always_update || !path.exists().await {
                    println!("Updating plugin {}", &plugin_settings.name);
                    if !path.exists().await {
                        files::delete_file(path).await.unwrap();
                    }
                    download_file_progress_bar(
                        &Client::new(),
                        &plugin_settings.download_url,
                        path
                    )
                    .await
                    .unwrap();
                }
            }),
            name: plugin.name.clone(),
        });
    }
    tasks
}

fn task_iris(settings: IrisSettings, always_update: bool) -> ServerTask {
    match settings.enabled || always_update {
        true => ServerTask {
            task: task::spawn(async move {

                // Check repo directory
                let path = Path::new(&settings.repo_path);
                if !path.exists().await {
                    println!("Cloning Iris into {}", &settings.repo_path);
                    match git::clone(&settings.repo_url, &settings.repo_path).await {
                        Ok(_) => {}
                        Err(e) => {
                            println!("Error cloning Iris: {}", e);
                            return;
                        }
                    }
                }
                if !path.exists().await {
                    println!("Error cloning Iris");
                    return;
                }

                // Pull latest changes
                println!("Pulling latest changes");
                match git::pull(&settings.repo_path) {
                    Ok(_) => {}
                    Err(e) => {
                        println!("Error pulling latest changes: {}", e);
                        return;
                    }
                }

                // Check dependencies
                let ps = path.to_str().unwrap().to_owned() + "/build/buildtools/CraftBukkit";
                let path_dep = Path::new(&ps);
                if !path_dep.exists().await {
                    println!("Setting up Iris repo dependencies");
                    let output = Command::new("cmd")
                        .arg("/C")
                        .arg("cd")
                        .arg(&settings.repo_path)
                        .arg("&&")
                        .arg("gradlew")
                        .arg("setup")
                        .stdout(Stdio::piped())
                        .output().unwrap();
                    println!("Output: {}", String::from_utf8_lossy(&output.stdout));
                }
                if !path_dep.exists().await {
                    println!("Error setting up Iris repo dependencies");
                    return;
                }

                // Build Iris
                println!("Building Iris");
                Command::new("cmd")
                    .arg("/C")
                    .arg("cd")
                    .arg(&settings.repo_path)
                    .arg("&&")
                    .arg("gradlew")
                    .arg("Iris")
                    .stdout(Stdio::piped())
                    .output().unwrap();

                // Find Iris jar
                let mut iris_jar = String::new();
                for entry in WalkDir::new(&settings.repo_path) {
                    let entry = entry.unwrap();
                    let path = entry.path();
                    if path.is_file() {
                        let file_name = path.file_name().unwrap().to_str().unwrap();
                        if file_name.starts_with("Iris") && file_name.ends_with(".jar") {
                            iris_jar = path.to_str().unwrap().to_owned();
                            break;
                        }
                    }
                }
                
                // Move Iris jar
                let path = Path::new(&iris_jar);
                let ps = "./plugins/".to_string() + &settings.name + ".jar";
                let path_dest = Path::new(&ps);
                if path.exists().await {
                    println!("Deleting existing Iris jar");
                    files::delete_file(path_dest).await.expect("Error deleting existing Iris jar");
                }
                files::move_file(path, path_dest).await.expect("Error moving Iris jar");
            }),
            name: "Iris".to_string(),
        },
        false => ServerTask {
            task: task::spawn(async move {
                println!("Iris disabled");
            }),
            name: "Iris".to_string(),
        }
    }
}

fn task_clean(settings: CleanSettings, always_clean: bool) -> ServerTask {
    match always_clean || settings.enabled {
        true => ServerTask {
            task: task::spawn(async move {
                println!("Cleaning");
                cleaner::clean(&settings).await.unwrap();
            }),
            name: "Clean".to_string(),
        },
        false => ServerTask {
            task: task::spawn(async move {
                println!("Clean disabled");
            }),
            name: "Clean".to_string(),
        }
    }
}