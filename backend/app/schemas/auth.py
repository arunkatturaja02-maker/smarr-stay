"""Pydantic request and response schemas for authentication."""

import re
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.user import UserRole

PHONE_PATTERN = re.compile(r"^\+?[0-9\s().-]{6,29}$")
EMPLOYEE_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,40}$")


class RegistrationRequest(BaseModel):
    """Shared fields for every staff registration endpoint.

    ``extra="forbid"`` means a client cannot smuggle in a role field. The role
    is assigned by the endpoint itself, never by request data.
    """

    model_config = ConfigDict(extra="forbid")

    full_name: str = Field(min_length=2, max_length=120)
    employee_id: str = Field(min_length=3, max_length=40)
    email: EmailStr
    phone_number: str = Field(min_length=7, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Full name must contain at least 2 characters.")
        return cleaned

    @field_validator("employee_id")
    @classmethod
    def validate_employee_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not EMPLOYEE_ID_PATTERN.fullmatch(cleaned):
            raise ValueError(
                "Employee ID must be 3-40 characters using letters, numbers, hyphens or underscores."
            )
        return cleaned.upper()

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        cleaned = value.strip()
        if not PHONE_PATTERN.fullmatch(cleaned) or not 7 <= sum(
            character.isdigit() for character in cleaned
        ) <= 20:
            raise ValueError("Enter a valid phone number with 7-20 digits.")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not any(character.islower() for character in value):
            raise ValueError("Password must include a lowercase letter.")
        if not any(character.isupper() for character in value):
            raise ValueError("Password must include an uppercase letter.")
        if not any(character.isdigit() for character in value):
            raise ValueError("Password must include a number.")
        return value

    @model_validator(mode="after")
    def passwords_must_match(self) -> "RegistrationRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    identifier: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=128)

    @field_validator("identifier")
    @classmethod
    def clean_identifier(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Enter your email address or employee ID.")
        return cleaned


class UserProfile(BaseModel):
    """Safe profile data. password_hash is intentionally absent."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    employee_id: str
    email: EmailStr
    phone_number: str
    role: UserRole


class RegistrationResponse(BaseModel):
    message: str
    role: UserRole
    requires_approval: bool = True
    email: EmailStr


class LoginResponse(BaseModel):
    message: str
    user: UserProfile


class MessageResponse(BaseModel):
    message: str
