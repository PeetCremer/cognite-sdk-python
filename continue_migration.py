#!/usr/bin/env python3
"""
Requests to HTTPX Migration Helper Script

This script helps identify remaining work for migrating from requests to httpx
in the cognite-sdk-python project.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

def find_requests_imports(directory: str) -> List[Tuple[str, int, str]]:
    """Find all files that still import requests."""
    results = []
    pattern = re.compile(r'(import requests|from requests)', re.IGNORECASE)
    
    for root, dirs, files in os.walk(directory):
        # Skip test directories for now
        if 'test' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line):
                                results.append((filepath, line_num, line.strip()))
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return results

def find_response_type_annotations(directory: str) -> List[Tuple[str, int, str]]:
    """Find remaining requests.Response type annotations."""
    results = []
    # Look for type annotations that reference Response but not httpx.Response
    pattern = re.compile(r'-> Response[:\s]|: Response[,\s\]]', re.IGNORECASE)
    
    for root, dirs, files in os.walk(directory):
        # Skip test directories for now
        if 'test' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line) and 'httpx.Response' not in line:
                                results.append((filepath, line_num, line.strip()))
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return results

def find_requests_utils_usage(directory: str) -> List[Tuple[str, int, str]]:
    """Find usage of requests.utils functions."""
    results = []
    pattern = re.compile(r'requests\.utils\.', re.IGNORECASE)
    
    for root, dirs, files in os.walk(directory):
        if 'test' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if pattern.search(line):
                                results.append((filepath, line_num, line.strip()))
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return results

def analyze_migration_status():
    """Analyze the current migration status."""
    print("🔍 Analyzing Requests to HTTPX Migration Status\n")
    
    cognite_dir = "cognite"
    
    if not os.path.exists(cognite_dir):
        print("❌ Error: cognite directory not found. Please run this script from the project root.")
        return
    
    print("1. Checking for remaining requests imports...")
    requests_imports = find_requests_imports(cognite_dir)
    if requests_imports:
        print(f"   ⚠️  Found {len(requests_imports)} files with requests imports:")
        for filepath, line_num, line in requests_imports:
            print(f"     {filepath}:{line_num} - {line}")
    else:
        print("   ✅ No requests imports found!")
    
    print("\n2. Checking for Response type annotations...")
    response_types = find_response_type_annotations(cognite_dir)
    if response_types:
        print(f"   ⚠️  Found {len(response_types)} Response type annotations to update:")
        for filepath, line_num, line in response_types:
            print(f"     {filepath}:{line_num} - {line}")
    else:
        print("   ✅ No requests.Response type annotations found!")
    
    print("\n3. Checking for requests.utils usage...")
    utils_usage = find_requests_utils_usage(cognite_dir)
    if utils_usage:
        print(f"   ⚠️  Found {len(utils_usage)} requests.utils usages:")
        for filepath, line_num, line in utils_usage:
            print(f"     {filepath}:{line_num} - {line}")
    else:
        print("   ✅ No requests.utils usage found!")
    
    # Summary
    total_issues = len(requests_imports) + len(response_types) + len(utils_usage)
    print(f"\n📊 Summary:")
    print(f"   Total issues to fix: {total_issues}")
    
    if total_issues == 0:
        print("   🎉 Core migration appears complete!")
    else:
        print("   ⚡ Next steps:")
        if requests_imports:
            print("     - Update requests imports to httpx")
        if response_types:
            print("     - Fix Response type annotations")
        if utils_usage:
            print("     - Replace requests.utils with httpx equivalents")
    
    print("\n🔧 Additional migration steps still needed:")
    print("   - Update test infrastructure (responses → httpx mocking)")
    print("   - Migrate OAuth (requests_oauthlib → authlib)")
    print("   - Update Pyodide compatibility layer")
    print("   - Run full test suite validation")

if __name__ == "__main__":
    analyze_migration_status()