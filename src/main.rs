pub mod util;

use reqwest::Client;
use clap::Parser;
use util::{files, cleaner};
use util::settings::default_settings;
use async_std::task::{self, JoinHandle};

use crate::util::web::download_file_progress_bar;
use crate::util::settings::Settings;

#[derive(Parser)]
struct Cli {
    /// Activate debug mode
    #[arg(short, long, default_value_t = false)]
    debug: bool,
    /// Full update
    #[arg(short, long, default_value_t = false)]
    update: bool,
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
    name: String
}

#[tokio::main]
async fn main() {

    // Load command line arguments
    let args = Cli::parse();

    // Load settings
    let settings  = Settings::load(&args.settings);

    // Tasks
    let mut tasks: Vec<ServerTask> = Vec::new();
    
    // Iris task
    tasks.push(ServerTask {
        task: task::spawn(async move {
            let iris_files = files::find_files_regex("", &settings.iris.regex).await.unwrap();
            if args.update || args.update_iris || iris_files.len() == 0 {
                if iris_files.len() > 0 {
                    files::delete_files(&iris_files).await.unwrap();
                }
                println!("Iris download todo");
            }
        }),
        name: "Iris".to_string()
    });

    // Server task
    let server_settings = settings.server.clone();
    tasks.push(ServerTask {
        task: task::spawn(async move {
            let server_files = files::find_files_regex("", &server_settings.regex).await.unwrap();
            if args.update || args.update_server || server_files.len() == 0 {
                println!("Updating server");
                if server_files.len() > 0 {
                    files::delete_files(&server_files).await.unwrap();
                }
                download_file_progress_bar(&Client::new(), &server_settings.download_url, &server_settings.name, true).await.unwrap();
            }
        }),
        name: "Server".to_string()
    });

    // Plugin tasks
    for plugin in &settings.plugins {
        let plugin_settings = plugin.clone();
        tasks.push(ServerTask {
            task: task::spawn(async move {
                let plugin_files = files::find_files_regex("", &plugin_settings.regex).await.unwrap();
                if args.update || args.update_plugins || plugin_files.len() == 0 {
                    println!("Updating plugin {}", plugin_settings.name);
                    if plugin_files.len() > 0 {
                        files::delete_files(&plugin_files).await.unwrap();
                    }
                    download_file_progress_bar(&Client::new(), &plugin_settings.download_url, &("./plugins/".to_string() + &plugin_settings.name), true).await.unwrap();
                }
            }),
            name: plugin.name.clone()
        });
    }

    // Clean task
    let clean_settings = settings.clean.clone();
    tasks.push(ServerTask {
        task: task::spawn(async move {
            cleaner::clean(&clean_settings).await.unwrap();
        }),
        name: "Clean".to_string()
    });

    // Print task details
    println!("Scheduled {} tasks: {}", tasks.len(), tasks.iter().map(|t| t.name.as_str()).collect::<Vec<&str>>().join(", "));

    // Wait for tasks to finish
    for task in tasks {
        println!("Waiting for task {}", task.name);
        task.task.await;
    }

    // Start server
    todo!("Start server");
}