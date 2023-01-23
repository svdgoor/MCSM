use std::{fs::File, io::{Read, Write}, path::Path};

use serde::{Deserialize, Serialize};

/// Default settings toml
pub fn default_settings() -> String {
    "settings.toml".to_string()
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct Settings {
    pub debug: bool,
    pub server: ServerSoftwareSettings,
    pub clean: CleanSettings,
    pub plugins: Vec<PluginSettings>,
    pub iris: IrisSettings,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct ServerSoftwareSettings {
    pub name: String,
    pub regex: String,
    pub download_url: String,
    pub reboot_delay: u32,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct CleanSettings {
    pub enabled: bool,
    pub also_on_reboot: bool,
    pub folders: Vec<String>,
    pub files: Vec<String>,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct PluginSettings {
    pub name: String,
    pub enabled: bool,
    pub regex: String,
    pub download_url: String,
}

#[derive(Debug, Deserialize, Serialize, Clone)]
pub struct IrisSettings {
    pub enabled: bool,
    pub regex: String,
    pub repo_url: String,
    pub repo_branch: String,
    pub repo_path: String,
}

fn generate_default_settings() -> Settings { 
    Settings {
        debug: false,
        server: ServerSoftwareSettings {
            name: "purpur.jar".to_string(),
            regex: "purpur.*\\.jar".to_string(),
            download_url: "https://api.purpurmc.org/v2/purpur/1.19.3/latest/download".to_string(),
            reboot_delay: 5,
        },
        clean: CleanSettings {
            enabled: false,
            also_on_reboot: false,
            folders: vec![
                "./crash-reports".to_string(),
                "./logs".to_string(),
                "./w".to_string(),
                "./v".to_string(),
                "./x".to_string(),
                "./y".to_string(),
                "./z".to_string(),
                "./k".to_string(),
                "./l".to_string(),
                "./o".to_string(),
                "./world/advancements".to_string(),
                "./world/data".to_string(),
                "./world/entities".to_string(),
                "./world/playerdata".to_string(),
                "./world/poi".to_string(),
                "./world/region".to_string(),
                "./world/stats".to_string(),
                "./world_nether".to_string(),
                "./world_the_end".to_string(),
                "./versions".to_string(),
                "./plugins/*/*".to_string(),
            ],
            files: vec![
                "version_history.json".to_string(),
                ".console_history".to_string(),
                "banned-ips.json".to_string(),
                "banned-players.json".to_string(),
                "commands.yml".to_string(),
                "help.yml".to_string(),
                "permissions.yml".to_string(),
                "wepif.yml".to_string(),
                "whitelist.json".to_string(),
                "usercache.json".to_string(),
                "./world/level.dat".to_string(),
                "./world/level.dat_old".to_string(),
                "./world/session.lock".to_string(),
                "./world/uid.dat".to_string(),
            ]
        },
        plugins: vec![
            PluginSettings {
                name: "EssentialsX".to_string(),
                enabled: true,
                regex: "EssentialsX-?.*\\.jar".to_string(),
                download_url: "https://github.com/EssentialsX/Essentials/releases/download/2.19.4/EssentialsX-2.19.4.jar".to_string(),
            },
            PluginSettings {
                name: "WorldEdit".to_string(),
                enabled: true,
                regex: "WorldEdit-Bukkit?.*\\.jar".to_string(),
                download_url: "https://dev.bukkit.org/projects/worldedit/files/latest".to_string(),
            },
            PluginSettings {
                name: "BileTools".to_string(),
                enabled: true,
                regex: "BileTools-?.*\\.jar".to_string(),
                download_url: "https://github.com/VolmitSoftware/BileTools/releases/download/2/BileTools-2.jar".to_string(),
            },
            PluginSettings {
                name: "Rift".to_string(),
                enabled: true,
                regex: "Rift-?.*\\.jar".to_string(),
                download_url: "https://github.com/VolmitSoftware/Rift/releases/download/1.0.1/Rift-1.0.1.jar".to_string(),
            },
        ],
        iris: IrisSettings {
            enabled: true,
            regex: "Iris-?.*\\.jar".to_string(),
            repo_url: "https://github.com/VolmitSoftware/Iris.git".to_string(),
            repo_branch: "master".to_string(),
            repo_path: "plugins/Iris/repo".to_string(),
        }
    }
}

impl Settings {
    pub fn load(path: &str) -> Settings {
        match !Path::new(path).exists() {
            true => {
                let mut file = File::create(path).unwrap();
                let settings = generate_default_settings();
                file.write_all(toml::to_string(&settings).unwrap().as_bytes()).unwrap();
                settings
            }
            false => {
                let mut file = File::open(path).unwrap();
                let mut contents = String::new();
                file.read_to_string(&mut contents).unwrap();
                toml::from_str(&contents).unwrap()
            }
        }
    }
}