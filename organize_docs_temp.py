#!/usr/bin/env python3
import os
import shutil
import subprocess

repo_path = "/git/ignition-stack-builder"
os.chdir(repo_path)

# Create directory structure
os.makedirs("docs/testing", exist_ok=True)
os.makedirs("docs/planning", exist_ok=True)
os.makedirs("docs/guides", exist_ok=True)

# Files to move to docs/testing/
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
]

# Files to move to docs/planning/
planning_docs = [
    "CONTINUITY.md",
    "INTEGRATION_PLAN.md",
    "NEXT_PHASES.md",
    "PHASE2_STATUS.md",
    "PHASE3_PLAN.md",
    "PROJECT_STATUS.md",
]

# Files to move to docs/guides/
guide_docs = [
    "USER_VERIFICATION_GUIDE.md",
    "FEATURES.md",
]

print("📁 Organizing documentation...")
print()

# Move testing docs
moved_count = 0
for doc in testing_docs:
    if os.path.exists(doc):
        shutil.move(doc, f"docs/testing/{doc}")
        print(f"✓ {doc} → docs/testing/")
        moved_count += 1

# Move planning docs
for doc in planning_docs:
    if os.path.exists(doc):
        shutil.move(doc, f"docs/planning/{doc}")
        print(f"✓ {doc} → docs/planning/")
        moved_count += 1

# Move guide docs
for doc in guide_docs:
    if os.path.exists(doc):
        shutil.move(doc, f"docs/guides/{doc}")
        print(f"✓ {doc} → docs/guides/")
        moved_count += 1

print()
print(f"✅ Moved {moved_count} documentation files")
print()

# Clean up the temp script
os.remove("organize_docs_temp.py")
print("✅ Cleanup complete!")
