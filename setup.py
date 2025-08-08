#!/usr/bin/env python
"""
Setup script for AI Research Platform
Quick database initialization and environment validation
"""

import os
import sqlite3
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories."""
    dirs = ['data', 'logs']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✓ Created directory: {dir_name}")


def initialize_database():
    """Initialize SQLite database with schema."""
    db_path = "ai_research_platform.db"
    schema_path = "src/db/schema.sql"
    
    if not Path(schema_path).exists():
        print(f"❌ Schema file not found: {schema_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            with open(schema_path, 'r') as f:
                conn.executescript(f.read())
        print(f"✓ Database initialized: {db_path}")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def check_environment():
    """Check environment file and required variables."""
    env_file = ".env"
    example_file = ".env.example"
    
    if not Path(env_file).exists():
        if Path(example_file).exists():
            print(f"⚠️  Please copy {example_file} to {env_file} and configure your API keys")
        else:
            print(f"❌ Environment file not found: {env_file}")
        return False
    
    print(f"✓ Environment file found: {env_file}")
    
    # Check for required variables
    required_vars = [
        "OPENROUTER_API_KEY",
        "LANGCHAIN_API_KEY"
    ]
    
    missing_vars = []
    try:
        with open(env_file, 'r') as f:
            env_content = f.read()
            for var in required_vars:
                if f"{var}=your_" in env_content or f"{var}=" in env_content and "your_" in env_content:
                    missing_vars.append(var)
    except Exception as e:
        print(f"❌ Error reading environment file: {e}")
        return False
    
    if missing_vars:
        print(f"⚠️  Please configure these API keys in {env_file}:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✓ Environment configuration looks good")
    return True


def main():
    """Main setup function."""
    print("🚀 Setting up AI Research Platform...")
    print()
    
    # Create directories
    create_directories()
    print()
    
    # Initialize database
    if not initialize_database():
        sys.exit(1)
    print()
    
    # Check environment
    env_ok = check_environment()
    print()
    
    if env_ok:
        print("✅ Setup complete! You can now run:")
        print("   python src/api/main.py")
        print()
        print("📊 API will be available at:")
        print("   http://localhost:8000")
        print("   http://localhost:8000/docs (API documentation)")
    else:
        print("⚠️  Setup incomplete. Please configure your environment file.")
        sys.exit(1)


if __name__ == "__main__":
    main()