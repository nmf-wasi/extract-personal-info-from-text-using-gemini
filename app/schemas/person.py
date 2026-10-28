from pydantic import BaseModel, Field, field_validator


class PersonalInfo(BaseModel):
    is_personal_info: bool = Field(
        description="False if the text is not about a person"
    )
    name: str | None = Field(description="null if not stated in the text")
    age: int | None = Field(description="null if not stated in the text")

    birthplace: str | None = Field(description="null if not stated in the text")

    @field_validator("age")
    @classmethod
    def validate_age(cls, value: int | None) -> int | None:
        if (value is not None and value < 0) or (value is not None and value) > 130:
            raise ValueError("Age can't be less than 0!")
        return value
