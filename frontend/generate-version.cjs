#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

try {
  // Get git commit count (acts as build number)
  const commitCount = execSync('git rev-list --count HEAD', { encoding: 'utf-8' }).trim();

  // Get short commit hash
  const commitHash = execSync('git rev-parse --short HEAD', { encoding: 'utf-8' }).trim();

  // Get commit date
  const commitDate = execSync('git log -1 --format=%cd --date=short', { encoding: 'utf-8' }).trim();

  // Get current branch
  const branch = execSync('git rev-parse --abbrev-ref HEAD', { encoding: 'utf-8' }).trim();

  // Generate version string: v{build}.{hash} (date)
  const version = `v1.0.${commitCount}`;
  const fullVersion = `${version}-${commitHash}`;

  // Create version object
  const versionInfo = {
    version: version,
    fullVersion: fullVersion,
    commitHash: commitHash,
    commitCount: commitCount,
    commitDate: commitDate,
    branch: branch,
    buildDate: new Date().toISOString()
  };

  // Write to version.json
  const outputPath = path.join(__dirname, 'public', 'version.json');
  fs.writeFileSync(outputPath, JSON.stringify(versionInfo, null, 2));

  console.log(`✅ Generated version: ${fullVersion}`);
  console.log(`   Commit: ${commitHash} (${commitDate})`);
  console.log(`   Build: ${commitCount}`);
  console.log(`   Branch: ${branch}`);

} catch (error) {
  console.warn('⚠️  Could not generate version from git, using fallback');

  // Fallback version if git is not available
  const versionInfo = {
    version: 'v1.0.0',
    fullVersion: 'v1.0.0-unknown',
    commitHash: 'unknown',
    commitCount: '0',
    commitDate: new Date().toISOString().split('T')[0],
    branch: 'unknown',
    buildDate: new Date().toISOString()
  };

  const outputPath = path.join(__dirname, 'public', 'version.json');
  fs.writeFileSync(outputPath, JSON.stringify(versionInfo, null, 2));

  console.log('Generated fallback version:', versionInfo.fullVersion);
}
