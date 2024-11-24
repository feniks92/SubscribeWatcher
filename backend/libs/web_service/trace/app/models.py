from pydantic import BaseModel, Field


class TraceRequest(BaseModel):
    root: bool = Field(True, description="True - делает корневой снимок,  False - делает сравнение с корневым снимком")
    limit: int = Field(default=5, description="Кол-во выводимых объектов памяти")
    exclude_filters: list[str] = Field(default_factory=list, description="Исключающий фильтр по traceback")
    include_filters: list[str] = Field(default_factory=list, description="Включающий фильтр по traceback")
