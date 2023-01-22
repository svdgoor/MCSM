pub mod util;

use reqwest::Client;
use clap::Parser;

use crate::util::web::download_file_progress_bar;

#[derive(Parser)]
#[clap(version = "1.0", author = "Author Name")]
struct Opts {
    /// Activate debug mode
    #[clap(short, long)]
    debug: bool,
    /// Re-build Iris distr
    #[clap(short, long)]
    update_iris: bool,
    /// Update to latest server version
    #[clap(short, long)]
    update_server: bool,
}

#[tokio::main]
async fn main() {
    let opts = Opts::parse();
    
    let client = Client::new();
    let url = "https://www.rust-lang.org/logos/rust-logo-512x512.png";
    let path = "rust-logo.png";
    download_file_progress_bar(&client, url, path, true).await.unwrap();
}