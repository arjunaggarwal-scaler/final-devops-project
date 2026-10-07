"""Pytest configuration and fixtures.

The test suite runs against an isolated on-disk SQLite database so it never
touches the real PostgreSQL production database. DATABASE_URL is forced to
SQLite *before* the application modules are imported.
"""
import os

# Force the test database BEFORE importing the app (config reads it at import time).
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def _fresh_schema():
    """Create the schema once for the test session and drop it afterwards."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    """A FastAPI TestClient wired to the SQLite test database."""
    return TestClient(app)
