from pydantic import BaseModel
from typing import Optional

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: Optional[str] = None