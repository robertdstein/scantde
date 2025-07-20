from sqlmodel import Field, SQLModel
from scantde.database.models._source import default_time_field
import datetime


class Night(SQLModel, table=True):
    datestr: str = Field(primary_key=True, default=None, min_length=8, max_length=8)
    last_updated: datetime.datetime = default_time_field
    n_initial: int = Field(default=0)
    n_tdes: int = Field(default=0)
    n_candidates: int = Field(default=0)

