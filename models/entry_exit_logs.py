# generated by datamodel-codegen:
#   filename:  entry_exit_logs.json
#   timestamp: 2024-09-29T08:39:13+00:00

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class Column(BaseModel):
    name: str
    type: str
    null: Optional[bool] = None
    comment: Optional[str] = None


class Part(BaseModel):
    column: str


class Index(BaseModel):
    name: str
    parts: List[Part]


class PrimaryKey(BaseModel):
    parts: List[Part]


class Model(BaseModel):
    name: str
    columns: List[Column]
    indexes: List[Index]
    primary_key: PrimaryKey
    comment: str
    charset: str
    collate: str
