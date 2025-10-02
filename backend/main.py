from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import yaml
import io
import zipfile
from pathlib import Path

app = FastAPI(title="IIoT Stack Builder API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load catalog
def load_catalog():
    with open("catalog.json", "r") as f:
        return json.load(f)

# Pydantic models
class InstanceConfig(BaseModel):
    app_id: str
    instance_name: str
    config: Dict[str, Any]
    instanceId: Optional[float] = None

class GlobalSettings(BaseModel):
    timezone: str = "Australia/Adelaide"
    restart_policy: str = "unless-stopped"

class StackConfig(BaseModel):
    instances: List[InstanceConfig]
    integrations: List[str] = []
    global_settings: Optional[GlobalSettings] = None

@app.get("/")
def read_root():
    return {"message": "IIoT Stack Builder API", "version": "1.0.0"}

@app.get("/catalog")
def get_catalog():
    """Get the application catalog"""
    return load_catalog()

@app.post("/generate")
def generate_stack(stack_config: StackConfig):
    """Generate docker-compose.yml and configuration files"""
    try:
        catalog = load_catalog()
        catalog_dict = {app["id"]: app for app in catalog["applications"]}

        # Get global settings
        global_settings = stack_config.global_settings or GlobalSettings()

        # Build docker-compose structure
        compose = {
            "version": "3.8",
            "services": {},
            "networks": {
                "iiot-network": {
                    "driver": "bridge"
                }
            },
            "volumes": {}
        }

        env_vars = []
        env_vars.append("# Global Settings")
        env_vars.append(f"TZ={global_settings.timezone}")
        env_vars.append(f"RESTART_POLICY={global_settings.restart_policy}")
        env_vars.append("")

        # Process each instance
        for instance in stack_config.instances:
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
                "container_name": service_name,
                "networks": ["iiot-network"],
                "restart": global_settings.restart_policy
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
                                host_port = config.get("http_port", port_mapping.split(":")[0])
                            elif container_port == "8043":
                                host_port = config.get("https_port", port_mapping.split(":")[0])
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
                            host_port = config.get("port", config.get("http_port", port_mapping.split(":")[0]))

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
                    env["POSTGRES_USER"] = config.get("username", env.get("POSTGRES_USER"))
                    env["POSTGRES_PASSWORD"] = config.get("password", env.get("POSTGRES_PASSWORD"))

                elif instance.app_id == "mariadb":
                    env["MYSQL_DATABASE"] = config.get("database", env.get("MYSQL_DATABASE"))
                    env["MYSQL_USER"] = config.get("username", env.get("MYSQL_USER"))
                    env["MYSQL_PASSWORD"] = config.get("password", env.get("MYSQL_PASSWORD"))
                    env["MYSQL_ROOT_PASSWORD"] = config.get("root_password", env.get("MYSQL_ROOT_PASSWORD"))

                elif instance.app_id == "mssql":
                    env["SA_PASSWORD"] = config.get("sa_password", env.get("SA_PASSWORD"))
                    env["MSSQL_PID"] = config.get("edition", env.get("MSSQL_PID"))

                elif instance.app_id == "ignition":
                    env["GATEWAY_ADMIN_USERNAME"] = config.get("admin_username", env.get("GATEWAY_ADMIN_USERNAME"))
                    env["GATEWAY_ADMIN_PASSWORD"] = config.get("admin_password", env.get("GATEWAY_ADMIN_PASSWORD"))
                    env["IGNITION_EDITION"] = config.get("edition", env.get("IGNITION_EDITION", "standard"))

                    # Handle modules - convert array to comma-separated string
                    modules = config.get("modules", ["perspective", "vision", "tag-historian", "sql-bridge", "alarm-notification", "opc-ua", "reporting"])
                    if isinstance(modules, list):
                        env["GATEWAY_MODULES_ENABLED"] = ",".join(modules)
                    else:
                        env["GATEWAY_MODULES_ENABLED"] = str(modules)

                    # Handle third party modules
                    third_party_modules = config.get("third_party_modules", "")
                    if third_party_modules and third_party_modules.strip():
                        # Split by newlines and filter empty lines
                        module_urls = [url.strip() for url in third_party_modules.split('\n') if url.strip()]
                        if module_urls:
                            env["GATEWAY_MODULE_RELINK"] = ";".join(module_urls)

                    env["IGNITION_MEMORY_MAX"] = config.get("memory_max", env.get("IGNITION_MEMORY_MAX", "2048m"))
                    env["IGNITION_MEMORY_INIT"] = config.get("memory_init", env.get("IGNITION_MEMORY_INIT", "512m"))

                    # Handle commissioning options
                    if config.get("commissioning_allow_non_secure", True):
                        env["GATEWAY_SYSTEM_COMMISSIONING_ALLOWINSECURE"] = "true"

                    if config.get("quick_start", True):
                        env["IGNITION_QUICKSTART"] = "true"

                elif instance.app_id == "keycloak":
                    env["KEYCLOAK_ADMIN"] = config.get("admin_username", env.get("KEYCLOAK_ADMIN"))
                    env["KEYCLOAK_ADMIN_PASSWORD"] = config.get("admin_password", env.get("KEYCLOAK_ADMIN_PASSWORD"))

                elif instance.app_id == "grafana":
                    env["GF_SECURITY_ADMIN_USER"] = config.get("admin_username", env.get("GF_SECURITY_ADMIN_USER"))
                    env["GF_SECURITY_ADMIN_PASSWORD"] = config.get("admin_password", env.get("GF_SECURITY_ADMIN_PASSWORD"))

                elif instance.app_id == "n8n":
                    env["N8N_BASIC_AUTH_USER"] = config.get("username", env.get("N8N_BASIC_AUTH_USER"))
                    env["N8N_BASIC_AUTH_PASSWORD"] = config.get("password", env.get("N8N_BASIC_AUTH_PASSWORD"))

                elif instance.app_id == "rabbitmq":
                    env["RABBITMQ_DEFAULT_USER"] = config.get("username", env.get("RABBITMQ_DEFAULT_USER"))
                    env["RABBITMQ_DEFAULT_PASS"] = config.get("password", env.get("RABBITMQ_DEFAULT_PASS"))

                elif instance.app_id == "vault":
                    env["VAULT_DEV_ROOT_TOKEN_ID"] = config.get("root_token", env.get("VAULT_DEV_ROOT_TOKEN_ID"))

                service["environment"] = env

            # Handle volumes
            if "volumes" in app["default_config"]:
                volumes = []
                for vol in app["default_config"]["volumes"]:
                    # Replace {instance_name} placeholder
                    vol = vol.replace("{instance_name}", service_name)
                    volumes.append(vol)
                service["volumes"] = volumes

            # Handle command
            if "command" in app["default_config"]:
                service["command"] = app["default_config"]["command"]

            # Handle cap_add (for services like Vault)
            if "cap_add" in app["default_config"]:
                service["cap_add"] = app["default_config"]["cap_add"]

            compose["services"][service_name] = service

            # Add to env file
            env_vars.append(f"# {service_name}")
            env_vars.append(f"{service_name.upper().replace('-', '_')}_VERSION={version}")
            if "environment" in service:
                for key, value in service["environment"].items():
                    env_vars.append(f"{service_name.upper().replace('-', '_')}_{key}={value}")
            env_vars.append("")

        # Convert to YAML
        compose_yaml = yaml.dump(compose, default_flow_style=False, sort_keys=False)

        # Create .env file
        env_content = "\n".join(env_vars)

        # Create README
        readme_content = f"""# IIoT Stack - Generated Configuration

## Global Settings
- **Timezone**: {global_settings.timezone}
- **Restart Policy**: {global_settings.restart_policy}

## Services Included
{chr(10).join([f"- {instance.instance_name} ({instance.app_id}) - {instance.config.get('version', 'latest')}" for instance in stack_config.instances])}

## Getting Started

1. Review the generated `docker-compose.yml` and `.env` files
2. Customize any settings as needed
3. Create required directories:
   ```bash
   mkdir -p configs
   ```
4. Start the stack:
   ```bash
   docker-compose up -d
   ```

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
                elif instance.app_id == "loki":
                    port = config.get("port", 3100)
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
                else:
                    port = config.get("port", config.get("http_port", "8080"))
                    url = f"http://localhost:{port}"

                readme_content += f"- **{instance.instance_name}**: {url}\n"

        readme_content += """
## Stopping the Stack

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## Generated by IIoT Stack Builder
"""

        return {
            "docker_compose": compose_yaml,
            "env": env_content,
            "readme": readme_content
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download")
def download_stack(stack_config: StackConfig):
    """Download complete stack as ZIP file"""
    try:
        generated = generate_stack(stack_config)

        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("docker-compose.yml", generated["docker_compose"])
            zip_file.writestr(".env", generated["env"])
            zip_file.writestr("README.md", generated["readme"])

            # Create directory structure placeholders
            zip_file.writestr("configs/.gitkeep", "")
            zip_file.writestr("scripts/.gitkeep", "")

        zip_buffer.seek(0)

        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={"Content-Disposition": "attachment; filename=iiot-stack.zip"}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
