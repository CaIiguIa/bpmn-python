# coding=utf-8
"""
Class used for representing condition expression in sequence flow
"""
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class ConditionExpression(BaseModel):
    """
    Class used for representing condition expression in sequence flow.
    Fields:
    - condition: condition expression. Required field. Must be a String.
    """
    id: Optional[str] = Field(default=None, description="Optional ID of the condition expression")
    condition: str = Field(..., description="Condition expression. Required field.")

    @field_validator('condition')
    def validate_condition(cls, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Condition is required and must be a non-empty string")
        return value