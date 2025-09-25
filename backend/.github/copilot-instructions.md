# EasySSH Backend - AI Coding Assistant Instructions

## Project Architecture Overview

This is a Django REST API backend with a custom directory structure that differs from standard Django patterns:

- **Core Configuration**: `core/` contains Django settings, main URLs, custom middleware, and authentication handlers
- **Apps Structure**: All Django apps live under `apps/` directory (added to `sys.path` in settings)
- **Utilities**: Shared utilities in `utils/` directory (also added to `sys.path`)
- **Custom App Pattern**: The main business logic is in the `common` app under `apps/common/`

## Key Development Patterns

### Controller-Based Architecture
This project uses a controller pattern instead of standard Django views:
- Controllers are organized in `apps/common/controllers/` by feature (Authentication, Common, PlatformApi)
- Example: `LoginController.py` contains both serializer and APIView classes in one file
- Controllers inherit from DRF's `APIView` and use `@swagger_auto_schema` for API documentation

### Model Organization
- Base models in `apps/common/models/Base.py` provide common fields (`BaseModel` with timestamps and soft delete)
- Feature-specific models are separate files (e.g., `Profile.py`, `PlatformApi.py`)
- Models use Django signals for automatic profile creation (`@receiver(post_save, sender=User)`)

### Routing Pattern
The project uses a dual-router system:
- Main routes in `apps/common/urls.py` combine DefaultRouter with explicit path patterns
- Secondary router in `apps/common/routers/RouterEnvelop.py` for platform API endpoints
- URL pattern: `api/v1/` prefix for all endpoints

### Authentication System
Implements multiple authentication methods simultaneously:
1. **JWT Authentication**: Using `rest_framework_simplejwt` with very long token lifetime (99999 days)
2. **Platform API Token**: Custom `X-API-KEY` header authentication via `PlatformApiTokenAuthentication`
3. **Session Authentication**: Standard Django session auth

### Environment & Configuration
- Uses `python-dotenv` for environment variables
- Conditional database setup: PostgreSQL if `DATABASE_DRIVER=postgres`, otherwise SQLite
- Swagger UI enabled when `SWAGGER_UI=true`

## Development Workflow

### Running the Application
```bash
make run          # Starts server on 0.0.0.0:8000 (or ENV vars HOST:PORT)
make migrate      # Runs migrations for both Django and common app
make shell        # Django shell
make test         # Run tests
```

### Code Quality
```bash
make format       # Auto-formats with black and autoflake
make lint         # Lints with flake8 (ignores E501, allows F401/F403 in __init__.py)
make clean        # Removes __pycache__, .pyc files, and migration files
```

### Docker Development
- Use `docker compose up -d --build --force-recreate` for clean rebuilds
- Volumes mount to `/var/esign/` for persistence (logs, media, database)

## Custom Middleware & Utilities

### Middleware Stack (in order)
1. `CsrfExemptMiddleware` - Disables CSRF for all requests
2. `HandleErrorsMiddleware` - Converts errors to JSON responses
3. Standard Django middleware stack

### Utility Functions
- `utils.Microfunctions.is_valid_email()` - Email validation with regex
- Controllers can authenticate by email or username (see `LoginController.py`)

## File Storage & Media
- Local media storage in `media/` directory
- Profile-related file uploads handled through Django's default file storage

## API Documentation
- Uses `drf-yasg` for Swagger/OpenAPI documentation
- Custom schema generator: `core.schema.CustomSchemaGenerator`
- Bearer token and X-API-KEY authentication in Swagger UI

## Project-Specific Conventions

### Import Patterns
```python
# Controllers import from utils directly (utils/ in sys.path)
from utils.Microfunctions import is_valid_email

# Apps import with apps prefix
from apps.common.models import APITokenModel
```

### Error Handling
- Middleware automatically converts Django errors to JSON
- Custom error messages for 401 (Authentication required), 403 (Authorization required), 404 (Resource not found)
- Detailed error logging with `loguru` logger

### Model Conventions
- All models inherit from `BaseModel` for timestamp and soft delete functionality
- Use Django's built-in User model with OneToOne profile extension
- Signal-based automatic profile creation on user registration
- Profile model contains user-specific data and preferences

When working on this codebase:
1. Follow the controller pattern for new endpoints
2. Add new routes to both main `urls.py` and appropriate router files
3. Use the custom authentication classes for API endpoints
4. Inherit from `BaseModel` for new models needing timestamps
5. Use the existing middleware for consistent error handling
6. Test with both JWT and X-API-KEY authentication methods