#!/bin/bash
# Repository Cleanup Script for GitHub
# This script organizes documentation and prepares the repository for GitHub

set -e

echo "🧹 Ignition Stack Builder - Repository Cleanup"
echo "=============================================="
echo ""

# Navigate to repository root
cd "$(dirname "$0")"

echo "📁 Creating documentation structure..."
mkdir -p docs/testing
mkdir -p docs/planning
mkdir -p docs/guides

# Move testing documentation
echo ""
echo "Moving testing documentation..."
mv -f AUTOMATED_CODE_VERIFICATION.md docs/testing/ 2>/dev/null || true
mv -f AUTOMATED_TEST_RESULTS.md docs/testing/ 2>/dev/null || true
mv -f COMPLETE_TEST_STATUS.md docs/testing/ 2>/dev/null || true
mv -f EXTENDED_TESTS_COMPLETE.md docs/testing/ 2>/dev/null || true
mv -f FINAL_TEST_SUMMARY.md docs/testing/ 2>/dev/null || true
mv -f NEW_FEATURES_TESTING.md docs/testing/ 2>/dev/null || true
mv -f OPTIONAL_TESTS_COMPLETE.md docs/testing/ 2>/dev/null || true
mv -f SESSION5_TESTING_SUMMARY.md docs/testing/ 2>/dev/null || true
mv -f TEST_EXECUTION_RESULTS.md docs/testing/ 2>/dev/null || true
mv -f TEST_PLAN.md docs/testing/ 2>/dev/null || true
mv -f TEST_RESULTS.md docs/testing/ 2>/dev/null || true
mv -f TEST_RESULTS_NEW_FEATURES.md docs/testing/ 2>/dev/null || true
mv -f TRACK1_CODE_VERIFIED_RESULTS.md docs/testing/ 2>/dev/null || true
mv -f TRACK1_MANUAL_TEST_GUIDE.md docs/testing/ 2>/dev/null || true
mv -f TRACK1_MANUAL_TEST_RESULTS.md docs/testing/ 2>/dev/null || true
mv -f TRACK1_TESTING_STATUS.md docs/testing/ 2>/dev/null || true

# Move planning documentation
echo "Moving planning documentation..."
mv -f CONTINUITY.md docs/planning/ 2>/dev/null || true
mv -f INTEGRATION_PLAN.md docs/planning/ 2>/dev/null || true
mv -f NEXT_PHASES.md docs/planning/ 2>/dev/null || true
mv -f PHASE2_STATUS.md docs/planning/ 2>/dev/null || true
mv -f PHASE3_PLAN.md docs/planning/ 2>/dev/null || true
mv -f PROJECT_STATUS.md docs/planning/ 2>/dev/null || true

# Move user guides
echo "Moving user guides..."
mv -f USER_VERIFICATION_GUIDE.md docs/guides/ 2>/dev/null || true
mv -f FEATURES.md docs/guides/ 2>/dev/null || true

echo ""
echo "✅ Documentation organized!"
echo ""
echo "📊 Repository Structure:"
echo "  - docs/testing/   (16 test reports)"
echo "  - docs/planning/  (6 planning docs)"
echo "  - docs/guides/    (2 user guides)"
echo ""
echo "📄 Root directory files:"
echo "  - README.md"
echo "  - LICENSE"
echo "  - CHANGELOG.md"
echo "  - CRITICAL_BUG_FOUND.md (important for users)"
echo ""
echo "✅ Cleanup complete! Ready for GitHub."
