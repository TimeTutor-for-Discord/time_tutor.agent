# generated by datamodel-codegen:
#   filename:  current_study_target.json
#   timestamp: 2024-09-29T10:33:44+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, constr


class Model(BaseModel):
    id: int
    guild_id: Optional[int] = None
    user_id: int
    study_target_id: constr(max_length=255)
    created_at: str
    updated_at: str
