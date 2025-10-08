#!/usr/bin/env python3
import os
import shutil

print("🧹 Ignition Stack Builder - Repository Cleanup")
print("=" * 50)
print()

repo_path = "/git/ignition-stack-builder"
os.chdir(repo_path)

# Create directory structure
print("📁 Creating documentation structure...")
os.makedirs("docs/testing", exist_ok=True)
os.makedirs("docs/planning", exist_ok=True)
os.makedirs("docs/guides", exist_ok=True)
print("✓ Directories created")
print()

# Testing documentation files
testing_docs = [
    "AUTOMATED_CODE_VERIFICATION.md",
    "AUTOMATED_TEST_RESULTS.md",
    "COMPLETE_TEST_STATUS.md",
    "EXTENDED_TESTS_COMPLETE.md",
    "FINAL_TEST_SUMMARY.md",
    "NEW_FEATURES_TESTING.md",
    "OPTIONAL_TESTS_COMPLETE.md",
    "SESSION5_TESTING_SUMMARY.md",
    "TEST_EXECUTION_RESULTS.md",
    "TEST_PLAN.md",
    "TEST_RESULTS.md",
    "TEST_RESULTS_NEW_FEATURES.md",
    "TRACK1_CODE_VERIFIED_RESULTS.md",
    "TRACK1_MANUAL_TEST_GUIDE.md",
    "TRACK1_MANUAL_TEST_RESULTS.md",
    "TRACK1_TESTING_STATUS.md",
    "ADVANCED_TESTS_EXECUTION.md",
    "ADVANCED_TESTS_SUMMARY.md",
    "REMAINING_TESTS_ASSESSMENT.md",
]

# Planning documentation files
planning_docs = [
    "CONTINUITY.md",
    "INTEGRATION_PLAN.md",
    "NEXT_PHASES.md",
    "PHASE2_STATUS.md",
    "PHASE3_PLAN.md",
    "PROJECT_STATUS.md",
]

# User guide files
guide_docs = [
    "USER_VERIFICATION_GUIDE.md",
    "FEATURES.md",
]

print("Moving testing documentation...")
moved_testing = 0
for doc in testing_docs:
    if os.path.exists(doc):
        shutil.move(doc, f"docs/testing/{doc}")
        print(f"  ✓ {doc}")
        moved_testing += 1
print(f"✓ Moved {moved_testing} testing documents")
print()

print("Moving planning documentation...")
moved_planning = 0
for doc in planning_docs:
    if os.path.exists(doc):
        shutil.move(doc, f"docs/planning/{doc}")
        print(f"  ✓ {doc}")
        moved_planning += 1
print(f"✓ Moved {moved_planning} planning documents")
print()

print("Moving user guides...")
moved_guides = 0
for doc in guide_docs:
    if os.path.exists(doc):
        shutil.move(doc, f"docs/guides/{doc}")
        print(f"  ✓ {doc}")
        moved_guides += 1
print(f"✓ Moved {moved_guides} user guides")
print()

print("=" * 50)
print("✅ Documentation organized!")
print()
print("📊 Repository Structure:")
print(f"  - docs/testing/   ({moved_testing} test reports)")
print(f"  - docs/planning/  ({moved_planning} planning docs)")
print(f"  - docs/guides/    ({moved_guides} user guides)")
print()
print("📄 Root directory files:")
print("  - README.md")
print("  - LICENSE")
print("  - CHANGELOG.md")
print("  - CRITICAL_BUG_FOUND.md (important for users)")
print()
print("✅ Cleanup complete! Ready for GitHub.")
