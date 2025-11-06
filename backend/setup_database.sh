#!/bin/bash

# EDoS Security Dashboard Database Setup Script
# This script installs PostgreSQL and initializes the database

echo "🚀 Setting up PostgreSQL database for EDoS Security Dashboard..."

# Check if PostgreSQL is installed
if ! command -v postgres &> /dev/null; then
    echo "📦 Installing PostgreSQL..."
    
    # Install PostgreSQL
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
    
    # Start PostgreSQL service
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    echo "✅ PostgreSQL installed successfully"
else
    echo "✅ PostgreSQL is already installed"
fi

# Configure PostgreSQL
echo "🔧 Configuring PostgreSQL..."

# Create database user and database
sudo -u postgres psql -c "CREATE USER edos_user WITH ENCRYPTED PASSWORD 'edos_password';" 2>/dev/null || true
sudo -u postgres psql -c "CREATE DATABASE edos_security OWNER edos_user;" 2>/dev/null || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE edos_security TO edos_user;" 2>/dev/null || true

# Allow local connections (modify pg_hba.conf)
PG_VERSION=$(sudo -u postgres psql -t -c "SELECT version();" | grep -oE '[0-9]+\.[0-9]+' | head -1)
PG_CONFIG_DIR="/etc/postgresql/${PG_VERSION}/main"

if [ -f "${PG_CONFIG_DIR}/pg_hba.conf" ]; then
    echo "📝 Updating PostgreSQL authentication configuration..."
    
    # Backup original config
    sudo cp "${PG_CONFIG_DIR}/pg_hba.conf" "${PG_CONFIG_DIR}/pg_hba.conf.backup"
    
    # Add local authentication for edos_user
    sudo sed -i "s/#local   all             all                                     peer/local   all             all                                     md5/" "${PG_CONFIG_DIR}/pg_hba.conf"
    
    # Restart PostgreSQL
    sudo systemctl restart postgresql
fi

echo "✅ PostgreSQL configuration completed"

# Test database connection
echo "🔍 Testing database connection..."
export PGPASSWORD='edos_password'
if psql -h localhost -U edos_user -d edos_security -c "SELECT 1;" &>/dev/null; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed. Please check the configuration."
    exit 1
fi

echo "🎉 Database setup completed successfully!"
echo ""
echo "📋 Database Details:"
echo "   Database: edos_security"
echo "   User: edos_user"
echo "   Password: edos_password"
echo "   Host: localhost"
echo "   Port: 5432"
echo ""
echo "🔗 Connection URL: postgresql://edos_user:edos_password@localhost:5432/edos_security"
echo ""
echo "▶️  Next steps:"
echo "   1. Run: cd backend && python app/database.py"
echo "   2. Start the backend: uvicorn app.main:app --reload --port 8001"
