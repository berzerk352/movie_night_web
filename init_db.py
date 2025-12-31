#!/usr/bin/env python3
"""Database initialization script for Movie Night Web."""

import sys
from app import app
from database import init_db, seed_db, reset_db


def main():
    """Main initialization function."""
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        print("⚠️  WARNING: This will delete all existing data!")
        response = input("Are you sure you want to reset the database? (yes/no): ")
        if response.lower() == 'yes':
            print("Resetting database...")
            reset_db(app)
            print("✓ Database reset complete!")
            print("\nSeeding initial data...")
            seed_db(app)
            print("✓ Database seeded!")
        else:
            print("Reset cancelled.")
            return
    else:
        print("Initializing database...")
        init_db(app)
        print("✓ Database tables created!")
        
        print("\nSeeding initial data...")
        seed_db(app)
        print("✓ Database seeded!")
    
    print("\n🎉 Database setup complete!")
    print("\nYou can now run the application with:")
    print("  uv run python app.py")


if __name__ == '__main__':
    main()
