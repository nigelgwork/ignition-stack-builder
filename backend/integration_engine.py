"""
Integration Engine for IIoT Stack Builder
Handles automatic service integration detection and configuration generation.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class IntegrationEngine:
    """Core engine for managing service integrations"""

    def __init__(self, integrations_file: str = "integrations.json"):
        """Initialize the integration engine"""
        self.integrations_file = integrations_file
        self.integrations = self._load_integrations()
        self.integration_types = self.integrations.get("integration_types", {})
        self.service_capabilities = self.integrations.get("service_capabilities", {})
        self.integration_rules = self.integrations.get("integration_rules", {})
        self.config_templates = self.integrations.get("config_templates", {})

    def _load_integrations(self) -> Dict:
        """Load integrations configuration from JSON file"""
        try:
            with open(self.integrations_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Integrations file not found: {self.integrations_file}")
            return {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing integrations file: {e}")
            return {}

    def detect_integrations(self, instances: List[Dict]) -> Dict[str, Any]:
        """
        Detect all possible integrations based on selected services

        Args:
            instances: List of instance configurations

        Returns:
            Dictionary containing detected integrations, conflicts, and recommendations
        """
        result = {
            "integrations": {},
            "conflicts": [],
            "warnings": [],
            "recommendations": [],
            "auto_add_services": [],
        }

        # Get list of selected service IDs
        selected_services = [inst["app_id"] for inst in instances]

        # Check mutual exclusivity
        conflicts = self.check_mutual_exclusivity(selected_services)
        result["conflicts"] = conflicts

        # Check dependencies
        deps = self.check_dependencies(selected_services, instances)
        result["warnings"].extend(deps["warnings"])
        result["auto_add_services"] = deps["auto_add"]

        # Detect available integrations
        for integration_type, type_config in self.integration_types.items():
            providers = [
                s for s in selected_services if s in type_config.get("providers", [])
            ]

            if providers:
                # For each provider, find consumers/clients
                if integration_type == "reverse_proxy":
                    result["integrations"][integration_type] = (
                        self._detect_reverse_proxy(
                            providers[0], selected_services, instances
                        )
                    )
                elif integration_type == "oauth_provider":
                    result["integrations"][integration_type] = self._detect_oauth(
                        providers, selected_services, instances
                    )
                elif integration_type == "db_provider":
                    result["integrations"][integration_type] = self._detect_database(
                        providers, selected_services, instances
                    )
                elif integration_type == "mqtt_broker":
                    result["integrations"][integration_type] = self._detect_mqtt(
                        providers, selected_services, instances
                    )
                elif integration_type == "visualization":
                    result["integrations"][integration_type] = (
                        self._detect_visualization(
                            providers, selected_services, instances
                        )
                    )
                elif integration_type == "email_testing":
                    result["integrations"][integration_type] = self._detect_email(
                        providers, selected_services, instances
                    )

        # Get recommendations
        recommendations = self.get_recommendations(selected_services)
        result["recommendations"] = recommendations

        return result

    def check_mutual_exclusivity(self, selected_services: List[str]) -> List[Dict]:
        """Check for mutually exclusive service conflicts"""
        conflicts = []

        exclusivity_rules = self.integration_rules.get("mutual_exclusivity", [])

        for rule in exclusivity_rules:
            group_services = rule["services"]
            selected_from_group = [s for s in selected_services if s in group_services]

            if len(selected_from_group) > 1:
                conflict = {
                    "group": rule["group"],
                    "services": selected_from_group,
                    "message": rule["message"],
                    "level": rule.get("level", "error"),
                }
                conflicts.append(conflict)

        return conflicts

    def check_dependencies(
        self, selected_services: List[str], instances: List[Dict]
    ) -> Dict:
        """Check for missing dependencies and requirements"""
        result = {"warnings": [], "auto_add": []}

        dependency_rules = self.integration_rules.get("dependencies", [])

        for rule in dependency_rules:
            service = rule["service"]

            if service not in selected_services:
                continue

            # Check hard requirements
            if "requires" in rule:
                req = rule["requires"]
                req_type = req.get("type")

                # Check if any service provides this type
                providers = self._find_providers(req_type, selected_services)

                if not providers:
                    if req.get("auto_add", False):
                        # Auto-add the preferred service
                        preferred = req.get("preferred")
                        if preferred:
                            result["auto_add"].append(
                                {
                                    "service": preferred,
                                    "reason": req.get(
                                        "message", f"{service} requires {preferred}"
                                    ),
                                }
                            )
                    else:
                        result["warnings"].append(
                            {
                                "service": service,
                                "message": req.get(
                                    "message", f"{service} requires {req_type}"
                                ),
                                "level": "error",
                            }
                        )

            # Check recommendations
            if "recommends" in rule:
                rec = rule["recommends"]
                rec_type = rec.get("type")

                providers = self._find_providers(rec_type, selected_services)

                if not providers:
                    result["warnings"].append(
                        {
                            "service": service,
                            "message": rec.get(
                                "message", f"{service} recommends {rec_type}"
                            ),
                            "level": rec.get("level", "warning"),
                        }
                    )

        return result

    def get_recommendations(self, selected_services: List[str]) -> List[Dict]:
        """Get recommendations for additional services based on current selection"""
        recommendations = []

        rec_rules = self.integration_rules.get("recommendations", [])

        for rule in rec_rules:
            if_selected = rule.get("if_selected", [])
            if_not_selected = rule.get("if_not_selected", [])

            # Check if condition matches
            if if_selected and all(s in selected_services for s in if_selected):
                # Check if any required services are missing
                if if_not_selected and all(
                    s not in selected_services for s in if_not_selected
                ):
                    recommendations.append(
                        {
                            "message": rule["message"],
                            "level": rule.get("level", "info"),
                            "suggest": rule.get("suggest", []),
                        }
                    )
                elif "suggest" in rule and not if_not_selected:
                    # General suggestion
                    missing = [s for s in rule["suggest"] if s not in selected_services]
                    if missing:
                        recommendations.append(
                            {
                                "message": rule["message"],
                                "level": rule.get("level", "info"),
                                "suggest": missing,
                            }
                        )

            # Check suggest_for pattern (e.g., Keycloak OAuth suggestion)
            if "suggest_for" in rule:
                suggest_for = rule["suggest_for"]
                if if_selected and all(s in selected_services for s in if_selected):
                    # Check which suggested services are selected
                    applicable = [s for s in suggest_for if s in selected_services]
                    if applicable:
                        recommendations.append(
                            {
                                "message": rule["message"],
                                "level": rule.get("level", "info"),
                                "applies_to": applicable,
                            }
                        )

        return recommendations

    def _find_providers(
        self, integration_type: str, selected_services: List[str]
    ) -> List[str]:
        """Find services that provide a specific integration type"""
        providers = []

        type_config = self.integration_types.get(integration_type, {})
        type_providers = type_config.get("providers", [])

        for service in selected_services:
            if service in type_providers:
                providers.append(service)

        return providers

    def _detect_reverse_proxy(
        self, provider: str, selected_services: List[str], instances: List[Dict]
    ) -> Dict:
        """Detect reverse proxy integrations"""
        integration = {
            "provider": provider,
            "targets": [],
            "method": None,
            "config": {},
        }

        # Get provider capabilities
        provider_caps = self.service_capabilities.get(provider, {})
        provider_integration = provider_caps.get("integrations", {}).get(
            "reverse_proxy", {}
        )
        integration["method"] = provider_integration.get("method", "docker_labels")

        # Find all web services that should be proxied
        type_config = self.integration_types.get("reverse_proxy", {})
        auto_targets = type_config.get("auto_configure_targets", [])

        for service_id in selected_services:
            if service_id == provider:
                continue

            if service_id in auto_targets:
                # Get service integration config
                service_caps = self.service_capabilities.get(service_id, {})
                service_integration = service_caps.get("integrations", {}).get(
                    "reverse_proxy", {}
                )

                if service_integration:
                    # Find instance details
                    instance = next(
                        (i for i in instances if i["app_id"] == service_id), None
                    )
                    if instance:
                        # Use custom name from config, fallback to instance_name or service_id
                        custom_name = instance.get("config", {}).get("name")
                        subdomain = (
                            custom_name or instance.get("instance_name") or service_id
                        )

                        target = {
                            "service_id": service_id,
                            "instance_name": instance.get("instance_name"),
                            "ports": service_integration.get("ports", []),
                            "default_subdomain": subdomain,
                            "health_check": service_integration.get("health_check"),
                        }
                        integration["targets"].append(target)

        return integration

    def _detect_oauth(
        self, providers: List[str], selected_services: List[str], instances: List[Dict]
    ) -> Dict:
        """Detect OAuth/SSO integrations"""
        integration = {"providers": providers, "clients": []}

        # For each provider, find compatible clients
        for provider_id in providers:
            provider_caps = self.service_capabilities.get(provider_id, {})
            provider_integration = provider_caps.get("integrations", {}).get(
                "oauth_provider", {}
            )

            if not provider_integration:
                continue

            client_configs = provider_integration.get("client_configs", {})

            # Find selected services that can be OAuth clients
            for service_id in selected_services:
                service_caps = self.service_capabilities.get(service_id, {})
                service_integration = service_caps.get("integrations", {}).get(
                    "oauth_provider", {}
                )

                if service_integration and service_integration.get("type") == "client":
                    supports = service_integration.get("supports", [])

                    if provider_id in supports:
                        instance = next(
                            (i for i in instances if i["app_id"] == service_id), None
                        )
                        if instance:
                            client = {
                                "service_id": service_id,
                                "instance_name": instance.get("instance_name"),
                                "provider": provider_id,
                                "env_vars": service_integration.get("env_vars", {}),
                                "client_config": client_configs.get(service_id, {}),
                            }
                            integration["clients"].append(client)

        return integration

    def _detect_database(
        self, providers: List[str], selected_services: List[str], instances: List[Dict]
    ) -> Dict:
        """Detect database integrations"""
        integration = {"providers": [], "clients": []}

        # Get provider details
        for provider_id in providers:
            instance = next((i for i in instances if i["app_id"] == provider_id), None)
            if instance:
                provider_caps = self.service_capabilities.get(provider_id, {})
                provider_integration = provider_caps.get("integrations", {}).get(
                    "db_provider", {}
                )

                provider_info = {
                    "service_id": provider_id,
                    "instance_name": instance.get("instance_name"),
                    "config": instance.get("config", {}),
                    "jdbc_url_template": provider_integration.get("jdbc_url_template"),
                    "default_port": provider_integration.get("default_port"),
                }
                integration["providers"].append(provider_info)

        # Find database clients
        for service_id in selected_services:
            service_caps = self.service_capabilities.get(service_id, {})
            service_integration = service_caps.get("integrations", {}).get(
                "db_provider", {}
            )

            if service_integration and service_integration.get("type") == "client":
                instance = next(
                    (i for i in instances if i["app_id"] == service_id), None
                )
                if instance:
                    client = {
                        "service_id": service_id,
                        "instance_name": instance.get("instance_name"),
                        "supports": service_integration.get("supports", []),
                        "auto_register": service_integration.get(
                            "auto_register", False
                        ),
                        "jdbc_drivers": service_integration.get("jdbc_drivers", {}),
                    }

                    # Match with compatible providers
                    compatible_providers = [
                        p
                        for p in integration["providers"]
                        if p["service_id"] in client["supports"]
                    ]
                    client["matched_providers"] = compatible_providers

                    integration["clients"].append(client)

        return integration

    def _detect_mqtt(
        self, providers: List[str], selected_services: List[str], instances: List[Dict]
    ) -> Dict:
        """Detect MQTT broker integrations"""
        integration = {"providers": [], "clients": []}

        # Get provider details
        for provider_id in providers:
            instance = next((i for i in instances if i["app_id"] == provider_id), None)
            if instance:
                provider_caps = self.service_capabilities.get(provider_id, {})
                provider_integration = provider_caps.get("integrations", {}).get(
                    "mqtt_broker", {}
                )

                provider_info = {
                    "service_id": provider_id,
                    "instance_name": instance.get("instance_name"),
                    "mqtt_port": provider_integration.get("mqtt_port", 1883),
                    "ws_port": provider_integration.get("ws_port"),
                }
                integration["providers"].append(provider_info)

        # Find MQTT clients
        for service_id in selected_services:
            service_caps = self.service_capabilities.get(service_id, {})
            service_integration = service_caps.get("integrations", {}).get(
                "mqtt_broker", {}
            )

            if service_integration and service_integration.get("type") == "client":
                instance = next(
                    (i for i in instances if i["app_id"] == service_id), None
                )
                if instance:
                    client = {
                        "service_id": service_id,
                        "instance_name": instance.get("instance_name"),
                        "supports": service_integration.get("supports", []),
                        "requires_module": service_integration.get("requires_module"),
                        "config_file": service_integration.get("config_file"),
                    }

                    # Match with compatible providers
                    compatible_providers = [
                        p
                        for p in integration["providers"]
                        if p["service_id"] in client["supports"]
                    ]
                    client["matched_providers"] = compatible_providers

                    integration["clients"].append(client)

        return integration

    def _detect_visualization(
        self, providers: List[str], selected_services: List[str], instances: List[Dict]
    ) -> Dict:
        """Detect visualization (Grafana) datasource integrations"""
        integration = {
            "provider": providers[0] if providers else None,
            "datasources": [],
        }

        if not integration["provider"]:
            return integration

        provider_caps = self.service_capabilities.get(integration["provider"], {})
        provider_integration = provider_caps.get("integrations", {}).get(
            "visualization", {}
        )
        datasource_types = provider_integration.get("datasource_types", {})

        # Find compatible data sources
        for service_id in selected_services:
            if service_id in datasource_types:
                instance = next(
                    (i for i in instances if i["app_id"] == service_id), None
                )
                if instance:
                    datasource = {
                        "service_id": service_id,
                        "instance_name": instance.get("instance_name"),
                        "type": datasource_types[service_id],
                        "config": instance.get("config", {}),
                    }
                    integration["datasources"].append(datasource)

        return integration

    def _detect_email(
        self, providers: List[str], selected_services: List[str], instances: List[Dict]
    ) -> Dict:
        """Detect email testing (MailHog) integrations"""
        integration = {"provider": providers[0] if providers else None, "clients": []}

        if not integration["provider"]:
            return integration

        provider_instance = next(
            (i for i in instances if i["app_id"] == integration["provider"]), None
        )

        # Find services that can use email
        for service_id in selected_services:
            service_caps = self.service_capabilities.get(service_id, {})
            service_integration = service_caps.get("integrations", {}).get(
                "email_testing", {}
            )

            if service_integration and service_integration.get("type") == "client":
                instance = next(
                    (i for i in instances if i["app_id"] == service_id), None
                )
                if instance:
                    client = {
                        "service_id": service_id,
                        "instance_name": instance.get("instance_name"),
                        "env_vars": service_integration.get("env_vars", {}),
                    }
                    integration["clients"].append(client)

        return integration

    def generate_traefik_labels(
        self,
        service_name: str,
        subdomain: str,
        port: int,
        domain: str = "localhost",
        https: bool = False,
    ) -> List[str]:
        """Generate Traefik labels for a service"""
        template = self.config_templates.get(
            "traefik_https_label" if https else "traefik_label", []
        )

        labels = []
        for label_template in template:
            label = label_template.format(
                service_name=service_name, subdomain=subdomain, domain=domain, port=port
            )
            labels.append(label)

        return labels

    def get_integration_summary(self, detection_result: Dict) -> str:
        """Generate a human-readable summary of detected integrations"""
        lines = ["# Integration Summary\n"]

        integrations = detection_result.get("integrations", {})

        if "reverse_proxy" in integrations:
            rp = integrations["reverse_proxy"]
            lines.append(f"## Reverse Proxy: {rp['provider']}")
            lines.append(f"Configured {len(rp['targets'])} services:")
            for target in rp["targets"]:
                lines.append(
                    f"  - {target['instance_name']} → {target['default_subdomain']}.localhost"
                )
            lines.append("")

        if "oauth_provider" in integrations:
            oauth = integrations["oauth_provider"]
            lines.append(f"## OAuth/SSO: {', '.join(oauth['providers'])}")
            lines.append(f"Configured {len(oauth['clients'])} clients:")
            for client in oauth["clients"]:
                lines.append(f"  - {client['instance_name']} → {client['provider']}")
            lines.append("")

        if "db_provider" in integrations:
            db = integrations["db_provider"]
            lines.append(f"## Databases")
            for provider in db["providers"]:
                lines.append(f"  Provider: {provider['instance_name']}")
            for client in db["clients"]:
                if client.get("auto_register"):
                    lines.append(f"  - Auto-registered in {client['instance_name']}")
            lines.append("")

        conflicts = detection_result.get("conflicts", [])
        if conflicts:
            lines.append("## ⚠️ Conflicts")
            for conflict in conflicts:
                lines.append(f"  - {conflict['message']}")
            lines.append("")

        warnings = detection_result.get("warnings", [])
        if warnings:
            lines.append("## ℹ️ Warnings")
            for warning in warnings:
                lines.append(f"  - {warning['message']}")
            lines.append("")

        return "\n".join(lines)


# Singleton instance
_engine = None


def get_integration_engine() -> IntegrationEngine:
    """Get or create the integration engine singleton"""
    global _engine
    if _engine is None:
        _engine = IntegrationEngine()
    return _engine
