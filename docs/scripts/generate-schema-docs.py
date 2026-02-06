#!/usr/bin/env python3
"""
Generate human-readable HTML documentation from meltano.schema.json
using json-schema-for-humans.

This script is called during the docs build process to generate
schema documentation.

Usage:
    python3 scripts/generate-schema-docs.py

Requirements:
    pip install json-schema-for-humans==0.44.2
"""

import os
import subprocess
import sys
from pathlib import Path


def generate_schema_docs():
    """Generate schema documentation using json-schema-for-humans."""
    # Get paths
    docs_dir = Path(__file__).parent.parent
    repo_root = docs_dir.parent
    schema_path = repo_root / "src" / "meltano" / "schemas" / "meltano.schema.json"
    static_dir = docs_dir / "static" / "schema"
    
    # Ensure the static/schema directory exists
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if schema file exists
    if not schema_path.exists():
        print(f"Error: Schema file not found at {schema_path}", file=sys.stderr)
        sys.exit(1)
    
    # Check if json-schema-for-humans is installed
    try:
        import json_schema_for_humans
    except ImportError:
        print("Error: json-schema-for-humans is not installed.", file=sys.stderr)
        print("Please install it with: pip install json-schema-for-humans==0.44.2", file=sys.stderr)
        print("\nFor CI environments, you can skip schema generation by setting SKIP_SCHEMA_GENERATION=1", file=sys.stderr)
        sys.exit(1)
    
    # Generate the schema documentation
    output_file = static_dir / "index.html"
    
    cmd = [
        sys.executable, "-m", "json_schema_for_humans.generate",
        "--expand-buttons",
        "--minify",
        str(schema_path),
        str(output_file)
    ]
    
    print(f"Generating schema docs...")
    subprocess.check_call(cmd)
    
    print(f"Schema documentation generated successfully at {output_file}")


if __name__ == "__main__":
    # Allow skipping schema generation in environments where the package is not available
    if os.environ.get("SKIP_SCHEMA_GENERATION") == "1":
        print("Skipping schema generation (SKIP_SCHEMA_GENERATION=1)")
        sys.exit(0)
    generate_schema_docs()
