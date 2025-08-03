use std::fs;
use std::path::Path;

use paris::*;
use std::collections::HashSet;
use tokio_postgres::NoTls;
use uuid::Uuid;

pub fn is_docker() -> bool {
    Path::new("/.dockerenv").exists()
}

pub async fn init_db() {
    let mut host = "localhost";
    if is_docker() {
        host = "pgbouncer";
    }

    let (client, connection) = tokio_postgres::connect(
        &format!(
            "user=connectorlib password=connectorlib dbname=connectorlib host={}",
            host
        ),
        NoTls,
    )
    .await
    .unwrap();

    let handle = tokio::spawn(async move {
        if let Err(e) = &connection.await {
            error!("connection error: {}", e);
        }
    });

    let config_sql = match fs::read_to_string("config.sql") {
        Ok(content) => content,
        Err(e) => {
            error!("Failed to read config.sql: {}", e);
            return;
        }
    };

    let mut expected_tables = HashSet::new();
    for line in config_sql.lines() {
        let line = line.trim().to_lowercase();
        if line.starts_with("create table") {
            let parts: Vec<&str> = line.split_whitespace().collect();
            if parts.len() >= 3 {
                let table_name = parts[2].trim_end_matches('(').to_string();
                expected_tables.insert(table_name.replace("\"", ""));
            }
        }
    }

    let current_tables = match client
        .query(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'",
            &[],
        )
        .await
    {
        Ok(rows) => {
            let mut tables = HashSet::new();
            for row in rows {
                let table_name: String = row.get(0);
                tables.insert(table_name);
            }
            tables
        }
        Err(e) => {
            error!("Failed to get current tables: {}", e);
            return;
        }
    };

    let mut schema_matches = expected_tables == current_tables;
    if schema_matches {
        for table_name in &expected_tables {
            match client
                .query(
                    "SELECT column_name FROM information_schema.columns 
                     WHERE table_name = $1 AND table_schema = 'public'",
                    &[table_name],
                )
                .await
            {
                Ok(rows) => {
                    if rows.is_empty() {
                        schema_matches = false;
                        break;
                    }
                }
                Err(_) => {
                    schema_matches = false;
                    break;
                }
            }
        }
    }

    if !schema_matches {
        warn!("Schema mismatch detected. Recreating database...");
        let remaining_tables: Vec<String> = current_tables.iter().cloned().collect();
        let mut max_attempts = current_tables.len() * 2;
        let mut tables_to_drop = remaining_tables;

        while !tables_to_drop.is_empty() && max_attempts > 0 {
            let mut dropped_any = false;
            let mut i = 0;

            while i < tables_to_drop.len() {
                let table_name = &tables_to_drop[i];
                let drop_sql = format!("DROP TABLE IF EXISTS {} CASCADE", table_name);

                match client.execute(&drop_sql, &[]).await {
                    Ok(_) => {
                        info!("Dropped table: {}", table_name);
                        tables_to_drop.remove(i);
                        dropped_any = true;
                    }
                    Err(e) => {
                        error!("Failed to drop table {}: {}", table_name, e);
                        i += 1;
                    }
                }
            }

            if !dropped_any {
                for table_name in &tables_to_drop {
                    let drop_sql = format!("DROP TABLE IF EXISTS {} CASCADE", table_name);
                    if let Err(e) = client.execute(&drop_sql, &[]).await {
                        error!("Failed to force drop table {}: {}", table_name, e);
                    } else {
                        info!("Force dropped table: {}", table_name);
                    }
                }
                break;
            }

            max_attempts -= 1;
        }

        let mut statements = Vec::new();
        let mut current_statement = String::new();
        let mut in_string = false;
        let mut escape_next = false;

        for ch in config_sql.chars() {
            if escape_next {
                current_statement.push(ch);
                escape_next = false;
                continue;
            }

            match ch {
                '\\' if in_string => {
                    current_statement.push(ch);
                    escape_next = true;
                }
                '\'' => {
                    current_statement.push(ch);
                    in_string = !in_string;
                }
                ';' if !in_string => {
                    current_statement.push(ch);
                    statements.push(current_statement.trim().to_string());
                    current_statement.clear();
                }
                _ => {
                    current_statement.push(ch);
                }
            }
        }

        if !current_statement.trim().is_empty() {
            statements.push(current_statement.trim().to_string());
        }

        for statement in statements {
            let statement = statement.trim();
            if statement.is_empty() || statement.starts_with("--") {
                continue;
            }

            if let Err(e) = client.execute(statement, &[]).await {
                error!("Failed to execute statement: {}", e);
                return;
            }
        }
    }

    handle.abort();
}

pub async fn get_username(uuid: Uuid, hclient: &reqwest::Client) -> Result<String, String> {
    let response = hclient
        .get(format!(
            "https://playerdb.co/api/player/minecraft/{}",
            uuid.to_string()
        ))
        .send()
        .await;

    if response.is_err() {
        return Err("Failed to send request".to_string());
    }

    let response = response.unwrap().json::<serde_json::Value>().await.unwrap();
    let username = response["data"]["player"]["username"].as_str();

    if username.is_none() || username.unwrap().is_empty() {
        return Err("Failed to get username".to_string());
    }

    Ok(username.unwrap().to_string())
}
