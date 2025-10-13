"""
IIoT Stack Builder API
FastAPI backend for generating Docker Compose stacks for industrial IoT applications.
"""

import base64
import io
import json
import logging
import zipfile
from typing import Any, Dict, List, Optional

import yaml
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# Import authentication and user management routers
import auth_router
import settings_router
import stacks_router
from config_generator import (generate_email_env_vars,
                              generate_grafana_datasources,
                              generate_mosquitto_config,
                              generate_mosquitto_password_file,
                              generate_oauth_env_vars,
                              generate_prometheus_config,
                              generate_traefik_dynamic_config,
                              generate_traefik_static_config)
from database import check_db_connection
from docker_hub import (get_docker_tags, get_ignition_versions,
                        get_postgres_versions)
from ignition_db_registration import (generate_ignition_db_readme_section,
                                      generate_ignition_db_registration_script,
                                      generate_requirements_file)
from integration_engine import get_integration_engine
from keycloak_generator import (generate_keycloak_readme_section,
                                generate_keycloak_realm)
from ntfy_monitor import (generate_ntfy_monitor_script,
                          generate_ntfy_readme_section)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="IIoT Stack Builder API", version="2.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication and user management routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(stacks_router.router, prefix="/api")
app.include_router(settings_router.router, prefix="/api")


# Database connection check on startup
@app.on_event("startup")
async def startup_event():
    """Check database connection on startup"""
    logger.info("Starting IIoT Stack Builder API...")
    if check_db_connection():
        logger.info("✓ Database connection established")
    else:
        logger.warning("⚠ Database connection failed - auth features may not work")


def load_catalog():
    """Load the application catalog from catalog.json"""
    with open("catalog.json", "r") as f:
        return json.load(f)


class InstanceConfig(BaseModel):
    """Configuration for a single service instance"""

    app_id: str
    instance_name: str
    config: Dict[str, Any]
    instanceId: Optional[float] = None


class GlobalSettings(BaseModel):
    """Global settings for the entire stack"""

    stack_name: str = "iiot-stack"
    timezone: str = "Australia/Adelaide"
    restart_policy: str = "unless-stopped"
    ntfy_enabled: bool = False
    ntfy_server: str = "https://ntfy.sh"
    ntfy_topic: str = ""


class IntegrationSettings(BaseModel):
    """Settings for automatic integrations"""

    reverse_proxy: Optional[Dict[str, Any]] = {
        "base_domain": "localhost",
        "enable_https": False,
        "letsencrypt_email": "",
    }
    mqtt: Optional[Dict[str, Any]] = {
        "enable_tls": False,
        "username": "",
        "password": "",
        "tls_port": 8883,
    }
    oauth: Optional[Dict[str, Any]] = {
        "realm_name": "iiot",
        "auto_configure_services": True,
    }
    database: Optional[Dict[str, Any]] = {"auto_register": True}
    email: Optional[Dict[str, Any]] = {
        "from_address": "noreply@iiot.local",
        "auto_configure_services": True,
    }


class StackConfig(BaseModel):
    """Complete stack configuration with instances and global settings"""

    instances: List[InstanceConfig]
    integrations: List[str] = []
    global_settings: Optional[GlobalSettings] = None
    integration_settings: Optional[IntegrationSettings] = None


@app.get("/")
def read_root():
    return {"message": "IIoT Stack Builder API", "version": "1.0.0"}


@app.get("/api/catalog")
def get_catalog():
    """Get the application catalog"""
    return load_catalog()


@app.post("/validate-config")
def validate_config(config: StackConfig):
    """Validate and sanitize an imported stack configuration"""
    try:
        catalog = load_catalog()
        catalog_dict = {app["id"]: app for app in catalog["applications"]}

        # Validate all instances reference valid apps
        for instance in config.instances:
            if instance.app_id not in catalog_dict:
                raise HTTPException(
                    status_code=400, detail=f"Invalid app_id: {instance.app_id}"
                )

            app = catalog_dict[instance.app_id]
            if not app.get("enabled", False):
                raise HTTPException(
                    status_code=400, detail=f"App {instance.app_id} is not enabled"
                )

        # Return validated config
        return {
            "valid": True,
            "config": config.dict(),
            "message": "Configuration is valid",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Config validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid configuration: {str(e)}")


@app.get("/versions/{app_id}")
def get_versions(app_id: str):
    """Get available versions for a specific application from Docker Hub"""
    try:
        if app_id == "ignition":
            versions = get_ignition_versions()
        elif app_id == "postgres":
            versions = get_postgres_versions()
        else:
            # For other apps, try to fetch from catalog and Docker Hub
            catalog = load_catalog()
            app = next((a for a in catalog["applications"] if a["id"] == app_id), None)
            if app and "image" in app:
                versions = get_docker_tags(app["image"], limit=50)
                if not versions:
                    # Fallback to catalog versions if API fails
                    versions = app.get("available_versions", ["latest"])
            else:
                return {"versions": ["latest"]}

        return {"versions": versions}
    except Exception as e:
        logger.error(f"Error fetching versions for {app_id}: {e}")
        # Fallback to catalog versions
        catalog = load_catalog()
        app = next((a for a in catalog["applications"] if a["id"] == app_id), None)
        if app:
            return {"versions": app.get("available_versions", ["latest"])}
        return {"versions": ["latest"]}


@app.post("/upload-module")
async def upload_module(file: UploadFile = File(...)):
    """
    Upload a 3rd party Ignition module file (.modl)
    Returns base64 encoded file content that can be included in the stack
    """
    try:
        if not file.filename.endswith(".modl"):
            raise HTTPException(status_code=400, detail="Only .modl files are allowed")

        # Read file content
        content = await file.read()

        # Encode as base64 for storage/transfer
        encoded = base64.b64encode(content).decode("utf-8")

        return {"filename": file.filename, "size": len(content), "encoded": encoded}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/detect-integrations")
def detect_integrations(stack_config: StackConfig):
    """
    Detect possible integrations, conflicts, and recommendations
    based on selected services
    """
    try:
        # Convert instances to dict format for integration engine
        instances = [
            {
                "app_id": inst.app_id,
                "instance_name": inst.instance_name,
                "config": inst.config,
            }
            for inst in stack_config.instances
        ]

        # Get integration engine and detect integrations
        engine = get_integration_engine()
        detection_result = engine.detect_integrations(instances)

        # Add human-readable summary
        detection_result["summary"] = engine.get_integration_summary(detection_result)

        return detection_result

    except Exception as e:
        logger.error(f"Error detecting integrations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate")
def generate_stack(stack_config: StackConfig):
    """Generate docker-compose.yml and configuration files"""
    try:
        catalog = load_catalog()
        catalog_dict = {app["id"]: app for app in catalog["applications"]}

        # Get global settings
        global_settings = stack_config.global_settings or GlobalSettings()

        # Get integration settings
        integration_settings = (
            stack_config.integration_settings or IntegrationSettings()
        )

        # Detect integrations
        instances_for_detection = [
            {
                "app_id": inst.app_id,
                "instance_name": inst.instance_name,
                "config": inst.config,
            }
            for inst in stack_config.instances
        ]
        engine = get_integration_engine()
        integration_results = engine.detect_integrations(instances_for_detection)

        # Build docker compose structure
        stack_name = global_settings.stack_name
        compose = {
            "name": stack_name,
            "services": {},
            "networks": {f"{stack_name}-network": {"driver": "bridge"}},
            "volumes": {},
        }

        # Track generated config files
        config_files = {}

        env_vars = []
        env_vars.append("# Global Settings")
        env_vars.append(f"TZ={global_settings.timezone}")
        env_vars.append(f"RESTART_POLICY={global_settings.restart_policy}")
        env_vars.append("")

        # Check if Traefik is in the stack
        has_traefik = any(inst.app_id == "traefik" for inst in stack_config.instances)
        has_oauth_provider = "oauth_provider" in integration_results.get(
            "integrations", {}
        )
        has_email_testing = "email_testing" in integration_results.get(
            "integrations", {}
        )
        has_mqtt_broker = "mqtt_broker" in integration_results.get("integrations", {})

        # Pre-generate Keycloak realm configuration if needed (for OAuth client secrets)
        keycloak_clients = []
        keycloak_realm_config = None
        if has_oauth_provider and integration_settings.oauth.get(
            "auto_configure_services", True
        ):
            oauth_int = integration_results["integrations"]["oauth_provider"]
            keycloak_providers = [
                p for p in oauth_int.get("providers", []) if p == "keycloak"
            ]

            if keycloak_providers:
                # Get list of services that will be OAuth clients
                oauth_client_services = [
                    client["service_id"] for client in oauth_int.get("clients", [])
                ]

                # Get users from integration settings
                realm_users = integration_settings.oauth.get("realm_users", [])

                # Generate realm configuration
                realm_name = integration_settings.oauth.get("realm_name", "iiot")
                base_domain = integration_settings.reverse_proxy.get(
                    "base_domain", "localhost"
                )
                enable_https = integration_settings.reverse_proxy.get(
                    "enable_https", False
                )

                keycloak_realm_config = generate_keycloak_realm(
                    realm_name=realm_name,
                    services=oauth_client_services,
                    users=realm_users,
                    base_domain=base_domain,
                    enable_https=enable_https,
                )

                # Store clients for use in OAuth env vars and README
                keycloak_clients = keycloak_realm_config.get("clients", [])

        # Handle pgadmin/phpmyadmin checkboxes - add instances dynamically
        instances_to_process = list(stack_config.instances)
        for instance in stack_config.instances:
            if instance.app_id == "postgres" and instance.config.get("include_pgadmin"):
                # Add pgAdmin instance
                pgadmin_instance = InstanceConfig(
                    app_id="pgadmin",
                    instance_name="pgadmin",
                    config={
                        "port": 5050,
                        "email": "admin@admin.com",
                        "password": "admin",
                    },
                    instanceId=None,
                )
                instances_to_process.append(pgadmin_instance)
            elif instance.app_id == "mariadb" and instance.config.get(
                "include_phpmyadmin"
            ):
                # Add phpMyAdmin instance
                phpmyadmin_instance = InstanceConfig(
                    app_id="phpmyadmin",
                    instance_name="phpmyadmin",
                    config={"port": 8080},
                    instanceId=None,
                )
                instances_to_process.append(phpmyadmin_instance)

        # Process each instance
        for instance in instances_to_process:
            app = catalog_dict.get(instance.app_id)
            if not app or not app.get("enabled", False):
                continue

            service_name = instance.instance_name
            config = instance.config

            # Build image name with version
            version = config.get("version", app.get("default_version", "latest"))
            image = f"{app['image']}:{version}"

            # Create service definition
            service = {
                "image": image,
                "container_name": f"{stack_name}-{service_name}",
                "networks": [f"{stack_name}-network"],
                "restart": global_settings.restart_policy,
            }

            # Handle ports
            if "ports" in app["default_config"]:
                ports = []
                for port_mapping in app["default_config"]["ports"]:
                    if ":" in port_mapping:
                        container_port = port_mapping.split(":")[1]
                        # Check for various port config options
                        if instance.app_id == "postgres":
                            host_port = config.get("port", port_mapping.split(":")[0])
                        elif instance.app_id == "ignition":
                            if container_port == "8088":
                                host_port = config.get(
                                    "http_port", port_mapping.split(":")[0]
                                )
                            elif container_port == "8043":
                                host_port = config.get(
                                    "https_port", port_mapping.split(":")[0]
                                )
                            else:
                                host_port = port_mapping.split(":")[0]
                        elif instance.app_id == "keycloak":
                            host_port = config.get("port", port_mapping.split(":")[0])
                        elif instance.app_id == "traefik":
                            if container_port == "80":
                                host_port = config.get("http_port", 80)
                            elif container_port == "443":
                                host_port = config.get("https_port", 443)
                            elif container_port == "8080":
                                host_port = config.get("dashboard_port", 8080)
                            else:
                                host_port = port_mapping.split(":")[0]
                        else:
                            host_port = config.get(
                                "port",
                                config.get("http_port", port_mapping.split(":")[0]),
                            )

                        ports.append(f"{host_port}:{container_port}")
                    else:
                        ports.append(port_mapping)
                service["ports"] = ports

            # Handle environment variables
            if "environment" in app["default_config"]:
                env = app["default_config"]["environment"].copy()
                env["TZ"] = global_settings.timezone

                # Update with configured values based on app type
                if instance.app_id == "postgres":
                    env["POSTGRES_DB"] = config.get("database", env.get("POSTGRES_DB"))
                    env["POSTGRES_USER"] = config.get(
                        "username", env.get("POSTGRES_USER")
                    )
                    env["POSTGRES_PASSWORD"] = config.get(
                        "password", env.get("POSTGRES_PASSWORD")
                    )

                elif instance.app_id == "mariadb":
                    env["MYSQL_DATABASE"] = config.get(
                        "database", env.get("MYSQL_DATABASE")
                    )
                    env["MYSQL_USER"] = config.get("username", env.get("MYSQL_USER"))
                    env["MYSQL_PASSWORD"] = config.get(
                        "password", env.get("MYSQL_PASSWORD")
                    )
                    env["MYSQL_ROOT_PASSWORD"] = config.get(
                        "root_password", env.get("MYSQL_ROOT_PASSWORD")
                    )

                elif instance.app_id == "mssql":
                    env["SA_PASSWORD"] = config.get(
                        "sa_password", env.get("SA_PASSWORD")
                    )
                    env["MSSQL_PID"] = config.get("edition", env.get("MSSQL_PID"))

                elif instance.app_id == "ignition":
                    env["GATEWAY_ADMIN_USERNAME"] = config.get(
                        "admin_username", env.get("GATEWAY_ADMIN_USERNAME")
                    )
                    env["GATEWAY_ADMIN_PASSWORD"] = config.get(
                        "admin_password", env.get("GATEWAY_ADMIN_PASSWORD")
                    )
                    env["IGNITION_EDITION"] = config.get(
                        "edition", env.get("IGNITION_EDITION", "standard")
                    )

                    # Determine version to decide which modules field to use
                    version = config.get("version", "latest")
                    is_83_or_later = False
                    # "latest" maps to 8.3+, so treat it as 8.3
                    if version == "latest" or (
                        version.startswith("8.3")
                        or version.startswith("8.4")
                        or version.startswith("9")
                    ):
                        is_83_or_later = True

                    # Handle modules - convert array to comma-separated string
                    # Check for version-specific module fields first, then fall back to legacy "modules" field
                    if is_83_or_later:
                        modules = config.get("modules_83", config.get("modules", []))
                    else:
                        modules = config.get("modules_81", config.get("modules", []))

                    if isinstance(modules, list) and len(modules) > 0:
                        # Extract just the values if modules are objects
                        module_values = []
                        for mod in modules:
                            if isinstance(mod, dict):
                                module_values.append(mod.get("value", mod))
                            else:
                                module_values.append(mod)
                        env["GATEWAY_MODULES_ENABLED"] = ",".join(module_values)

                    # Handle third party modules
                    third_party_modules = config.get("third_party_modules", "")
                    if third_party_modules and third_party_modules.strip():
                        # Split by newlines and filter empty lines
                        module_urls = [
                            url.strip()
                            for url in third_party_modules.split("\n")
                            if url.strip()
                        ]
                        if module_urls:
                            env["GATEWAY_MODULE_RELINK"] = ";".join(module_urls)

                    env["IGNITION_MEMORY_MAX"] = config.get(
                        "memory_max", env.get("IGNITION_MEMORY_MAX", "2048m")
                    )
                    env["IGNITION_MEMORY_INIT"] = config.get(
                        "memory_init", env.get("IGNITION_MEMORY_INIT", "512m")
                    )

                    # Handle commissioning options - only set if explicitly true
                    if config.get("commissioning_allow_non_secure", False):
                        env["GATEWAY_SYSTEM_COMMISSIONING_ALLOWINSECURE"] = "true"

                    # REMOVED: IGNITION_QUICKSTART causes volume mount issues
                    # Users should manually commission the gateway after first start

                    # Apply email integration if available (for alarm notifications)
                    if has_email_testing and integration_settings.email.get(
                        "auto_configure_services", True
                    ):
                        email_int = integration_results["integrations"]["email_testing"]
                        mailhog_instance = email_int.get("provider", "mailhog")
                        from_address = integration_settings.email.get(
                            "from_address", "noreply@iiot.local"
                        )
                        email_env_vars = generate_email_env_vars(
                            "ignition", mailhog_instance, from_address
                        )
                        env.update(email_env_vars)

                elif instance.app_id == "keycloak":
                    env["KEYCLOAK_ADMIN"] = config.get(
                        "admin_username", env.get("KEYCLOAK_ADMIN")
                    )
                    env["KEYCLOAK_ADMIN_PASSWORD"] = config.get(
                        "admin_password", env.get("KEYCLOAK_ADMIN_PASSWORD")
                    )

                    # Apply email integration if available (for user emails)
                    if has_email_testing and integration_settings.email.get(
                        "auto_configure_services", True
                    ):
                        email_int = integration_results["integrations"]["email_testing"]
                        mailhog_instance = email_int.get("provider", "mailhog")
                        from_address = integration_settings.email.get(
                            "from_address", "noreply@iiot.local"
                        )
                        email_env_vars = generate_email_env_vars(
                            "keycloak", mailhog_instance, from_address
                        )
                        env.update(email_env_vars)

                elif instance.app_id == "grafana":
                    env["GF_SECURITY_ADMIN_USER"] = config.get(
                        "admin_username", env.get("GF_SECURITY_ADMIN_USER")
                    )
                    env["GF_SECURITY_ADMIN_PASSWORD"] = config.get(
                        "admin_password", env.get("GF_SECURITY_ADMIN_PASSWORD")
                    )

                    # Apply OAuth integration if available
                    if has_oauth_provider and integration_settings.oauth.get(
                        "auto_configure_services", True
                    ):
                        oauth_int = integration_results["integrations"][
                            "oauth_provider"
                        ]
                        for client in oauth_int.get("clients", []):
                            if (
                                client["service_id"] == "grafana"
                                and client["instance_name"] == instance.instance_name
                            ):
                                provider = client["provider"]
                                realm_name = integration_settings.oauth.get(
                                    "realm_name", "iiot"
                                )

                                # Get client secret from generated Keycloak realm
                                client_secret = None
                                if keycloak_clients:
                                    kc_client = next(
                                        (
                                            kc
                                            for kc in keycloak_clients
                                            if kc.get("clientId") == "grafana"
                                        ),
                                        None,
                                    )
                                    if kc_client:
                                        client_secret = kc_client.get("secret")

                                oauth_env_vars = generate_oauth_env_vars(
                                    "grafana",
                                    provider,
                                    realm_name,
                                    client_secret=client_secret,
                                )
                                env.update(oauth_env_vars)

                    # Apply email integration if available
                    if has_email_testing and integration_settings.email.get(
                        "auto_configure_services", True
                    ):
                        email_int = integration_results["integrations"]["email_testing"]
                        mailhog_instance = email_int.get("provider", "mailhog")
                        from_address = integration_settings.email.get(
                            "from_address", "noreply@iiot.local"
                        )
                        email_env_vars = generate_email_env_vars(
                            "grafana", mailhog_instance, from_address
                        )
                        env.update(email_env_vars)

                elif instance.app_id == "n8n":
                    env["N8N_BASIC_AUTH_USER"] = config.get(
                        "username", env.get("N8N_BASIC_AUTH_USER")
                    )
                    env["N8N_BASIC_AUTH_PASSWORD"] = config.get(
                        "password", env.get("N8N_BASIC_AUTH_PASSWORD")
                    )

                    # Apply OAuth integration if available
                    if has_oauth_provider and integration_settings.oauth.get(
                        "auto_configure_services", True
                    ):
                        oauth_int = integration_results["integrations"][
                            "oauth_provider"
                        ]
                        for client in oauth_int.get("clients", []):
                            if (
                                client["service_id"] == "n8n"
                                and client["instance_name"] == instance.instance_name
                            ):
                                provider = client["provider"]
                                realm_name = integration_settings.oauth.get(
                                    "realm_name", "iiot"
                                )

                                # Get client secret from generated Keycloak realm
                                client_secret = None
                                if keycloak_clients:
                                    kc_client = next(
                                        (
                                            kc
                                            for kc in keycloak_clients
                                            if kc.get("clientId") == "n8n"
                                        ),
                                        None,
                                    )
                                    if kc_client:
                                        client_secret = kc_client.get("secret")

                                oauth_env_vars = generate_oauth_env_vars(
                                    "n8n",
                                    provider,
                                    realm_name,
                                    client_secret=client_secret,
                                )
                                env.update(oauth_env_vars)

                    # Apply email integration if available
                    if has_email_testing and integration_settings.email.get(
                        "auto_configure_services", True
                    ):
                        email_int = integration_results["integrations"]["email_testing"]
                        mailhog_instance = email_int.get("provider", "mailhog")
                        from_address = integration_settings.email.get(
                            "from_address", "noreply@iiot.local"
                        )
                        email_env_vars = generate_email_env_vars(
                            "n8n", mailhog_instance, from_address
                        )
                        env.update(email_env_vars)

                elif instance.app_id == "rabbitmq":
                    env["RABBITMQ_DEFAULT_USER"] = config.get(
                        "username", env.get("RABBITMQ_DEFAULT_USER")
                    )
                    env["RABBITMQ_DEFAULT_PASS"] = config.get(
                        "password", env.get("RABBITMQ_DEFAULT_PASS")
                    )

                elif instance.app_id == "vault":
                    env["VAULT_DEV_ROOT_TOKEN_ID"] = config.get(
                        "root_token", env.get("VAULT_DEV_ROOT_TOKEN_ID")
                    )

                elif instance.app_id == "pgadmin":
                    env["PGADMIN_DEFAULT_EMAIL"] = config.get(
                        "email", env.get("PGADMIN_DEFAULT_EMAIL")
                    )
                    env["PGADMIN_DEFAULT_PASSWORD"] = config.get(
                        "password", env.get("PGADMIN_DEFAULT_PASSWORD")
                    )

                elif instance.app_id == "phpmyadmin":
                    # PMA_HOST should point to the mariadb instance
                    mariadb_instance = next(
                        (
                            inst
                            for inst in stack_config.instances
                            if inst.app_id == "mariadb"
                        ),
                        None,
                    )
                    if mariadb_instance:
                        env["PMA_HOST"] = mariadb_instance.instance_name
                        env["PMA_PORT"] = str(mariadb_instance.config.get("port", 3306))

                service["environment"] = env

            # Handle volumes
            if "volumes" in app["default_config"]:
                volumes = []
                for vol in app["default_config"]["volumes"]:
                    # Replace {instance_name} placeholder
                    vol = vol.replace("{instance_name}", service_name)
                    volumes.append(vol)

                # Add Keycloak import volume if realm import is configured
                if instance.app_id == "keycloak" and keycloak_clients:
                    volumes.append(
                        f"./configs/{service_name}/import:/opt/keycloak/data/import:ro"
                    )

                service["volumes"] = volumes

            # Handle command
            if "command" in app["default_config"]:
                service["command"] = app["default_config"]["command"]

                # Modify Keycloak command to include import flag
                if instance.app_id == "keycloak" and keycloak_clients:
                    realm_name = integration_settings.oauth.get("realm_name", "iiot")
                    service["command"] = f"start-dev --import-realm"

            # Handle cap_add (for services like Vault)
            if "cap_add" in app["default_config"]:
                service["cap_add"] = app["default_config"]["cap_add"]

            # Add Traefik labels if Traefik is present and this is a web-accessible service
            if has_traefik and instance.app_id != "traefik":
                # Define web services and their default ports
                web_service_ports = {
                    "ignition": lambda c: str(c.get("http_port", 8088)),
                    "grafana": lambda c: str(c.get("port", 3000)),
                    "nodered": lambda c: str(c.get("port", 1880)),
                    "n8n": lambda c: str(c.get("port", 5678)),
                    "keycloak": lambda c: str(c.get("port", 8180)),
                    "prometheus": lambda c: "9090",
                    "dozzle": lambda c: "8080",
                    "portainer": lambda c: "9000",
                    "guacamole": lambda c: "8080",
                    "authentik": lambda c: "9000",
                    "authelia": lambda c: "9091",
                    "mailhog": lambda c: "8025",
                    "influxdb": lambda c: "8086",
                    "chronograf": lambda c: "8888",
                }

                if instance.app_id in web_service_ports:
                    # Create subdomain from service name
                    subdomain = (
                        service_name.split("-")[0]
                        if "-" in service_name
                        else service_name
                    )

                    # Get the port using the port function
                    port = web_service_ports[instance.app_id](config)

                    # Get domain from integration settings
                    base_domain = integration_settings.reverse_proxy.get(
                        "base_domain", "localhost"
                    )
                    enable_https = integration_settings.reverse_proxy.get(
                        "enable_https", False
                    )
                    entrypoint = "websecure" if enable_https else "web"

                    service["labels"] = [
                        "traefik.enable=true",
                        f"traefik.http.routers.{service_name}.rule=Host(`{subdomain}.{base_domain}`)",
                        f"traefik.http.routers.{service_name}.entrypoints={entrypoint}",
                        f"traefik.http.services.{service_name}.loadbalancer.server.port={port}",
                    ]

                    # Add TLS if HTTPS is enabled
                    if enable_https:
                        service["labels"].append(
                            f"traefik.http.routers.{service_name}.tls=true"
                        )
                        service["labels"].append(
                            f"traefik.http.routers.{service_name}.tls.certresolver=letsencrypt"
                        )

            compose["services"][service_name] = service

            # Add to env file
            env_vars.append(f"# {service_name}")
            env_vars.append(
                f"{service_name.upper().replace('-', '_')}_VERSION={version}"
            )
            if "environment" in service:
                for key, value in service["environment"].items():
                    env_vars.append(
                        f"{service_name.upper().replace('-', '_')}_{key}={value}"
                    )
            env_vars.append("")

        # Collect named volumes from all services
        # Named volumes are those that don't start with ./ or / (not bind mounts)
        named_volumes = set()
        for service_name, service in compose["services"].items():
            if "volumes" in service:
                for vol in service["volumes"]:
                    # Check if this is a named volume (not a bind mount)
                    if ":" in vol:
                        volume_part = vol.split(":")[0]
                        # Named volumes don't start with ./ or /
                        if not volume_part.startswith(
                            "./"
                        ) and not volume_part.startswith("/"):
                            named_volumes.add(volume_part)

        # Add named volumes to compose structure
        if named_volumes:
            for vol_name in sorted(named_volumes):
                compose["volumes"][vol_name] = None

        # Generate integration configuration files
        # 1. MQTT Broker Configuration
        if has_mqtt_broker:
            mqtt_int = integration_results["integrations"]["mqtt_broker"]
            for provider_info in mqtt_int.get("providers", []):
                provider_id = provider_info["service_id"]
                instance_name = provider_info["instance_name"]

                if provider_id == "mosquitto":
                    # Generate Mosquitto configuration
                    mqtt_username = integration_settings.mqtt.get("username", "")
                    mqtt_password = integration_settings.mqtt.get("password", "")
                    mqtt_enable_tls = integration_settings.mqtt.get("enable_tls", False)
                    mqtt_tls_port = integration_settings.mqtt.get("tls_port", 8883)

                    config_files[f"configs/{instance_name}/mosquitto.conf"] = (
                        generate_mosquitto_config(
                            username=mqtt_username,
                            password=mqtt_password,
                            enable_tls=mqtt_enable_tls,
                            tls_port=mqtt_tls_port,
                        )
                    )

                    if mqtt_username and mqtt_password:
                        config_files[f"configs/{instance_name}/passwd"] = (
                            generate_mosquitto_password_file(
                                mqtt_username, mqtt_password
                            )
                        )

        # Generate Prometheus config files for all Prometheus instances
        for instance in stack_config.instances:
            if instance.app_id == "prometheus":
                config_files[f"configs/{instance.instance_name}/prometheus.yml"] = (
                    generate_prometheus_config()
                )

        # 2. Grafana Datasource Provisioning
        if "visualization" in integration_results.get("integrations", {}):
            viz_int = integration_results["integrations"]["visualization"]
            grafana_instance = viz_int.get("provider")

            if grafana_instance:
                datasources_config = []

                for ds in viz_int.get("datasources", []):
                    ds_type = ds["service_id"]
                    ds_instance_name = ds["instance_name"]
                    ds_config = ds["config"]

                    datasources_config.append(
                        {
                            "type": ds_type,
                            "instance_name": ds_instance_name,
                            "config": ds_config,
                        }
                    )

                if datasources_config:
                    config_files[
                        f"configs/{grafana_instance}/provisioning/datasources/auto.yaml"
                    ] = generate_grafana_datasources(datasources_config)

        # 3. Keycloak Realm Configuration - Save to file
        if keycloak_realm_config:
            # Use the pre-generated realm config (ensures secrets match)
            realm_name = integration_settings.oauth.get("realm_name", "iiot")
            realm_json = json.dumps(keycloak_realm_config, indent=2)
            config_files[f"configs/keycloak/import/realm-{realm_name}.json"] = (
                realm_json
            )

        # Convert to YAML
        compose_yaml = yaml.dump(compose, default_flow_style=False, sort_keys=False)

        # Create .env file
        env_content = "\n".join(env_vars)

        # Create README
        has_ignition_service = any(
            inst.app_id == "ignition" for inst in stack_config.instances
        )

        startup_instructions = """4. Start the stack:
   ```bash
   docker compose up -d
   ```"""

        if has_ignition_service:
            startup_instructions = """4. Start the stack using the initialization script:

   **Linux/Mac:**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

   **Windows:**
   ```cmd
   start.bat
   ```

   The script automatically handles Ignition volume initialization on first run.

   **Note:** For Ignition stacks, use `start.sh`/`start.bat` instead of `docker compose up -d` directly.
   This ensures data volumes are properly initialized on first startup."""

        # Generate list of required directories for config files (bind mounts only)
        # Named volumes are automatically managed by Docker, no directory creation needed
        required_dirs = set()
        for instance in stack_config.instances:
            app = catalog_dict.get(instance.app_id)
            if app and "volumes" in app["default_config"]:
                for vol in app["default_config"]["volumes"]:
                    if ":" in vol and vol.startswith("./"):
                        # Extract local path from volume mapping (e.g., "./configs/traefik/traefik.yml:/etc/traefik/traefik.yml")
                        local_path = vol.split(":")[0]
                        # Replace {instance_name} placeholder
                        local_path = local_path.replace(
                            "{instance_name}", instance.instance_name
                        )

                        # Only add parent directory of config files, not data directories
                        # For config files, we need to ensure the parent directory exists
                        if "/" in local_path:
                            parent_dir = "/".join(local_path.split("/")[:-1])
                            if parent_dir:  # Ensure it's not empty
                                required_dirs.add(parent_dir)

        # Generate directory creation commands
        dir_creation_cmds = (
            "\n   ".join([f"mkdir -p {d}" for d in sorted(required_dirs)])
            if required_dirs
            else "   # No directories required - using Docker named volumes"
        )

        readme_content = f"""# {global_settings.stack_name} - Generated Configuration

## Global Settings
- **Stack Name**: {global_settings.stack_name}
- **Timezone**: {global_settings.timezone}
- **Restart Policy**: {global_settings.restart_policy}

## Services Included
{chr(10).join([f"- {instance.instance_name} ({instance.app_id}) - {instance.config.get('version', 'latest')}" for instance in stack_config.instances])}

## Getting Started

1. Review the generated `docker-compose.yml` and `.env` files
2. Customise any settings as needed
3. Create required directories:
   ```bash
   {dir_creation_cmds}
   ```
{startup_instructions}

## Service URLs
"""

        for instance in stack_config.instances:
            app = catalog_dict.get(instance.app_id)
            if app and "ports" in app["default_config"]:
                config = instance.config
                url = ""

                if instance.app_id == "ignition":
                    port = config.get("http_port", 8088)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "postgres":
                    port = config.get("port", 5432)
                    url = f"localhost:{port}"
                elif instance.app_id == "mariadb":
                    port = config.get("port", 3306)
                    url = f"localhost:{port}"
                elif instance.app_id == "mssql":
                    port = config.get("port", 1433)
                    url = f"localhost:{port}"
                elif instance.app_id == "keycloak":
                    port = config.get("port", 8180)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "traefik":
                    port = config.get("dashboard_port", 8080)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "grafana":
                    port = config.get("port", 3000)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "prometheus":
                    port = config.get("port", 9090)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "dozzle":
                    port = config.get("port", 8888)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "nodered":
                    port = config.get("port", 1880)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "n8n":
                    port = config.get("port", 5678)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "emqx":
                    port = config.get("dashboard_port", 18083)
                    url = f"http://localhost:{port} (Dashboard)"
                elif instance.app_id == "mosquitto":
                    port = config.get("mqtt_port", 1883)
                    url = f"mqtt://localhost:{port}"
                elif instance.app_id == "rabbitmq":
                    port = config.get("management_port", 15672)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "portainer":
                    port = config.get("https_port", 9443)
                    url = f"https://localhost:{port}"
                elif instance.app_id == "whatupdocker":
                    port = config.get("port", 3001)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "vault":
                    port = config.get("port", 8200)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "guacamole":
                    port = config.get("port", 8080)
                    url = f"http://localhost:{port}/guacamole"
                elif instance.app_id == "authentik":
                    port = config.get("http_port", 9000)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "authelia":
                    port = config.get("port", 9091)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "mailhog":
                    port = config.get("http_port", 8025)
                    url = f"http://localhost:{port} (SMTP: {config.get('smtp_port', 1025)})"
                elif instance.app_id == "pgadmin":
                    port = config.get("port", 5050)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "phpmyadmin":
                    port = config.get("port", 8080)
                    url = f"http://localhost:{port}"
                elif instance.app_id == "nginx-proxy-manager":
                    admin_port = config.get("admin_port", 81)
                    url = f"http://localhost:{admin_port} (Admin UI)"
                else:
                    port = config.get("port", config.get("http_port", "8080"))
                    url = f"http://localhost:{port}"

                readme_content += f"- **{instance.instance_name}**: {url}\n"

        # Add PostgreSQL connection instructions if applicable
        postgres_in_stack = any(
            inst.app_id == "postgres" for inst in stack_config.instances
        )
        ignition_in_stack = any(
            inst.app_id == "ignition" for inst in stack_config.instances
        )

        if postgres_in_stack and ignition_in_stack:
            for inst in stack_config.instances:
                if inst.app_id == "postgres":
                    db_config = inst.config
                    db_host = inst.instance_name
                    db_port = db_config.get("port", 5432)
                    db_name = db_config.get("database", "ignition")
                    db_user = db_config.get("username", "ignition")
                    db_pass = db_config.get("password", "password")

                    readme_content += f"""
## PostgreSQL Database Connection

To connect Ignition to PostgreSQL:

1. Open Ignition Gateway: http://localhost:8088
2. Navigate to **Config → Databases → Connections**
3. Click **"Create new Database Connection"**
4. Enter these details:
   - **Name**: PostgreSQL
   - **Connect URL**: `jdbc:postgresql://{db_host}:{db_port}/{db_name}`
   - **Username**: `{db_user}`
   - **Password**: `{db_pass}`
   - **Status Query**: `SELECT 1`
   - **Max Connections**: 8
5. Click **"Create New Database Connection"**
6. Test the connection

**Credentials Summary:**
- Host: `{db_host}`
- Port: `{db_port}`
- Database: `{db_name}`
- Username: `{db_user}`
- Password: `{db_pass}`

*See `configs/ignition-gateway/postgres_connection_info.txt` for detailed instructions.*
"""
                    break

        # Add Keycloak SSO section if configured
        if keycloak_clients:
            realm_name = integration_settings.oauth.get("realm_name", "iiot")
            readme_content += generate_keycloak_readme_section(
                realm_name, keycloak_clients
            )

        # Add Ignition database auto-registration section if applicable
        ignition_db_list = []
        if "db_provider" in integration_results.get("integrations", {}):
            db_int = integration_results["integrations"]["db_provider"]

            # Find Ignition instances that will use databases
            for client in db_int.get("clients", []):
                if client["service_id"] == "ignition" and client.get("auto_register"):
                    # Get compatible databases for this Ignition instance
                    for provider in client.get("matched_providers", []):
                        ignition_db_list.append(
                            {
                                "type": provider["service_id"],
                                "instance_name": provider["instance_name"],
                                "config": provider["config"],
                            }
                        )

        if ignition_db_list:
            readme_content += generate_ignition_db_readme_section(ignition_db_list)

        # Add ntfy monitoring section if enabled
        if global_settings.ntfy_enabled and global_settings.ntfy_topic:
            readme_content += generate_ntfy_readme_section(
                global_settings.ntfy_server, global_settings.ntfy_topic
            )

        readme_content += """
## Stopping the Stack

```bash
docker compose down
```

To remove volumes as well:
```bash
docker compose down -v
```

## Generated by IIoT Stack Builder
"""

        return {
            "docker_compose": compose_yaml,
            "env": env_content,
            "readme": readme_content,
            "config_files": config_files,
            "ntfy_enabled": global_settings.ntfy_enabled,
            "ntfy_server": global_settings.ntfy_server,
            "ntfy_topic": global_settings.ntfy_topic,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/download")
def download_stack(stack_config: StackConfig):
    """Download complete stack as ZIP file"""
    try:
        generated = generate_stack(stack_config)

        # Check if Traefik is in the stack
        has_traefik = any(inst.app_id == "traefik" for inst in stack_config.instances)

        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("docker-compose.yml", generated["docker_compose"])
            zip_file.writestr(".env", generated["env"])
            zip_file.writestr("README.md", generated["readme"])

            # Add generated config files from integrations
            for file_path, content in generated.get("config_files", {}).items():
                # Create ZipInfo with proper permissions (0o644 = rw-r--r--)
                info = zipfile.ZipInfo(file_path)
                info.external_attr = 0o644 << 16  # Set file permissions
                zip_file.writestr(info, content)

            # Create directory structure placeholders
            zip_file.writestr("configs/.gitkeep", "")
            zip_file.writestr("scripts/.gitkeep", "")

            # Add ntfy monitoring script if enabled
            global_settings = stack_config.global_settings or GlobalSettings()
            if global_settings.ntfy_enabled and global_settings.ntfy_topic:
                monitor_script = generate_ntfy_monitor_script(
                    ntfy_server=global_settings.ntfy_server,
                    ntfy_topic=global_settings.ntfy_topic,
                    stack_name=global_settings.stack_name,
                )
                zip_file.writestr("monitor.sh", monitor_script)

            # Generate Ignition database auto-registration script if applicable
            has_ignition = any(
                inst.app_id == "ignition" for inst in stack_config.instances
            )
            has_databases = any(
                inst.app_id in ["postgres", "mariadb", "mssql"]
                for inst in stack_config.instances
            )

            if has_ignition and has_databases:
                # Detect integrations to find database connections
                instances_for_detection = [
                    {
                        "app_id": inst.app_id,
                        "instance_name": inst.instance_name,
                        "config": inst.config,
                    }
                    for inst in stack_config.instances
                ]
                engine = get_integration_engine()
                detection = engine.detect_integrations(instances_for_detection)

                if "db_provider" in detection.get("integrations", {}):
                    db_int = detection["integrations"]["db_provider"]

                    # Find databases that should be auto-registered with Ignition
                    ignition_dbs = []
                    for client in db_int.get("clients", []):
                        if client["service_id"] == "ignition":
                            for provider in client.get("matched_providers", []):
                                ignition_dbs.append(
                                    {
                                        "type": provider["service_id"],
                                        "instance_name": provider["instance_name"],
                                        "config": provider["config"],
                                    }
                                )

                    if ignition_dbs:
                        # Get Ignition admin credentials
                        ignition_inst = next(
                            (
                                inst
                                for inst in stack_config.instances
                                if inst.app_id == "ignition"
                            ),
                            None,
                        )
                        if ignition_inst:
                            ignition_host = ignition_inst.instance_name
                            ignition_port = ignition_inst.config.get("http_port", 8088)
                            admin_username = ignition_inst.config.get(
                                "admin_username", "admin"
                            )
                            admin_password = ignition_inst.config.get(
                                "admin_password", "password"
                            )

                            # Generate the registration script
                            db_registration_script = (
                                generate_ignition_db_registration_script(
                                    ignition_host=ignition_host,
                                    ignition_port=ignition_port,
                                    admin_username=admin_username,
                                    admin_password=admin_password,
                                    databases=ignition_dbs,
                                )
                            )

                            zip_file.writestr(
                                "scripts/register_databases.py", db_registration_script
                            )
                            zip_file.writestr(
                                "scripts/requirements.txt", generate_requirements_file()
                            )

            # Generate Ignition initialization script if Ignition is present
            has_postgres = any(
                inst.app_id == "postgres" for inst in stack_config.instances
            )

            if has_ignition:
                # Load catalog for volume path extraction
                catalog = load_catalog()
                catalog_dict_download = {
                    app["id"]: app for app in catalog["applications"]
                }

                ignition_instances = [
                    inst for inst in stack_config.instances if inst.app_id == "ignition"
                ]

                # Get Ignition and PostgreSQL configs for database auto-configuration
                ignition_config = None
                postgres_config = None
                for inst in stack_config.instances:
                    if inst.app_id == "ignition":
                        ignition_config = inst
                    elif inst.app_id == "postgres":
                        postgres_config = inst

                init_script = """#!/bin/bash
# Ignition Volume Initialization Script
# This script handles the two-phase startup for Ignition to properly initialize volumes

set -e

echo "🚀 Ignition Stack Initialization Script"
echo "========================================"

# Create required directories for config files (if any)
# Note: Data directories are managed as Docker named volumes
echo ""
echo "📁 Creating config directories..."
"""
                # Add directory creation only for config file bind mounts (not data directories)
                config_dirs = set()
                for instance in stack_config.instances:
                    app = catalog_dict_download.get(instance.app_id)
                    if app and "volumes" in app["default_config"]:
                        for vol in app["default_config"]["volumes"]:
                            if ":" in vol and vol.startswith("./"):
                                local_path = vol.split(":")[0]
                                local_path = local_path.replace(
                                    "{instance_name}", instance.instance_name
                                )
                                # Only add parent directory of config files
                                if "/" in local_path:
                                    parent_dir = "/".join(local_path.split("/")[:-1])
                                    if parent_dir:
                                        config_dirs.add(parent_dir)

                if config_dirs:
                    for config_dir in sorted(config_dirs):
                        init_script += f"""mkdir -p {config_dir}
"""
                else:
                    init_script += """# No config directories required
"""

                init_script += """
echo "✅ Config directories ready"

# With named volumes, Ignition can start normally without two-phase initialization
# Docker manages the named volumes automatically
echo ""
echo "🚀 Starting all services..."
echo "============================"
"""

                init_script += """
    docker compose up -d

    echo ""
    echo "⏳ Waiting for services to start..."
    sleep 10

    # Wait for Ignition to be healthy (if present)
    WAIT_TIME=0
    MAX_WAIT=90

    while [ $WAIT_TIME -lt $MAX_WAIT ]; do
"""

                for inst in ignition_instances:
                    service_name = inst.instance_name
                    container_name = f"{global_settings.stack_name}-{service_name}"
                    init_script += f"""        HEALTH=$(docker inspect --format='{{{{.State.Health.Status}}}}' {container_name} 2>/dev/null || echo "starting")
        if [ "$HEALTH" = "healthy" ]; then
            echo "✅ {service_name} is healthy!"
            break
        fi
"""

                init_script += """
        echo "   Status: $HEALTH - waiting... (${WAIT_TIME}s/${MAX_WAIT}s)"
        sleep 10
        WAIT_TIME=$((WAIT_TIME + 10))
    done

    if [ $WAIT_TIME -ge $MAX_WAIT ]; then
        echo "⚠️  Warning: Service health check timed out, but services are running"
    fi
"""

                # If PostgreSQL is present, create connection instructions
                if has_postgres and ignition_config and postgres_config:
                    db_name = postgres_config.config.get("database", "ignition")
                    db_user = postgres_config.config.get("username", "ignition")
                    db_pass = postgres_config.config.get("password", "password")
                    db_host = postgres_config.instance_name
                    db_port = postgres_config.config.get("port", 5432)

                    # Create config directory for Ignition
                    init_script += f"""
# Create PostgreSQL connection instructions
mkdir -p "./configs/{ignition_config.instance_name}"
cat > "./configs/{ignition_config.instance_name}/postgres_connection_info.txt" <<'DBINFO'
PostgreSQL Database Connection Information
==========================================

To add the PostgreSQL datasource in Ignition Gateway:

1. Open Ignition Gateway at http://localhost:{ignition_config.config.get("http_port", 8088)}
2. Go to Config → Databases → Connections
3. Click "Create new Database Connection"
4. Enter the following details:

   Name: PostgreSQL
   Connect URL: jdbc:postgresql://{db_host}:{db_port}/{db_name}
   Username: {db_user}
   Password: {db_pass}
   Status Query: SELECT 1
   Max Connections: 8

5. Click "Create New Database Connection"
6. Test the connection to verify it works

Database Credentials:
- Host: {db_host}
- Port: {db_port}
- Database: {db_name}
- Username: {db_user}
- Password: {db_pass}
DBINFO
echo "   📄 PostgreSQL connection info saved to configs/{ignition_config.instance_name}/postgres_connection_info.txt"
"""

                init_script += """

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📊 Waiting for services to be fully ready..."
sleep 10

echo ""
echo "🎉 Stack is ready!"
echo ""
echo "📋 Service URLs:"
"""

                # Add service URLs
                for instance in stack_config.instances:
                    if instance.app_id == "ignition":
                        http_port = instance.config.get("http_port", 8088)
                        if has_traefik:
                            subdomain = (
                                instance.instance_name.split("-")[0]
                                if "-" in instance.instance_name
                                else instance.instance_name
                            )
                            init_script += f"""echo "   🔧 {instance.instance_name}: http://{subdomain}.localhost (via Traefik) or http://localhost:{http_port}"
"""
                        else:
                            init_script += f"""echo "   🔧 {instance.instance_name}: http://localhost:{http_port}"
"""

                if has_traefik:
                    init_script += """echo "   🌐 Traefik Dashboard: http://localhost:8080"
"""

                init_script += """
echo ""
echo "💡 To stop the stack: docker compose down"
echo "💡 To view logs: docker compose logs -f"
echo ""
"""

                zip_file.writestr("start.sh", init_script)

                # Also create a Windows batch file version
                win_script = f"""@echo off
REM Ignition Volume Initialization Script for Windows
REM This script handles the two-phase startup for Ignition to properly initialize volumes

echo Ignition Stack Initialization Script
echo ========================================
echo.

REM For Windows, we'll use a simpler approach - just start normally
REM Users can manually do two-phase if needed

echo Starting stack...
docker compose up -d

echo.
echo Stack is starting...
echo.
echo Service URLs:
"""

                for instance in stack_config.instances:
                    if instance.app_id == "ignition":
                        http_port = instance.config.get("http_port", 8088)
                        if has_traefik:
                            subdomain = (
                                instance.instance_name.split("-")[0]
                                if "-" in instance.instance_name
                                else instance.instance_name
                            )
                            win_script += f"""echo    {instance.instance_name}: http://{subdomain}.localhost or http://localhost:{http_port}
"""
                        else:
                            win_script += f"""echo    {instance.instance_name}: http://localhost:{http_port}
"""

                if has_traefik:
                    win_script += """echo    Traefik Dashboard: http://localhost:8080
"""

                win_script += """
echo.
echo To stop: docker compose down
echo To view logs: docker compose logs -f
echo.
pause
"""

                zip_file.writestr("start.bat", win_script)

            # Generate Traefik configuration files if Traefik is present
            if has_traefik:
                # Get integration settings for Traefik
                integration_settings = (
                    stack_config.integration_settings or IntegrationSettings()
                )
                enable_https = integration_settings.reverse_proxy.get(
                    "enable_https", False
                )
                letsencrypt_email = integration_settings.reverse_proxy.get(
                    "letsencrypt_email", ""
                )

                # Main Traefik configuration using config generator
                traefik_config = generate_traefik_static_config(
                    enable_https=enable_https, letsencrypt_email=letsencrypt_email
                )
                zip_file.writestr("configs/traefik/traefik.yml", traefik_config)

                # Define web services and their ports (must match the docker compose generation)
                web_service_ports = {
                    "ignition": lambda c: str(c.get("http_port", 8088)),
                    "grafana": lambda c: str(c.get("port", 3000)),
                    "nodered": lambda c: str(c.get("port", 1880)),
                    "n8n": lambda c: str(c.get("port", 5678)),
                    "keycloak": lambda c: str(c.get("port", 8180)),
                    "prometheus": lambda c: "9090",
                    "dozzle": lambda c: "8080",
                    "portainer": lambda c: "9000",
                    "guacamole": lambda c: "8080",
                    "authentik": lambda c: "9000",
                    "authelia": lambda c: "9091",
                    "mailhog": lambda c: "8025",
                    "influxdb": lambda c: "8086",
                    "chronograf": lambda c: "8888",
                }

                # Generate dynamic routing for each web service
                services_for_traefik = []
                for instance in stack_config.instances:
                    if (
                        instance.app_id != "traefik"
                        and instance.app_id in web_service_ports
                    ):
                        service_name = instance.instance_name
                        config = instance.config

                        # Create subdomain from service name
                        subdomain = (
                            service_name.split("-")[0]
                            if "-" in service_name
                            else service_name
                        )

                        # Get the port using the port function
                        port = int(web_service_ports[instance.app_id](config))

                        services_for_traefik.append(
                            {
                                "instance_name": service_name,
                                "subdomain": subdomain,
                                "port": port,
                            }
                        )

                # Generate dynamic config using config generator
                base_domain = integration_settings.reverse_proxy.get(
                    "base_domain", "localhost"
                )
                dynamic_config = generate_traefik_dynamic_config(
                    services=services_for_traefik,
                    domain=base_domain,
                    enable_https=enable_https,
                )
                zip_file.writestr(
                    "configs/traefik/dynamic/services.yml", dynamic_config
                )

            # Add uploaded module files for Ignition instances
            for instance in stack_config.instances:
                if instance.app_id == "ignition":
                    uploaded_modules = instance.config.get("uploaded_modules", [])
                    if uploaded_modules:
                        for module in uploaded_modules:
                            # Decode base64 module file and add to zip
                            filename = module.get("filename", "module.modl")
                            encoded_content = module.get("encoded", "")
                            if encoded_content:
                                try:
                                    content = base64.b64decode(encoded_content)
                                    zip_file.writestr(
                                        f"modules/{instance.instance_name}/{filename}",
                                        content,
                                    )
                                except Exception as e:
                                    logger.error(
                                        f"Error decoding module {filename}: {e}"
                                    )

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{global_settings.stack_name}.zip"'
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/docker-installer/linux")
def download_linux_installer():
    """Download Linux Docker installation script"""
    try:
        script_path = "/scripts/install-docker-linux.sh"
        with open(script_path, "r") as f:
            script_content = f.read()

        return StreamingResponse(
            io.BytesIO(script_content.encode("utf-8")),
            media_type="text/x-shellscript",
            headers={
                "Content-Disposition": "attachment; filename=install-docker-linux.sh"
            },
        )
    except Exception as e:
        logger.error(f"Error downloading Linux installer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/docker-installer/windows")
def download_windows_installer():
    """Download Windows Docker installation script"""
    try:
        script_path = "/scripts/install-docker-windows.ps1"
        with open(script_path, "r") as f:
            script_content = f.read()

        return StreamingResponse(
            io.BytesIO(script_content.encode("utf-8")),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; filename=install-docker-windows.ps1"
            },
        )
    except Exception as e:
        logger.error(f"Error downloading Windows installer: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-offline-bundle")
def generate_offline_bundle(stack_config: StackConfig):
    """Generate offline bundle with all Docker images and configurations"""
    try:
        # Generate the stack first
        generated = generate_stack(stack_config)

        # Get global settings for stack name
        global_settings = stack_config.global_settings or GlobalSettings()

        # Create a shell script to pull and save all Docker images
        catalog = load_catalog()
        catalog_dict = {app["id"]: app for app in catalog["applications"]}

        images_to_pull = []
        for instance in stack_config.instances:
            app = catalog_dict.get(instance.app_id)
            if not app or not app.get("enabled", False):
                continue

            version = instance.config.get(
                "version", app.get("default_version", "latest")
            )
            image = f"{app['image']}:{version}"
            images_to_pull.append(image)

        # Generate pull and save script
        pull_script = """#!/bin/bash
# Offline Bundle Image Pull and Save Script
# This script pulls all required Docker images and saves them to a tar file
# for offline/airgapped installation

set -e

echo "🚀 Offline Bundle Generator"
echo "============================"
echo ""
echo "This script will:"
echo "  1. Pull all required Docker images"
echo "  2. Save images to docker-images.tar"
echo "  3. Create a complete offline bundle"
echo ""

# Colors
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

"""

        for image in images_to_pull:
            pull_script += f"""echo -e "${{GREEN}}[INFO]${{NC}} Pulling {image}..."
docker pull {image}

"""

        pull_script += f"""
echo ""
echo -e "${{GREEN}}[INFO]${{NC}} Saving all images to docker-images.tar..."
docker save -o docker-images.tar {' '.join(images_to_pull)}

echo ""
echo -e "${{GREEN}}[INFO]${{NC}} Compressing images..."
gzip docker-images.tar

echo ""
echo "✅ Offline bundle created successfully!"
echo ""
echo "📦 Bundle contents:"
echo "   - docker-images.tar.gz (all Docker images)"
echo "   - docker-compose.yml"
echo "   - .env"
echo "   - All configuration files"
echo ""
echo "📋 To use on offline system:"
echo "   1. Transfer all files to the offline system"
echo "   2. Load images: gunzip -c docker-images.tar.gz | docker load"
echo "   3. Run: docker compose up -d"
echo ""
"""

        # Create load script for offline system
        load_script = """#!/bin/bash
# Offline Bundle Load Script
# Run this on the airgapped/offline system to load Docker images

set -e

echo "🚀 Loading Docker images from offline bundle..."
echo "==============================================="
echo ""

if [ ! -f "docker-images.tar.gz" ]; then
    echo "ERROR: docker-images.tar.gz not found!"
    echo "Please ensure the offline bundle files are in the current directory."
    exit 1
fi

echo "Decompressing and loading images..."
gunzip -c docker-images.tar.gz | docker load

echo ""
echo "✅ All images loaded successfully!"
echo ""
echo "Next steps:"
echo "  1. Review docker-compose.yml and .env files"
echo "  2. Create required directories (see README.md)"
echo "  3. Run: docker compose up -d"
echo ""
"""

        # Create README for offline bundle
        offline_readme = """# Offline/Airgapped Installation Bundle

This bundle contains everything needed to run your IIoT stack in an offline/airgapped environment.

## Bundle Contents

- `docker-images.tar.gz` - All required Docker images
- `docker-compose.yml` - Docker Compose configuration
- `.env` - Environment variables
- `configs/` - Configuration files for services
- `load-images.sh` - Script to load images on offline system
- `README.md` - This file

## Prerequisites (on offline system)

- Docker installed and running
- Docker Compose installed
- Sufficient disk space for images (check file size)

## Installation Steps

### 1. Transfer Bundle

Transfer all files from this bundle to your offline system using:
- USB drive
- Network transfer (if temporarily connected)
- Any secure file transfer method

### 2. Load Docker Images

On the offline system, run:

```bash
chmod +x load-images.sh
./load-images.sh
```

Or manually:

```bash
gunzip -c docker-images.tar.gz | docker load
```

### 3. Start the Stack

Follow the same instructions as in the main README.md:

```bash
# Create required directories
mkdir -p configs scripts

# Start services
docker compose up -d
```

## Verification

Check that all images are loaded:

```bash
docker images
```

Check that all services are running:

```bash
docker compose ps
```

## Troubleshooting

### Images not loading
- Ensure docker-images.tar.gz is not corrupted
- Check available disk space
- Verify Docker daemon is running

### Services failing to start
- Check logs: `docker compose logs -f`
- Verify all config files are present
- Ensure ports are not in use

## Support

For issues and documentation, see the main README.md file.

---

Generated by Ignition Stack Builder - Offline Bundle
"""

        # Create ZIP file with offline bundle
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add all generated files
            zip_file.writestr("docker-compose.yml", generated["docker_compose"])
            zip_file.writestr(".env", generated["env"])
            zip_file.writestr("README.md", generated["readme"])
            zip_file.writestr("OFFLINE-README.md", offline_readme)
            zip_file.writestr("pull-images.sh", pull_script)
            zip_file.writestr("load-images.sh", load_script)

            # Add config files
            for file_path, content in generated.get("config_files", {}).items():
                info = zipfile.ZipInfo(file_path)
                info.external_attr = 0o644 << 16
                zip_file.writestr(info, content)

            # Add instructions file
            instructions = """OFFLINE BUNDLE CREATION INSTRUCTIONS
=====================================

Step 1: On a system WITH internet access:
-----------------------------------------
1. Extract this bundle
2. Run: chmod +x pull-images.sh
3. Run: ./pull-images.sh
   This will download all Docker images and create docker-images.tar.gz

Step 2: Transfer to offline system:
-----------------------------------
1. Copy ALL files including docker-images.tar.gz to offline system
2. Use USB drive, secure network transfer, or approved method

Step 3: On the OFFLINE system:
------------------------------
1. Run: chmod +x load-images.sh
2. Run: ./load-images.sh
3. Follow README.md to start the stack

The docker-images.tar.gz file will be large (several GB).
Ensure you have sufficient space and transfer capacity.
"""
            zip_file.writestr("INSTRUCTIONS.txt", instructions)

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f'attachment; filename="{global_settings.stack_name}-offline-bundle.zip"'
            },
        )

    except Exception as e:
        logger.error(f"Error generating offline bundle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
