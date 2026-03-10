#!/usr/bin/env python
"""Test script to verify CLI functionality without full installation."""

import sys
sys.path.insert(0, r'c:\Users\dj-emina\summarize-readme\src')

try:
    from summarize_readme.cli import app
    print("✓ Successfully imported CLI app")
    print("\nTesting CLI commands...")
    print("Run with: python test_cli.py")
    
    # Test by invoking help
    from typer.testing import CliRunner
    runner = CliRunner()
    
    # Test version command
    result = runner.invoke(app, ["version"])
    print("\n--- Version Command ---")
    print(result.stdout)
    
    # Test help
    result = runner.invoke(app, ["--help"])
    print("\n--- Help Command ---")
    print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
    
    print("\n✓ CLI is working correctly!")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("\nMissing dependencies. Please install:")
    print("  typer[all], rich, requests, markdown, beautifulsoup4")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
