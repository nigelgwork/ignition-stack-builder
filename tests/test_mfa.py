#!/usr/bin/env python3
"""
Comprehensive MFA (Multi-Factor Authentication) Test Script
Tests TOTP setup, verification, backup codes, and MFA login flow
"""

import json
import sys
import time
from datetime import datetime

import pyotp
import requests

API_URL = "http://localhost:8000/api"
TEST_EMAIL = f"mfa_test_{int(time.time())}@example.com"
TEST_PASSWORD = "MFATestPass123!@#"
TEST_NAME = "MFA Test User"

# ANSI color codes
GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
NC = "\033[0m"  # No Color

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


def test_endpoint(
    test_name, method, endpoint, data=None, headers=None, expected_status=200
):
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
                    resp_json = response.json()
                    # Truncate long fields for readability
                    if isinstance(resp_json, dict):
                        display_json = resp_json.copy()
                        if "qr_code" in display_json:
                            display_json["qr_code"] = (
                                f"<{len(display_json['qr_code'])} chars>"
                            )
                        if "backup_codes" in display_json:
                            display_json["backup_codes"] = (
                                f"<{len(display_json['backup_codes'])} codes>"
                            )
                        print(json.dumps(display_json, indent=2))
                    else:
                        print(json.dumps(resp_json, indent=2))
                except:
                    print(response.text[:200])

            return response
        else:
            print(
                f"{RED}✗ FAILED{NC} (Expected HTTP {expected_status}, got {response.status_code})"
            )
            print(f"Response: {response.text[:200]}")
            tests_failed += 1
            return None

    except Exception as e:
        print(f"{RED}✗ ERROR:{NC} {str(e)}")
        tests_failed += 1
        return None


def main():
    global tests_passed, tests_failed

    print_header("MFA (Multi-Factor Authentication) Test Suite")

    # Test 1: User Registration
    print_section("1. User Registration")

    register_response = test_endpoint(
        "Register new user",
        "POST",
        "/auth/register",
        data={"email": TEST_EMAIL, "password": TEST_PASSWORD, "full_name": TEST_NAME},
        expected_status=201,
    )

    if not register_response:
        print(f"{RED}Registration failed, cannot continue{NC}")
        sys.exit(1)

    # Test 2: Initial Login
    print_section("2. Initial Login (No MFA)")

    login_response = test_endpoint(
        "Login without MFA enabled",
        "POST",
        "/auth/login",
        data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        expected_status=200,
    )

    if not login_response:
        print(f"{RED}Login failed, cannot continue{NC}")
        sys.exit(1)

    login_data = login_response.json()
    access_token = login_data.get("access_token")

    if not access_token:
        print(f"{RED}Could not extract access token{NC}")
        sys.exit(1)

    print(f"\n{GREEN}✓ Access token obtained{NC}")
    headers = {"Authorization": f"Bearer {access_token}"}

    # Test 3: Setup MFA
    print_section("3. MFA Setup")

    setup_response = test_endpoint(
        "Setup MFA (generate secret and backup codes)",
        "POST",
        "/auth/mfa/setup",
        headers=headers,
        expected_status=200,
    )

    if not setup_response:
        print(f"{RED}MFA setup failed, cannot continue{NC}")
        sys.exit(1)

    setup_data = setup_response.json()
    mfa_secret = setup_data.get("secret")
    backup_codes = setup_data.get("backup_codes")

    if not mfa_secret:
        print(f"{RED}Could not extract MFA secret{NC}")
        sys.exit(1)

    print(f"\n{GREEN}✓ MFA Secret obtained: {mfa_secret}{NC}")
    print(f"{GREEN}✓ Backup codes obtained: {len(backup_codes)} codes{NC}")

    # Save first backup code for later testing
    first_backup_code = backup_codes[0] if backup_codes else None

    # Test 4: Enable MFA with valid TOTP code
    print_section("4. Enable MFA")

    # Generate valid TOTP code
    totp = pyotp.TOTP(mfa_secret)
    valid_code = totp.now()

    print(f"{BLUE}Generated TOTP code: {valid_code}{NC}")

    enable_response = test_endpoint(
        "Enable MFA with valid TOTP code",
        "POST",
        "/auth/mfa/enable",
        data={"code": valid_code},
        headers=headers,
        expected_status=200,
    )

    if not enable_response:
        print(f"{RED}MFA enable failed{NC}")
        # Try to continue anyway for remaining tests
    else:
        print(f"\n{GREEN}✓ MFA successfully enabled{NC}")

    # Test 5: Test invalid TOTP code on enable (should already be enabled)
    print_section("5. Test Invalid Operations")

    test_endpoint(
        "Try to enable MFA again (should fail - already enabled)",
        "POST",
        "/auth/mfa/enable",
        data={"code": "123456"},
        headers=headers,
        expected_status=400,
    )

    # Test 6: Logout
    print_section("6. Logout")

    test_endpoint(
        "Logout user", "POST", "/auth/logout", headers=headers, expected_status=200
    )

    # Test 7: Login with MFA enabled (should require MFA)
    print_section("7. Login with MFA Enabled")

    mfa_login_response = test_endpoint(
        "Login with MFA enabled (should return temp token)",
        "POST",
        "/auth/login",
        data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        expected_status=200,
    )

    if not mfa_login_response:
        print(f"{RED}MFA login failed{NC}")
        sys.exit(1)

    mfa_login_data = mfa_login_response.json()
    requires_mfa = mfa_login_data.get("requires_mfa")
    temp_token = mfa_login_data.get("access_token")

    if requires_mfa:
        print(f"\n{GREEN}✓ MFA required as expected{NC}")
    else:
        print(f"\n{RED}✗ MFA not required (expected requires_mfa=true){NC}")

    # Test 8: Complete MFA verification with TOTP
    print_section("8. MFA Verification with TOTP")

    # Generate new TOTP code
    valid_code = totp.now()
    print(f"{BLUE}Generated TOTP code: {valid_code}{NC}")

    temp_headers = {"Authorization": f"Bearer {temp_token}"}

    mfa_verify_response = test_endpoint(
        "Verify MFA with valid TOTP code",
        "POST",
        "/auth/mfa/verify",
        data={"code": valid_code},
        headers=temp_headers,
        expected_status=200,
    )

    if not mfa_verify_response:
        print(f"{RED}MFA verification failed{NC}")
        sys.exit(1)

    verify_data = mfa_verify_response.json()
    full_access_token = verify_data.get("access_token")

    print(f"\n{GREEN}✓ Full access token obtained after MFA verification{NC}")

    # Test 9: Test backup code
    print_section("9. Backup Code Verification")

    # Logout again
    full_headers = {"Authorization": f"Bearer {full_access_token}"}
    test_endpoint(
        "Logout user", "POST", "/auth/logout", headers=full_headers, expected_status=200
    )

    # Login again to get temp token
    login_response2 = test_endpoint(
        "Login again for backup code test",
        "POST",
        "/auth/login",
        data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        expected_status=200,
    )

    if login_response2:
        temp_token2 = login_response2.json().get("access_token")
        temp_headers2 = {"Authorization": f"Bearer {temp_token2}"}

        # Try backup code
        if first_backup_code:
            print(f"{BLUE}Using backup code: {first_backup_code}{NC}")

            backup_verify_response = test_endpoint(
                "Verify MFA with backup code",
                "POST",
                "/auth/mfa/verify",
                data={"code": first_backup_code},
                headers=temp_headers2,
                expected_status=200,
            )

            if backup_verify_response:
                print(f"\n{GREEN}✓ Backup code verified successfully{NC}")

                # Try to use the same backup code again (should fail)
                backup_token = backup_verify_response.json().get("access_token")

                # Logout and login again
                test_endpoint(
                    "Logout after backup code use",
                    "POST",
                    "/auth/logout",
                    headers={"Authorization": f"Bearer {backup_token}"},
                    expected_status=200,
                )

                login_response3 = requests.post(
                    f"{API_URL}/auth/login",
                    json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
                ).json()

                temp_token3 = login_response3.get("access_token")

                test_endpoint(
                    "Try to reuse backup code (should fail)",
                    "POST",
                    "/auth/mfa/verify",
                    data={"code": first_backup_code},
                    headers={"Authorization": f"Bearer {temp_token3}"},
                    expected_status=401,
                )

    # Test 10: Disable MFA
    print_section("10. Disable MFA")

    # Get a fresh access token
    login_final = requests.post(
        f"{API_URL}/auth/login", json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    ).json()

    temp_token_final = login_final.get("access_token")
    valid_code_final = totp.now()

    # Complete MFA verification
    verify_final_response = requests.post(
        f"{API_URL}/auth/mfa/verify",
        json={"code": valid_code_final},
        headers={"Authorization": f"Bearer {temp_token_final}"},
    )

    if verify_final_response.status_code != 200:
        print(
            f"{RED}Failed to verify MFA for disable test: {verify_final_response.text}{NC}"
        )
        tests_failed += 1
        # Test Summary anyway
        print_header("Test Summary")
        print(f"Tests Passed: {GREEN}{tests_passed}{NC}")
        print(f"Tests Failed: {RED}{tests_failed}{NC}")
        return 1

    verify_final = verify_final_response.json()
    final_access_token = verify_final.get("access_token")
    final_headers = {"Authorization": f"Bearer {final_access_token}"}

    # Now disable MFA
    valid_code_disable = totp.now()

    test_endpoint(
        "Disable MFA with valid TOTP code",
        "POST",
        "/auth/mfa/disable",
        data={"code": valid_code_disable},
        headers=final_headers,
        expected_status=200,
    )

    # Test 11: Verify MFA is disabled
    print_section("11. Verify MFA Disabled")

    test_endpoint(
        "Logout after MFA disable",
        "POST",
        "/auth/logout",
        headers=final_headers,
        expected_status=200,
    )

    final_login = test_endpoint(
        "Login after MFA disabled (should not require MFA)",
        "POST",
        "/auth/login",
        data={"email": TEST_EMAIL, "password": TEST_PASSWORD},
        expected_status=200,
    )

    if final_login:
        final_data = final_login.json()
        if not final_data.get("requires_mfa"):
            print(f"\n{GREEN}✓ MFA successfully disabled - login works without MFA{NC}")
        else:
            print(f"\n{RED}✗ MFA still required after disable{NC}")

    # Test Summary
    print_header("Test Summary")
    print(f"Tests Passed: {GREEN}{tests_passed}{NC}")
    print(f"Tests Failed: {RED}{tests_failed}{NC}")
    print()

    if tests_failed == 0:
        print(f"{GREEN}✓ All MFA tests passed!{NC}")
        return 0
    else:
        print(f"{RED}✗ Some MFA tests failed{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
