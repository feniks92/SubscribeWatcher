from pydantic import BaseModel, ConfigDict


class DatabaseBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
