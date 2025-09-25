# EasySSH Backend - AI Coding Assistant Instructions

## Project Architecture Overview

This Django REST API backend uses a custom directory structure with:

- **Core Configuration**: `core/` - Django settings, URLs, middleware, and authentication
- **Apps Structure**: `apps/` - All Django apps (added to `sys.path`)
- **Utilities**: `utils/` - Shared utilities (added to `sys.path`)
- **Virtual Environment**: `.venv/` - Python executable at `.venv/bin/python3`

## Key Development Patterns

### Controller-Based Architecture
- Controllers replace standard Django views in `apps/common/controllers/`
- Organized by feature: Authentication, Common, PlatformApi
- Each controller contains serializers and APIView classes
- Use `@swagger_auto_schema` for API documentation

### Authentication System
1. **JWT Authentication**: `rest_framework_simplejwt` with 99999-day token lifetime
2. **Platform API Token**: Custom `X-API-KEY` header authentication
3. **Session Authentication**: Standard Django session auth

### Models & Database
- All models inherit from `BaseModel` (timestamps + soft delete)
- User profile with Django signals for auto-creation
- EasySSH models: Workspace, Vault, SSHCreds, SSHServers , PlatformAPI .
- PostgreSQL (production) / SQLite (development)

## Development Commands

### AI Development (Use these in automated tasks)
```bash
# Virtual environment setup
uv venv .venv                           # Create virtual environment with UV
source .venv/bin/activate               # Activate virtual environment
uv sync                                 # Install dependencies from uv.lock

# Package management
uv add <package_name>                   # Add new package
uv remove <package_name>                # Remove package

# Application management
python3 ./manage.py runserver 0.0.0.0:8000  # Start development server
python3 ./manage.py migrate                  # Run Django migrations
python3 ./manage.py migrate common           # Run app-specific migrations
python3 ./manage.py shell                    # Django shell
python3 ./manage.py test                     # Run tests
python3 ./manage.py collectstatic --noinput # Collect static files

# Code quality
python3 -m black .                      # Auto-format code with black
python3 -m autoflake --remove-all-unused-imports --in-place --recursive .  # Remove unused imports
python3 -m flake8 . --ignore=E501 --per-file-ignores="*/__init__.py:F401,F403"  # Lint code
```

### Human Developer Commands (Reference only)
```bash
make run          # Starts server on 0.0.0.0:8000
make migrate      # Runs migrations
make shell        # Django shell
make test         # Run tests
make format       # Auto-formats with black and autoflake
make lint         # Lints with flake8
make clean        # Removes cache files
```

## Key Conventions

### Import Patterns
```python
# Utils are in sys.path
from utils.Microfunctions import is_valid_email
from common.models import APITokenModel
```

### Middleware Stack
1. `CsrfExemptMiddleware` - Disables CSRF
2. `HandleErrorsMiddleware` - JSON error responses
3. Standard Django middleware

### Error Handling
- Automatic JSON error conversion via middleware
- Custom messages: 401 (Authentication required), 403 (Authorization required), 404 (Resource not found)
- Loguru logging integration

## EasySSH Models & Relationships

### Core Models
- **WorkspaceModel**: User organization unit for grouping environments
- **VaultModel**: Device/environment containers within workspaces
- **SSHCredsModel**: SSH key pair management for authentication
- **SSHServersModel**: SSH server configurations with vault associations
- **APITokenModel**: Enhanced platform API tokens with policy support

### Model Relationships
```
User (Django built-in)
├── WorkspaceModel (1:N) - User can have multiple workspaces
├── VaultModel (1:N) - User can have multiple vaults  
├── SSHCredsModel (1:N) - User can have multiple SSH credentials
├── SSHServersModel (1:N) - User can have multiple SSH servers
└── APITokenModel (1:N) - User can have multiple API tokens

WorkspaceModel
└── VaultModel (1:N) - Workspace can contain multiple vaults

VaultModel  
└── SSHServersModel (1:N) - Vault can contain multiple SSH servers

SSHCredsModel
└── SSHServersModel (1:N) - Credentials can be used by multiple servers
```

### Field Highlights
- **UUID Primary Keys**: All models use UUID for primary keys
- **JSON Fields**: Metadata (VaultModel), Policy (APITokenModel)
- **Soft Delete**: All models inherit BaseModel soft delete functionality
- **Timestamps**: Automatic created_at, updated_at, deleted_at tracking

## Project Structure Overview

```
├── .github/
│   └── copilot-instructions.md      # AI assistant coding guidelines and project documentation
├── .vscode/
│   ├── launch.json                  # VS Code debug configuration
│   └── settings.json                # VS Code workspace settings
├── apps/                            # Django applications directory (added to sys.path)
│   └── common/                      # Main business logic application
│       ├── admin/                   # Django admin customizations
│       │   ├── PlatformAPI.py       # Admin interface for platform API tokens (enhanced with policy)
│       │   ├── Profile.py           # Admin interface for user profiles
│       │   ├── Workspace.py         # Admin interface for workspaces
│       │   ├── Vault.py             # Admin interface for vaults
│       │   ├── SSHCreds.py          # Admin interface for SSH credentials
│       │   ├── SSHServers.py        # Admin interface for SSH servers
│       │   └── __init__.py          # Admin module initialization
│       ├── controllers/             # Controller-based architecture (replaces views)
│       │   ├── Authentication/      # Authentication-related controllers
│       │   │   ├── LoginController.py      # Login endpoint and serializers
│       │   │   └── RegistrationController.py # User registration logic
│       │   ├── Common/              # Common/shared controllers
│       │   │   └── ProfileController.py    # User profile management
│       │   └── PlatformApi/         # Platform API controllers
│       │       └── PlatformAPI.py   # Platform API token management
│       ├── migrations/              # Database migration files
│       │   ├── 0001_initial.py      # Initial database schema
│       │   └── __init__.py          # Migration module initialization
│       ├── models/                  # Django models
│       │   ├── Base.py              # BaseModel with timestamps and soft delete
│       │   ├── PlatformApi.py       # Platform API token model (enhanced with policy & is_active)
│       │   ├── Profile.py           # User profile model with signals
│       │   ├── Workspace.py         # Workspace model for user organization
│       │   ├── Vault.py             # Vault model for device/environment management
│       │   ├── SSHCreds.py          # SSH credentials model for key management
│       │   ├── SSHServers.py        # SSH servers model with vault relationships
│       │   └── __init__.py          # Model imports and initialization
│       ├── routers/                 # Custom routing logic
│       │   └── RouterEnvelop.py     # Secondary router for platform APIs
│       ├── __init__.py              # App initialization
│       ├── apps.py                  # Django app configuration
│       ├── tests.py                 # Unit tests for the common app
│       └── urls.py                  # Main URL routing with dual-router system
├── core/                            # Django core configuration
│   ├── helpers/                     # Core helper modules
│   │   ├── Authentications/         # Custom authentication classes
│   │   │   ├── PlatformApiToken.py  # X-API-KEY authentication handler
│   │   │   └── __init__.py          # Authentication module initialization
│   │   ├── HandlerLogGuru.py        # Loguru logging configuration
│   │   ├── Middleware.py            # Custom middleware (CSRF exempt, error handling)
│   │   └── __init__.py              # Helpers module initialization
│   ├── __init__.py                  # Core module initialization
│   ├── asgi.py                      # ASGI application configuration
│   ├── log_handler.py               # Logging handler setup
│   ├── schema.py                    # Custom Swagger/OpenAPI schema generator
│   ├── settings.py                  # Django settings with environment configuration
│   ├── urls.py                      # Main URL configuration with Swagger
│   └── wsgi.py                      # WSGI application configuration
├── db/                              # Database directory
│   ├── .gitignore                   # Database gitignore rules
│   └── db.sqlite3                   # SQLite database file (development)
├── logs/                            # Application logs directory
│   └── .gitignore                   # Logs gitignore rules
├── media/                           # User uploaded media files
│   └── .gitignore                   # Media gitignore rules
├── pipeline/                        # Docker and infrastructure configuration
│   ├── development/                 # Development environment configs
│   │   └── database/
│   │       └── compose.yml          # PostgreSQL development setup
│   ├── .gitignore                   # Pipeline gitignore rules
│   ├── pgadmin.yml                  # pgAdmin Docker configuration
│   └── redis.yml                    # Redis Docker configuration
├── static/                          # Static files (CSS, JS, images)
│   └── .gitignore                   # Static files gitignore rules
├── utils/                           # Shared utility functions (added to sys.path)
│   ├── ApiModel.py                  # API response models and utilities
│   └── Microfunctions.py            # Small utility functions (email validation, etc.)
├── .venv/                           # Virtual environment directory
│   ├── bin/
│   │   └── python3                  # Python executable for the project
│   ├── lib/                         # Installed packages and dependencies
│   └── pyvenv.cfg                   # Virtual environment configuration
├── .dockerignore                    # Docker build ignore rules
├── .env -> .env.sample              # Environment variables symlink
├── .env.sample                      # Environment variables template
├── .gitignore                       # Git ignore rules
├── .python-version                  # Python version specification
├── Dockerfile                       # Docker container configuration
├── Makefile                         # Development commands (run, migrate, format, lint)
├── README.md                        # Project documentation
├── TODO.md                          # Project todo list and roadmap
├── compose.yml                      # Docker Compose configuration
├── main.py                          # Alternative Django entry point
├── manage.py                        # Django management commands
├── pyproject.toml                   # Python project configuration and dependencies
└── uv.lock                          # UV package manager lock file
```

## Development Guidelines

When working on this codebase:

### Controllers & Views
- Follow controller pattern for new endpoints
- Controllers contain both serializers and APIView classes
- Use `@swagger_auto_schema` for API documentation
- Email/username authentication supported in login

### Models & Database
- Inherit from `BaseModel` for timestamps and soft delete
- User profiles auto-created via Django signals
- EasySSH models with proper relationships: User → Workspace → Vault → SSH Components
- Enhanced PlatformAPI with policy field and is_active status
- Dual-router system: main + platform API routes

### Authentication & Security
- Support JWT, X-API-KEY, and session authentication
- CSRF disabled globally via middleware
- Custom error handling with JSON responses

### Code Organization
- Controllers in `apps/common/controllers/` by feature
- Models in separate files with BaseModel inheritance
- Utils available directly (added to sys.path)
- API prefix: `api/v1/` for all endpoints