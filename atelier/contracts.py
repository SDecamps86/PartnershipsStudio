from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Score = Annotated[int, Field(ge=1, le=5)]
Text = Annotated[str, Field(min_length=1, max_length=8000)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_max_length=8000)
