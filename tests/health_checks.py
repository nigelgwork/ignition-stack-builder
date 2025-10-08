#!/usr/bin/env python3
"""
Health check utilities for IIoT Stack Builder testing
Verifies that services are actually functional, not just running
"""

import requests
import subprocess
import socket
import sys
import time
from typing import Tuple, Dict

class HealthChecker:
    """Service health verification"""

    def check_port(self, host: str, port: int, timeout: int = 2) -> bool:
        """Check if TCP port is open"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except:
            return False

    def check_http(self, url: str, timeout: int = 5) -> Tuple[bool, str]:
        """Check if HTTP endpoint is accessible"""
        try:
            r = requests.get(url, timeout=timeout)
            return True, f"HTTP {r.status_code}"
        except Exception as e:
            return False, str(e)

    def check_ignition(self, port: int = 8088) -> Tuple[bool, str]:
        """Check Ignition Gateway health"""
        try:
            r = requests.get(f"http://localhost:{port}/StatusPing", timeout=10)
            status = r.text.strip()
            if status == "RUNNING":
                return True, "Gateway running"
            return False, f"Gateway status: {status}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def check_postgres(self, container: str = "postgres") -> Tuple[bool, str]:
        """Check PostgreSQL health"""
        try:
            result = subprocess.run(
                ["docker", "exec", container, "pg_isready"],
                capture_output=True, text=True, timeout=5
            )
            if "accepting connections" in result.stdout:
                return True, "Database accepting connections"
            return False, result.stdout + result.stderr
        except Exception as e:
            return False, str(e)

    def check_grafana(self, port: int = 3000) -> Tuple[bool, str]:
        """Check Grafana health"""
        try:
            r = requests.get(f"http://localhost:{port}/api/health", timeout=10)
            data = r.json()
            if data.get("database") == "ok":
                return True, f"Grafana healthy (v{data.get('version', 'unknown')})"
            return False, f"Health check failed: {data}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def check_traefik(self, port: int = 8080) -> Tuple[bool, str]:
        """Check Traefik health"""
        try:
            r = requests.get(f"http://localhost:{port}/api/http/routers", timeout=10)
            routers = r.json()
            return True, f"Traefik running ({len(routers)} routers configured)"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def check_keycloak(self, port: int = 8180) -> Tuple[bool, str]:
        """Check Keycloak health"""
        try:
            r = requests.get(f"http://localhost:{port}/health/ready", timeout=10)
            data = r.json()
            if data.get("status") == "UP":
                return True, "Keycloak ready"
            return False, f"Status: {data.get('status', 'unknown')}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def check_container_running(self, container_name: str) -> Tuple[bool, str]:
        """Check if Docker container is running"""
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format={{.State.Status}}", container_name],
                capture_output=True, text=True, timeout=5
            )
            status = result.stdout.strip()
            if status == "running":
                return True, f"Container running"
            return False, f"Container status: {status}"
        except Exception as e:
            return False, f"Container check failed: {str(e)}"

def run_checks(service_type: str, container_name: str, config: Dict = None) -> Dict:
    """Run health checks for a specific service"""
    checker = HealthChecker()
    results = {
        "service": service_type,
        "container": container_name,
        "checks": [],
        "overall": False
    }

    # Container running check (always)
    running, msg = checker.check_container_running(container_name)
    results["checks"].append({"name": "Container Status", "passed": running, "message": msg})

    if not running:
        return results

    # Service-specific checks
    if service_type == "ignition":
        port = config.get("http_port", 8088) if config else 8088
        passed, msg = checker.check_ignition(port)
        results["checks"].append({"name": "Ignition Gateway", "passed": passed, "message": msg})

    elif service_type == "postgres":
        passed, msg = checker.check_postgres(container_name)
        results["checks"].append({"name": "PostgreSQL Ready", "passed": passed, "message": msg})

    elif service_type == "grafana":
        port = config.get("port", 3000) if config else 3000
        passed, msg = checker.check_grafana(port)
        results["checks"].append({"name": "Grafana API", "passed": passed, "message": msg})

    elif service_type == "traefik":
        passed, msg = checker.check_traefik(8080)
        results["checks"].append({"name": "Traefik API", "passed": passed, "message": msg})

    elif service_type == "keycloak":
        port = config.get("port", 8180) if config else 8180
        passed, msg = checker.check_keycloak(port)
        results["checks"].append({"name": "Keycloak Health", "passed": passed, "message": msg})

    # Overall result
    results["overall"] = all(check["passed"] for check in results["checks"])

    return results

if __name__ == "__main__":
    # Simple CLI for manual testing
    if len(sys.argv) < 3:
        print("Usage: health_checks.py <service_type> <container_name>")
        sys.exit(1)

    service_type = sys.argv[1]
    container_name = sys.argv[2]

    print(f"Running health checks for {service_type} ({container_name})...")
    results = run_checks(service_type, container_name)

    for check in results["checks"]:
        status = "✅" if check["passed"] else "❌"
        print(f"{status} {check['name']}: {check['message']}")

    if results["overall"]:
        print("\n✅ All checks passed")
        sys.exit(0)
    else:
        print("\n❌ Some checks failed")
        sys.exit(1)
