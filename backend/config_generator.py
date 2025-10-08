"""
Configuration file generators for integration auto-configuration
Generates config files for MQTT, Grafana datasources, Traefik, etc.
"""
from typing import Dict, List, Any, Optional
import yaml


def generate_prometheus_config() -> str:
    """Generate minimal Prometheus configuration file"""
    config = """global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""
    return config


def generate_mosquitto_config(username: str = "", password: str = "", enable_tls: bool = False,
                                tls_port: int = 8883) -> str:
    """Generate Mosquitto configuration file"""
    config = []

    # Listener configuration
    config.append("listener 1883")
    config.append("protocol mqtt")
    config.append("")

    if enable_tls:
        config.append(f"listener {tls_port}")
        config.append("protocol mqtt")
        config.append("# TLS configuration - add certificate paths here")
        config.append("# cafile /mosquitto/config/ca.crt")
        config.append("# certfile /mosquitto/config/server.crt")
        config.append("# keyfile /mosquitto/config/server.key")
        config.append("")

    # Authentication
    if username and password:
        config.append("allow_anonymous false")
        config.append("password_file /mosquitto/config/passwd")
    else:
        config.append("allow_anonymous true")

    config.append("")
    config.append("# Persistence")
    config.append("persistence true")
    config.append("persistence_location /mosquitto/data/")
    config.append("")
    config.append("# Logging")
    config.append("log_dest file /mosquitto/log/mosquitto.log")
    config.append("log_dest stdout")
    config.append("log_type all")

    return "\n".join(config)


def generate_mosquitto_password_file(username: str, password: str) -> str:
    """
    Generate Mosquitto password file content
    Note: This generates plain text. Users should run mosquitto_passwd to hash it.
    """
    return f"""# Mosquitto password file
# Run 'docker exec mosquitto mosquitto_passwd -U /mosquitto/config/passwd' to hash passwords

# Username: {username}
# This is a placeholder - password must be hashed using mosquitto_passwd
# Run: docker exec <container> mosquitto_passwd -b /mosquitto/config/passwd {username} {password}
"""


def generate_emqx_config(username: str = "", password: str = "", enable_tls: bool = False) -> str:
    """Generate EMQX configuration snippet"""
    config = {
        "authentication": []
    }

    if username and password:
        config["authentication"].append({
            "mechanism": "password_based",
            "backend": "built_in_database",
            "user_id_type": "username"
        })

    return yaml.dump(config, default_flow_style=False)


def generate_grafana_datasources(datasources: List[Dict[str, Any]]) -> str:
    """
    Generate Grafana datasource provisioning configuration

    datasources format:
    [
        {"type": "prometheus", "instance_name": "prometheus", "config": {}},
        {"type": "postgres", "instance_name": "postgres-1", "config": {...}},
    ]
    """
    provisioning = {
        "apiVersion": 1,
        "datasources": []
    }

    for idx, ds in enumerate(datasources):
        ds_type = ds.get("type")
        instance_name = ds.get("instance_name")
        config = ds.get("config", {})

        if ds_type == "prometheus":
            provisioning["datasources"].append({
                "name": "Prometheus",
                "type": "prometheus",
                "access": "proxy",
                "url": f"http://{instance_name}:9090",
                "isDefault": idx == 0,
                "editable": True
            })

        elif ds_type == "postgres":
            db_name = config.get("database", "postgres")
            db_user = config.get("username", "postgres")
            db_password = config.get("password", "postgres")
            port = config.get("port", 5432)

            provisioning["datasources"].append({
                "name": f"PostgreSQL-{instance_name}",
                "type": "postgres",
                "access": "proxy",
                "url": f"{instance_name}:{port}",
                "database": db_name,
                "user": db_user,
                "secureJsonData": {
                    "password": db_password
                },
                "jsonData": {
                    "sslmode": "disable",
                    "postgresVersion": 1400
                },
                "editable": True
            })

        elif ds_type == "mysql" or ds_type == "mariadb":
            db_name = config.get("database", "mysql")
            db_user = config.get("username", "root")
            db_password = config.get("password", "password")
            port = config.get("port", 3306)

            provisioning["datasources"].append({
                "name": f"MySQL-{instance_name}",
                "type": "mysql",
                "access": "proxy",
                "url": f"{instance_name}:{port}",
                "database": db_name,
                "user": db_user,
                "secureJsonData": {
                    "password": db_password
                },
                "editable": True
            })

        elif ds_type == "loki":
            provisioning["datasources"].append({
                "name": "Loki",
                "type": "loki",
                "access": "proxy",
                "url": f"http://{instance_name}:3100",
                "editable": True
            })

    return yaml.dump(provisioning, default_flow_style=False, sort_keys=False)


def generate_traefik_static_config(enable_https: bool = False, letsencrypt_email: str = "") -> str:
    """Generate Traefik static configuration (traefik.yml)"""
    config = {
        "api": {
            "dashboard": True,
            "insecure": True
        },
        "entryPoints": {
            "web": {
                "address": ":80"
            }
        },
        "providers": {
            "docker": {
                "exposedByDefault": False,
                "network": "iiot-network"
            },
            "file": {
                "directory": "/etc/traefik/dynamic",
                "watch": True
            }
        },
        "log": {
            "level": "INFO"
        }
    }

    if enable_https:
        config["entryPoints"]["websecure"] = {
            "address": ":443"
        }

        if letsencrypt_email:
            config["certificatesResolvers"] = {
                "letsencrypt": {
                    "acme": {
                        "email": letsencrypt_email,
                        "storage": "/letsencrypt/acme.json",
                        "httpChallenge": {
                            "entryPoint": "web"
                        }
                    }
                }
            }

    return yaml.dump(config, default_flow_style=False, sort_keys=False)


def generate_traefik_dynamic_config(services: List[Dict[str, Any]], domain: str = "localhost",
                                     enable_https: bool = False) -> str:
    """
    Generate Traefik dynamic configuration for services

    services format:
    [
        {"instance_name": "ignition-1", "subdomain": "ignition", "port": 8088},
        {"instance_name": "grafana", "subdomain": "grafana", "port": 3000}
    ]
    """
    config = {
        "http": {
            "routers": {},
            "services": {}
        }
    }

    for svc in services:
        instance_name = svc["instance_name"]
        subdomain = svc.get("subdomain", instance_name)
        port = svc["port"]

        # Router configuration
        router_name = f"{instance_name}-router"
        config["http"]["routers"][router_name] = {
            "rule": f"Host(`{subdomain}.{domain}`)",
            "service": instance_name,
            "entryPoints": ["websecure" if enable_https else "web"]
        }

        if enable_https:
            config["http"]["routers"][router_name]["tls"] = {
                "certResolver": "letsencrypt"
            }

        # Service configuration
        config["http"]["services"][instance_name] = {
            "loadBalancer": {
                "servers": [
                    {"url": f"http://{instance_name}:{port}"}
                ]
            }
        }

    return yaml.dump(config, default_flow_style=False, sort_keys=False)


def generate_ignition_db_setup_script(databases: List[Dict[str, Any]]) -> str:
    """
    Generate script to auto-configure databases in Ignition

    databases format:
    [
        {"type": "postgres", "instance_name": "postgres-1", "config": {...}},
        {"type": "mariadb", "instance_name": "mariadb-1", "config": {...}}
    ]
    """
    script = """#!/bin/bash
# Ignition Database Auto-Configuration Script
# This script configures database connections in Ignition via the Gateway API

# Wait for Ignition Gateway to be ready
echo "Waiting for Ignition Gateway to be ready..."
until curl -sf http://localhost:8088/StatusPing > /dev/null; do
    echo "Waiting..."
    sleep 5
done

echo "Ignition Gateway is ready!"

# Note: Database configuration via API requires additional setup
# For now, connection details are provided in README for manual configuration

echo "Database connection details are available in the README file."
"""

    for db in databases:
        db_type = db["type"]
        instance_name = db["instance_name"]
        config = db.get("config", {})

        script += f"\n# {db_type.upper()} Connection: {instance_name}\n"

        if db_type == "postgres":
            db_name = config.get("database", "postgres")
            db_user = config.get("username", "postgres")
            db_password = config.get("password", "postgres")
            port = config.get("port", 5432)

            script += f"# JDBC URL: jdbc:postgresql://{instance_name}:{port}/{db_name}\n"
            script += f"# Username: {db_user}\n"
            script += f"# Password: {db_password}\n"

        elif db_type in ["mariadb", "mysql"]:
            db_name = config.get("database", "mysql")
            db_user = config.get("username", "root")
            db_password = config.get("password", "password")
            port = config.get("port", 3306)

            script += f"# JDBC URL: jdbc:mysql://{instance_name}:{port}/{db_name}\n"
            script += f"# Username: {db_user}\n"
            script += f"# Password: {db_password}\n"

        elif db_type == "mssql":
            db_user = config.get("username", "sa")
            db_password = config.get("sa_password", "YourStrong!Passw0rd")
            port = config.get("port", 1433)

            script += f"# JDBC URL: jdbc:sqlserver://{instance_name}:{port}\n"
            script += f"# Username: {db_user}\n"
            script += f"# Password: {db_password}\n"

    return script


def generate_oauth_env_vars(service_id: str, provider: str, realm_name: str = "iiot",
                             base_domain: str = "localhost", client_secret: str = None) -> Dict[str, str]:
    """
    Generate OAuth environment variables for a service
    """
    env_vars = {}

    keycloak_base = f"http://{provider}:8080/realms/{realm_name}/protocol/openid-connect"

    # Use provided client secret or fallback to placeholder
    if not client_secret:
        client_secret = f"{service_id}-secret-changeme"

    if service_id == "grafana":
        env_vars.update({
            "GF_AUTH_GENERIC_OAUTH_ENABLED": "true",
            "GF_AUTH_GENERIC_OAUTH_NAME": "Keycloak",
            "GF_AUTH_GENERIC_OAUTH_CLIENT_ID": "grafana",
            "GF_AUTH_GENERIC_OAUTH_CLIENT_SECRET": client_secret,
            "GF_AUTH_GENERIC_OAUTH_SCOPES": "openid profile email",
            "GF_AUTH_GENERIC_OAUTH_AUTH_URL": f"{keycloak_base}/auth",
            "GF_AUTH_GENERIC_OAUTH_TOKEN_URL": f"{keycloak_base}/token",
            "GF_AUTH_GENERIC_OAUTH_API_URL": f"{keycloak_base}/userinfo",
            "GF_AUTH_GENERIC_OAUTH_ALLOW_SIGN_UP": "true",
            "GF_AUTH_GENERIC_OAUTH_ROLE_ATTRIBUTE_PATH": "contains(roles[*], 'admin') && 'Admin' || 'Viewer'"
        })

    elif service_id == "portainer":
        env_vars.update({
            "PORTAINER_OAUTH_ENABLED": "true",
            "PORTAINER_OAUTH_PROVIDER": "custom",
            "PORTAINER_OAUTH_CLIENT_ID": "portainer",
            "PORTAINER_OAUTH_CLIENT_SECRET": client_secret,
            "PORTAINER_OAUTH_AUTH_URL": f"{keycloak_base}/auth",
            "PORTAINER_OAUTH_TOKEN_URL": f"{keycloak_base}/token",
            "PORTAINER_OAUTH_USER_URL": f"{keycloak_base}/userinfo"
        })

    elif service_id == "n8n":
        env_vars.update({
            "N8N_OAUTH_ENABLED": "true",
            "N8N_OAUTH_CLIENT_ID": "n8n",
            "N8N_OAUTH_CLIENT_SECRET": client_secret,
            "N8N_OAUTH_AUTH_URL": f"{keycloak_base}/auth",
            "N8N_OAUTH_TOKEN_URL": f"{keycloak_base}/token"
        })

    return env_vars


def generate_email_env_vars(service_id: str, mailhog_instance: str = "mailhog",
                              from_address: str = "noreply@iiot.local") -> Dict[str, str]:
    """
    Generate email/SMTP environment variables for services
    """
    env_vars = {}

    if service_id == "grafana":
        env_vars.update({
            "GF_SMTP_ENABLED": "true",
            "GF_SMTP_HOST": f"{mailhog_instance}:1025",
            "GF_SMTP_FROM_ADDRESS": from_address,
            "GF_SMTP_FROM_NAME": "Grafana",
            "GF_SMTP_SKIP_VERIFY": "true"
        })

    elif service_id == "ignition":
        # Ignition SMTP is configured via Gateway config, not env vars
        # But we can add placeholders for documentation
        env_vars.update({
            "GATEWAY_SMTP_HOST": mailhog_instance,
            "GATEWAY_SMTP_PORT": "1025",
            "GATEWAY_SMTP_FROM": from_address
        })

    elif service_id == "n8n":
        env_vars.update({
            "N8N_EMAIL_MODE": "smtp",
            "N8N_SMTP_HOST": mailhog_instance,
            "N8N_SMTP_PORT": "1025",
            "N8N_SMTP_SENDER": from_address
        })

    elif service_id == "keycloak":
        env_vars.update({
            "KC_SMTP_HOST": mailhog_instance,
            "KC_SMTP_PORT": "1025",
            "KC_SMTP_FROM": from_address
        })

    return env_vars
