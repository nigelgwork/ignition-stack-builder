#!/usr/bin/env python3
"""
Comprehensive Authentication API Test Script
Tests all authentication endpoints systematically
"""

import requests
import json
import sys
import time
from datetime import datetime

API_URL = "http://localhost:8000/api"
TEST_EMAIL = f"test_{int(time.time())}@example.com"
TEST_PASSWORD = "TestPass123!@#"
TEST_NAME = "Test User"

# ANSI color codes
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

tests_passed = 0
tests_failed = 0

def print_header(text):
    print(f"\n{BLUE}{'=' * 60}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'=' * 60}{NC}\n")

def print_section(text):
    print(f"\n{BLUE}{'━' * 60}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'━' * 60}{NC}\n")

def test_endpoint(test_name, method, endpoint, data=None, headers=None, expected_status=200):
    """Test an API endpoint"""
    global tests_passed, tests_failed

    print(f"{YELLOW}Testing:{NC} {test_name}")

    url = f"{API_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)

        if response.status_code == expected_status:
            print(f"{GREEN}✓ PASSED{NC} (HTTP {response.status_code})")
            tests_passed += 1

            # Print response body if JSON
            if response.content:
                try:
                    print(json.dumps(response.json(), indent=2))
                except:
                    print(response.text[:200])

            return response
        else:
            print(f"{RED}✗ FAILED{NC} (Expected HTTP {expected_status}, got {response.status_code})")
            print(f"Response: {response.text[:200]}")
            tests_failed += 1
            return None

    except Exception as e:
        print(f"{RED}✗ ERROR:{NC} {str(e)}")
        tests_failed += 1
        return None

def main():
    global tests_passed, tests_failed

    print_header("Authentication API Test Suite")

    # Test 1: User Registration
    print_section("1. User Registration")

    register_response = test_endpoint(
        "Register new user",
        "POST",
        "/auth/register",
        data={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": TEST_NAME
        },
        expected_status=201
    )

    if not register_response:
        print(f"{RED}Registration failed, cannot continue{NC}")
        sys.exit(1)

    # Test 2: Login
    print_section("2. User Login")

    login_response = test_endpoint(
        "Login with correct credentials",
        "POST",
        "/auth/login",
        data={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        },
        expected_status=200
    )

    if not login_response:
        print(f"{RED}Login failed, cannot continue{NC}")
        sys.exit(1)

    login_data = login_response.json()
    access_token = login_data.get("access_token")
    refresh_token = login_data.get("refresh_token")

    if not access_token:
        print(f"{RED}Could not extract access token{NC}")
        sys.exit(1)

    print(f"\n{GREEN}✓ Access token obtained{NC}")

    # Test 3: Login with wrong password
    test_endpoint(
        "Login with wrong password (should fail)",
        "POST",
        "/auth/login",
        data={
            "email": TEST_EMAIL,
            "password": "WrongPassword123!"
        },
        expected_status=401
    )

    # Test 4: Get current user
    print_section("3. Protected Endpoints")

    headers = {"Authorization": f"Bearer {access_token}"}

    test_endpoint(
        "Get current user info",
        "GET",
        "/auth/me",
        headers=headers,
        expected_status=200
    )

    # Test 5: Settings Management
    print_section("4. Settings Management")

    test_endpoint(
        "Get user settings",
        "GET",
        "/settings",
        headers=headers,
        expected_status=200
    )

    test_endpoint(
        "Update user settings",
        "PUT",
        "/settings",
        data={
            "theme": "light",
            "timezone": "UTC",
            "notifications_enabled": True
        },
        headers=headers,
        expected_status=200
    )

    # Test 6: Stack Management
    print_section("5. Stack Management")

    create_stack_response = test_endpoint(
        "Create new stack",
        "POST",
        "/stacks",
        data={
            "stack_name": "Test Stack",
            "description": "A test stack",
            "config_json": {"services": ["ignition"]},
            "is_public": False
        },
        headers=headers,
        expected_status=201
    )

    stack_id = None
    if create_stack_response:
        stack_data = create_stack_response.json()
        stack_id = stack_data.get("id")

    test_endpoint(
        "List user stacks",
        "GET",
        "/stacks",
        headers=headers,
        expected_status=200
    )

    if stack_id:
        test_endpoint(
            "Get specific stack",
            "GET",
            f"/stacks/{stack_id}",
            headers=headers,
            expected_status=200
        )

        test_endpoint(
            "Update stack",
            "PUT",
            f"/stacks/{stack_id}",
            data={
                "stack_name": "Updated Test Stack",
                "description": "An updated test stack"
            },
            headers=headers,
            expected_status=200
        )

        test_endpoint(
            "Delete stack",
            "DELETE",
            f"/stacks/{stack_id}",
            headers=headers,
            expected_status=204
        )

    # Test 7: Token Refresh
    print_section("6. Token Refresh")

    test_endpoint(
        "Refresh access token",
        "POST",
        "/auth/refresh",
        data={"refresh_token": refresh_token},
        expected_status=200
    )

    # Test 8: Logout
    print_section("7. Logout")

    test_endpoint(
        "Logout user",
        "POST",
        "/auth/logout",
        headers=headers,
        expected_status=200
    )

    # Test 9: Authorization Tests
    print_section("8. Authorization Tests")

    test_endpoint(
        "Access protected endpoint without token (should fail)",
        "GET",
        "/auth/me",
        expected_status=403
    )

    test_endpoint(
        "Access with invalid token (should fail)",
        "GET",
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token_12345"},
        expected_status=401
    )

    # Test Summary
    print_header("Test Summary")
    print(f"Tests Passed: {GREEN}{tests_passed}{NC}")
    print(f"Tests Failed: {RED}{tests_failed}{NC}")
    print()

    if tests_failed == 0:
        print(f"{GREEN}✓ All tests passed!{NC}")
        return 0
    else:
        print(f"{RED}✗ Some tests failed{NC}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
