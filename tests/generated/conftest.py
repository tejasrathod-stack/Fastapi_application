"""
pytest configuration for AI-generated tests.
Framework-specific setup with minimal dependencies.
"""

import os
import sys
import pytest
import warnings

# Suppress deprecation warnings during testing
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Set testing environment
os.environ.setdefault("TESTING", "true")
os.environ.setdefault("LOG_LEVEL", "ERROR")

# Add target project to Python path
TARGET_ROOT = os.environ.get("TARGET_ROOT", "/home/runner/work/Fastapi_application/Fastapi_application/pipeline/target_repo")
if TARGET_ROOT and TARGET_ROOT not in sys.path:
    sys.path.insert(0, TARGET_ROOT)

# Also add current directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============== FASTAPI-SPECIFIC CONFIGURATION ==============

import asyncio

# Try to import the FastAPI app
_fastapi_app = None
try:
    for module_name in ['main', 'app', 'api', 'server', 'application']:
        try:
            mod = __import__(module_name)
            if hasattr(mod, 'app'):
                _fastapi_app = mod.app
                break
            elif hasattr(mod, 'create_app'):
                _fastapi_app = mod.create_app()
                break
        except ImportError:
            continue
except Exception:
    pass


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app():
    """FastAPI application fixture (function-scoped for isolation)."""
    if _fastapi_app is None:
        pytest.skip("No FastAPI app found")
    return _fastapi_app


@pytest.fixture
def client(app):
    """FastAPI TestClient fixture."""
    try:
        from fastapi.testclient import TestClient
        return TestClient(app)
    except ImportError:
        from starlette.testclient import TestClient
        return TestClient(app)


@pytest.fixture
def async_client(app):
    """Async client for FastAPI."""
    try:
        from httpx import AsyncClient
        return AsyncClient(app=app, base_url="http://test")
    except ImportError:
        pytest.skip("httpx not installed for async testing")


@pytest.fixture
def sample_data():
    """Sample test data for FastAPI apps."""
    return {
        "title": "Test Item",
        "description": "Test Description",
        "name": "Test Name",
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "is_active": True,
    }


@pytest.fixture
def auth_headers():
    """Authorization headers for API testing."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer test-token",
    }


@pytest.fixture
def mock_db():
    """Mock database for testing without real DB."""
    return {}


@pytest.fixture
def override_dependencies(app):
    """
    Override FastAPI dependencies for testing.

    Usage:
        def test_with_mock_db(client, override_dependencies):
            # Dependencies are overridden for this test
            pass

    To override specific dependencies:
        app.dependency_overrides[get_db] = lambda: mock_db
    """
    original_overrides = app.dependency_overrides.copy()
    yield app.dependency_overrides
    # Restore original dependencies after test
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


@pytest.fixture(autouse=True)
def reset_dependency_overrides(app):
    """Auto-reset dependency overrides after each test."""
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def reset_global_state():
    """Reset in-memory data stores between tests."""
    yield
    for module_name in ['main', 'app', 'api', 'server', 'application']:
        try:
            mod = __import__(module_name)
            for attr_name in dir(mod):
                if attr_name.startswith('_'):
                    continue
                attr = getattr(mod, attr_name, None)
                if isinstance(attr, list):
                    attr.clear()
                elif isinstance(attr, dict):
                    attr.clear()
                elif isinstance(attr, set):
                    attr.clear()
            break
        except ImportError:
            continue
