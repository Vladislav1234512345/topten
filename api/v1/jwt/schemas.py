from pydantic import BaseModel


class TokensInfoSchema(BaseModel):
    access_token: str
    refresh_token: str