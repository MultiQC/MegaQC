#!/usr/bin/env bash

# MegaQC Development Setup Script
# This script helps set up the development environment

set -e

echo "🚀 Setting up MegaQC development environment..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this from the MegaQC root directory."
    exit 1
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U megaqc_user; do
    echo "Waiting for postgres..."
    sleep 2
done
echo "✅ PostgreSQL is ready!"

# Install Python dependencies
echo "📦 Installing Python dependencies with uv..."
if command -v uv &> /dev/null; then
    uv pip install --system -e .[dev]
else
    echo "⚠️  uv not found, falling back to pip..."
    pip install -e .[dev]
fi

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Build frontend assets
echo "🔨 Building frontend assets..."
npm run build

# Initialize database
echo "🗄️  Initializing database..."
export MEGAQC_PRODUCTION=0
export DB_HOST=postgres
export DB_NAME=megaqc_dev
export DB_USER=megaqc_user
export DB_PASS=megaqc_dev_password

python -m megaqc initdb

echo ""
echo "🎉 Setup complete! You can now:"
echo ""
echo "   Start the development server:"
echo "   $ FLASK_ENV=development FLASK_DEBUG=1 python -m megaqc.cli run"
echo ""
echo "   Watch frontend changes:"
echo "   $ npm run watch"
echo ""
echo "   Run tests:"
echo "   $ uv run pytest"
echo ""
echo "   Access the application at http://localhost:5000"
echo "" 