"""Configuration safety tests (no database connection required)."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings

VALID_SECRET = "a-random-test-secret-value-that-is-long-enough"


def test_example_jwt_secret_placeholder_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="test",
            database_url="sqlite+pysqlite:///:memory:",
            jwt_secret_key=(
                "CHANGE_ME_GENERATE_A_RANDOM_SECRET_OF_AT_LEAST_32_CHARACTERS"
            ),
        )


def test_example_database_password_placeholder_is_rejected():
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment="test",
            database_url=(
                "postgresql+psycopg://staysmart_user:"
                "CHANGE_ME_DB_PASSWORD@localhost:5432/staysmart"
            ),
            jwt_secret_key=VALID_SECRET,
        )
