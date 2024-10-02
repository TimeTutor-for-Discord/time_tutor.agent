# generated by datamodel-codegen:
#   filename:  selfintroduction.json
#   timestamp: 2024-09-29T10:33:45+00:00

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, constr


class Model(BaseModel):
    guild_id: constr(max_length=20)
    member_id: constr(max_length=20)
    nickname: Optional[constr(max_length=50)] = None
    gender: Optional[constr(max_length=20)] = None
    twitter_id: Optional[constr(max_length=50)] = None
    specialty: Optional[str] = None
    before_study: Optional[str] = None
    after_study: Optional[str] = None
    sendmsg_id: Optional[constr(max_length=20)] = None
    mod_column: Optional[constr(max_length=20)] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
