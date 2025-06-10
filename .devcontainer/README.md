# MegaQC Development Container

This directory contains the configuration for a GitHub Codespaces / VS Code Dev Container setup for MegaQC development.

## What's Included

### Environment
- **Python 3.11** with uv package manager (preferred) and Poetry (fallback)
- **Node.js 18** for frontend development
- **PostgreSQL 15** database for realistic development
- **VS Code extensions** for Python, JavaScript, and web development

### Tools
- **uv** - Modern Python package manager (per project preferences)
- **Poetry** - Alternative Python dependency management
- **npm** - Node.js package management
- **PostgreSQL client** tools
- **GitHub CLI** for repository management

## Getting Started

### Using GitHub Codespaces
1. Go to your MegaQC repository on GitHub
2. Click the green "Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on main"

### Using VS Code Dev Containers
1. Install the "Dev Containers" extension in VS Code
2. Open the MegaQC repository folder
3. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
4. Select "Dev Containers: Reopen in Container"

## Development Workflow

### Starting the Application
```bash
# Development server (uses SQLite by default)
FLASK_ENV=development FLASK_DEBUG=1 python -m megaqc.cli run

# Or with PostgreSQL
MEGAQC_PRODUCTION=0 DB_HOST=postgres python -m megaqc.cli run
```

### Frontend Development
```bash
# Watch mode for frontend changes
npm run watch

# Build for production
npm run build
```

### Database Management
```bash
# Initialize database
python -m megaqc initdb

# Run migrations
flask db upgrade

# Create new migration
flask db migrate -m "Description of changes"
```

### Testing
```bash
# Run tests with uv
uv run pytest

# Run tests with specific module
uv run pytest tests/test_models.py

# Run with coverage
uv run pytest --cov=megaqc
```

## Environment Variables

The dev container sets up the following environment variables:

- `MEGAQC_PRODUCTION=0` - Enables development mode
- `FLASK_ENV=development` - Flask development environment
- `FLASK_DEBUG=1` - Enables Flask debug mode
- `DB_HOST=postgres` - PostgreSQL container hostname
- `DB_NAME=megaqc_dev` - Development database name
- `DB_USER=megaqc_user` - Database user
- `DB_PASS=megaqc_dev_password` - Database password

## Ports

- **5000** - Flask development server
- **8000** - Production server (gunicorn)
- **5432** - PostgreSQL database

## Volumes

- **postgres-data** - Persistent PostgreSQL data
- **megaqc-node-modules** - Node.js modules cache for better performance

## Customization

You can customize the dev container by modifying:

- `.devcontainer/devcontainer.json` - VS Code settings and extensions
- `.devcontainer/docker-compose.yml` - Services and environment configuration
- `.devcontainer/Dockerfile` - Container image and system dependencies

## Troubleshooting

### Database Connection Issues
If you can't connect to PostgreSQL:
```bash
# Check if PostgreSQL is running
pg_isready -h postgres -p 5432

# Reset database
docker-compose down -v
docker-compose up -d
```

### Python Package Issues
```bash
# Reinstall packages with uv
uv pip install --system -e .[dev] --force-reinstall

# Or with poetry
poetry install --with dev
```

### Frontend Build Issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
``` 