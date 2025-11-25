from pydantic import BaseModel, Field


class VersionResponse(BaseModel):
    name: str = Field(description="Service name")
    version: str = Field(description="Semantic version of the API deployment")
