import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from app.main import app as fastapi_app # noqa: E402
from app.db.database import get_db # noqa: E402
from app.core.base.model import BaseTableModel  # noqa: E402

import app.api.models  # noqa: F401 E402

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    BaseTableModel.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()
        BaseTableModel.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def _get_test_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = _get_test_db
    try:
        yield TestClient(fastapi_app)
    finally:
        fastapi_app.dependency_overrides.clear()
