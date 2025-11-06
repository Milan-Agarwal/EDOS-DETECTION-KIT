#!/usr/bin/env python3
"""
Database initialization script for EDoS Security Dashboard
Run this script to set up the database and initial data
"""

import asyncio
import os
import sys

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import (
    initialize_database,
    check_database_connection,
    seed_initial_data,
)


async def main():
    """Main initialization function"""
    print("🚀 EDoS Security Dashboard - Database Initialization")
    print("=" * 60)

    # Check if database connection works
    print("1. Testing database connection...")
    if check_database_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
        print("\n📋 Make sure PostgreSQL is installed and running:")
        print("   • Ubuntu/Debian: sudo apt install postgresql postgresql-contrib")
        print("   • Run: sudo systemctl start postgresql")
        print("   • Create user: sudo -u postgres createuser -s edos_user")
        print(
            "   • Create database: sudo -u postgres createdb edos_security -O edos_user"
        )
        print(
            "   • Set password: sudo -u postgres psql -c \"ALTER USER edos_user PASSWORD 'edos_password';\""
        )
        return False

    # Initialize database
    print("\n2. Initializing database schema...")
    success = await initialize_database()

    if success:
        print("✅ Database initialization completed successfully!")
        print("\n📊 Database Summary:")
        print("   • User management: Registration, authentication, profiles")
        print("   • Cloud resources: AWS, Azure, GCP resource monitoring")
        print("   • Security alerts: Real-time threat detection and classification")
        print("   • Network traffic: 3D globe visualization data")
        print("   • System logs: Centralized logging with full-text search")
        print("   • Metrics: Resource utilization and performance monitoring")
        print("   • Multi-tenant: Row Level Security for data isolation")

        print("\n🔗 Connection Details:")
        print(
            f"   Database URL: {os.getenv('DATABASE_URL', 'postgresql://edos_user:edos_password@localhost:5432/edos_security')}"
        )

        print("\n▶️  Next Steps:")
        print(
            "   1. Start the backend: cd backend && uvicorn main:app --reload --port 8001"
        )
        print("   2. Start the frontend: npm run dev")
        print("   3. Visit: http://localhost:3000")

        return True
    else:
        print("❌ Database initialization failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
