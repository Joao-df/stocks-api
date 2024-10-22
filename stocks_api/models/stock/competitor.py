from pydantic import BaseModel


class Competitor(BaseModel):
    name: str
