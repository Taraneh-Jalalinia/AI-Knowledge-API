import os

os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("RAG_MOCK", "true")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-ci-only-32chars")
os.environ.setdefault("JWT_REFRESH_SECRET_KEY", "test-refresh-secret-for-ci-32chars")
os.environ.setdefault("ALGORITHM", "HS256")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    signup = client.post(
        "/auth/signup",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    assert signup.status_code == 200
    token = signup.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
