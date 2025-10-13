"""
Keycloak realm configuration generator
Generates realm-import.json for automatic OAuth/SSO setup
"""

import hashlib
import json
import secrets
from typing import Any, Dict, List, Optional


def generate_client_secret(service_name: str) -> str:
    """Generate a secure client secret"""
    return secrets.token_urlsafe(32)


def generate_keycloak_realm(
    realm_name: str = "iiot",
    services: List[str] = None,
    users: List[Dict[str, Any]] = None,
    base_domain: str = "localhost",
    enable_https: bool = False,
) -> Dict[str, Any]:
    """
    Generate a complete Keycloak realm configuration

    Args:
        realm_name: Name of the realm
        services: List of service IDs that need OAuth clients
        users: List of users to import
        base_domain: Base domain for redirect URIs
        enable_https: Whether to use HTTPS URLs

    Returns:
        Complete realm configuration as dict
    """

    services = services or []
    users = users or []
    protocol = "https" if enable_https else "http"

    # Base realm configuration
    realm = {
        "id": realm_name,
        "realm": realm_name,
        "displayName": "IIoT Stack",
        "displayNameHtml": '<div class="kc-logo-text"><span>IIoT Stack</span></div>',
        "enabled": True,
        "sslRequired": "external",
        "registrationAllowed": False,
        "loginWithEmailAllowed": True,
        "duplicateEmailsAllowed": False,
        "resetPasswordAllowed": True,
        "editUsernameAllowed": False,
        "bruteForceProtected": True,
        # Session settings
        "ssoSessionIdleTimeout": 1800,
        "ssoSessionMaxLifespan": 36000,
        "offlineSessionIdleTimeout": 2592000,
        # Token settings
        "accessTokenLifespan": 300,
        "accessTokenLifespanForImplicitFlow": 900,
        "accessCodeLifespan": 60,
        "accessCodeLifespanUserAction": 300,
        # Roles
        "roles": {
            "realm": [
                {
                    "name": "admin",
                    "description": "Administrator role with full access",
                    "composite": False,
                },
                {
                    "name": "user",
                    "description": "Standard user role",
                    "composite": False,
                },
                {
                    "name": "viewer",
                    "description": "Read-only access",
                    "composite": False,
                },
            ],
            "client": {},
        },
        # Client scopes
        "clientScopes": [
            {
                "name": "roles",
                "description": "OpenID Connect scope for add user roles to the access token",
                "protocol": "openid-connect",
                "attributes": {
                    "include.in.token.scope": "true",
                    "display.on.consent.screen": "true",
                },
                "protocolMappers": [
                    {
                        "name": "realm roles",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-usermodel-realm-role-mapper",
                        "config": {
                            "multivalued": "true",
                            "userinfo.token.claim": "true",
                            "id.token.claim": "true",
                            "access.token.claim": "true",
                            "claim.name": "roles",
                            "jsonType.label": "String",
                        },
                    }
                ],
            },
            {
                "name": "email",
                "description": "OpenID Connect built-in scope: email",
                "protocol": "openid-connect",
                "attributes": {
                    "include.in.token.scope": "true",
                    "display.on.consent.screen": "true",
                },
                "protocolMappers": [
                    {
                        "name": "email",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-usermodel-property-mapper",
                        "config": {
                            "userinfo.token.claim": "true",
                            "user.attribute": "email",
                            "id.token.claim": "true",
                            "access.token.claim": "true",
                            "claim.name": "email",
                            "jsonType.label": "String",
                        },
                    }
                ],
            },
            {
                "name": "profile",
                "description": "OpenID Connect built-in scope: profile",
                "protocol": "openid-connect",
                "attributes": {
                    "include.in.token.scope": "true",
                    "display.on.consent.screen": "true",
                },
                "protocolMappers": [
                    {
                        "name": "given name",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-usermodel-property-mapper",
                        "config": {
                            "userinfo.token.claim": "true",
                            "user.attribute": "firstName",
                            "id.token.claim": "true",
                            "access.token.claim": "true",
                            "claim.name": "given_name",
                            "jsonType.label": "String",
                        },
                    },
                    {
                        "name": "family name",
                        "protocol": "openid-connect",
                        "protocolMapper": "oidc-usermodel-property-mapper",
                        "config": {
                            "userinfo.token.claim": "true",
                            "user.attribute": "lastName",
                            "id.token.claim": "true",
                            "access.token.claim": "true",
                            "claim.name": "family_name",
                            "jsonType.label": "String",
                        },
                    },
                ],
            },
        ],
        # Users
        "users": [],
        # Clients
        "clients": [],
    }

    # Add users
    for user in users:
        realm["users"].append(_generate_user(user, realm_name))

    # Add OAuth clients for each service
    clients = []

    if "grafana" in services:
        clients.append(_generate_grafana_client(realm_name, base_domain, protocol))

    if "n8n" in services:
        clients.append(_generate_n8n_client(realm_name, base_domain, protocol))

    if "portainer" in services:
        clients.append(_generate_portainer_client(realm_name, base_domain, protocol))

    if "ignition" in services:
        clients.append(_generate_ignition_client(realm_name, base_domain, protocol))

    realm["clients"] = clients

    return realm


def _generate_user(user_data: Dict[str, Any], realm_name: str) -> Dict[str, Any]:
    """Generate a Keycloak user object"""

    username = user_data.get("username", "")
    password = user_data.get("password", "changeme")
    email = user_data.get("email", f"{username}@{realm_name}.local")
    first_name = user_data.get("firstName", username.capitalize())
    last_name = user_data.get("lastName", "User")

    # Determine roles
    roles = user_data.get("roles", ["user"])
    if not isinstance(roles, list):
        roles = [roles]

    return {
        "username": username,
        "enabled": True,
        "emailVerified": True,
        "email": email,
        "firstName": first_name,
        "lastName": last_name,
        "credentials": [
            {
                "type": "password",
                "value": password,
                "temporary": user_data.get("temporary", True),
            }
        ],
        "realmRoles": roles,
        "requiredActions": (
            ["UPDATE_PASSWORD"] if user_data.get("temporary", True) else []
        ),
    }


def _generate_grafana_client(
    realm_name: str, base_domain: str, protocol: str
) -> Dict[str, Any]:
    """Generate Grafana OAuth client configuration"""

    client_secret = generate_client_secret("grafana")
    redirect_uri = f"{protocol}://grafana.{base_domain}/*"

    return {
        "clientId": "grafana",
        "name": "Grafana",
        "description": "Grafana Analytics Platform",
        "enabled": True,
        "clientAuthenticatorType": "client-secret",
        "secret": client_secret,
        "redirectUris": [
            redirect_uri,
            f"{protocol}://grafana.{base_domain}/login/generic_oauth",
        ],
        "webOrigins": ["+"],
        "protocol": "openid-connect",
        "publicClient": False,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "implicitFlowEnabled": False,
        "serviceAccountsEnabled": False,
        "authorizationServicesEnabled": False,
        "fullScopeAllowed": True,
        "defaultClientScopes": ["email", "profile", "roles"],
        "optionalClientScopes": [],
        "attributes": {
            "saml.assertion.signature": "false",
            "saml.force.post.binding": "false",
            "saml.multivalued.roles": "false",
            "saml.encrypt": "false",
            "saml.server.signature": "false",
            "saml.server.signature.keyinfo.ext": "false",
            "exclude.session.state.from.auth.response": "false",
            "saml_force_name_id_format": "false",
            "saml.client.signature": "false",
            "tls.client.certificate.bound.access.tokens": "false",
            "saml.authnstatement": "false",
            "display.on.consent.screen": "false",
            "saml.onetimeuse.condition": "false",
        },
        "protocolMappers": [
            {
                "name": "grafana-role-mapper",
                "protocol": "openid-connect",
                "protocolMapper": "oidc-usermodel-realm-role-mapper",
                "config": {
                    "claim.name": "roles",
                    "jsonType.label": "String",
                    "multivalued": "true",
                    "userinfo.token.claim": "true",
                    "id.token.claim": "true",
                    "access.token.claim": "true",
                },
            }
        ],
    }


def _generate_n8n_client(
    realm_name: str, base_domain: str, protocol: str
) -> Dict[str, Any]:
    """Generate n8n OAuth client configuration"""

    client_secret = generate_client_secret("n8n")

    return {
        "clientId": "n8n",
        "name": "n8n Workflow Automation",
        "enabled": True,
        "clientAuthenticatorType": "client-secret",
        "secret": client_secret,
        "redirectUris": [
            f"{protocol}://n8n.{base_domain}/*",
            f"{protocol}://n8n.{base_domain}/rest/oauth2-credential/callback",
        ],
        "webOrigins": ["+"],
        "protocol": "openid-connect",
        "publicClient": False,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "fullScopeAllowed": True,
        "defaultClientScopes": ["email", "profile", "roles"],
    }


def _generate_portainer_client(
    realm_name: str, base_domain: str, protocol: str
) -> Dict[str, Any]:
    """Generate Portainer OAuth client configuration"""

    client_secret = generate_client_secret("portainer")

    return {
        "clientId": "portainer",
        "name": "Portainer",
        "enabled": True,
        "clientAuthenticatorType": "client-secret",
        "secret": client_secret,
        "redirectUris": [f"{protocol}://portainer.{base_domain}/*"],
        "webOrigins": ["+"],
        "protocol": "openid-connect",
        "publicClient": False,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "fullScopeAllowed": True,
        "defaultClientScopes": ["email", "profile", "roles"],
    }


def _generate_ignition_client(
    realm_name: str, base_domain: str, protocol: str
) -> Dict[str, Any]:
    """Generate Ignition OAuth client configuration (for future IdP module support)"""

    client_secret = generate_client_secret("ignition")

    return {
        "clientId": "ignition",
        "name": "Ignition SCADA",
        "enabled": True,
        "clientAuthenticatorType": "client-secret",
        "secret": client_secret,
        "redirectUris": [
            f"{protocol}://ignition.{base_domain}/*",
            f"{protocol}://ignition.{base_domain}/data/perspective/client/*",
        ],
        "webOrigins": ["+"],
        "protocol": "openid-connect",
        "publicClient": False,
        "directAccessGrantsEnabled": True,
        "standardFlowEnabled": True,
        "fullScopeAllowed": True,
        "defaultClientScopes": ["email", "profile", "roles"],
    }


def generate_keycloak_readme_section(
    realm_name: str, clients: List[Dict[str, Any]]
) -> str:
    """Generate README section with Keycloak setup instructions and client secrets"""

    content = f"""
## 🔐 Keycloak SSO Configuration

Your stack includes automatic Keycloak realm configuration for Single Sign-On (SSO).

### Realm Import

The realm configuration has been automatically imported on first startup.

**Realm Name:** `{realm_name}`

### OAuth Client Credentials

Use these credentials to configure OAuth in your applications:

"""

    for client in clients:
        client_id = client.get("clientId")
        client_secret = client.get("secret", "N/A")

        content += f"""
#### {client.get("name", client_id)}
- **Client ID:** `{client_id}`
- **Client Secret:** `{client_secret}`
- **Scopes:** openid, profile, email, roles

"""

    content += f"""
### Accessing Keycloak Admin Console

1. Navigate to Keycloak: `http://keycloak.localhost` (or your configured domain)
2. Login with admin credentials (from your configuration)
3. Select the `{realm_name}` realm from the dropdown

### Default Users

Users configured in your integration settings have been imported.
All users are required to change their password on first login.

### Adding New Users

1. Go to Keycloak Admin Console → Users
2. Click "Add User"
3. Fill in username, email, first name, last name
4. Click "Save"
5. Go to "Credentials" tab
6. Set temporary password

### Roles

Three realm roles are available:
- **admin** - Full administrative access
- **user** - Standard user access
- **viewer** - Read-only access

Assign roles to users in the Admin Console → Users → Role Mappings.
"""

    return content
