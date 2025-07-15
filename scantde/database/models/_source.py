from sqlmodel import Field, SQLModel
from typing import Optional
import datetime


default_time_field = Field(
    default_factory=datetime.datetime.utcnow,
)


class NuclearSource(SQLModel, table=True):
    name: str = Field(primary_key=True)
    first_detected: datetime.datetime = default_time_field
    last_updated: datetime.datetime = default_time_field
    latest_datestr: str = Field(default=None, min_length=8, max_length=8)
    latest_ra: float = Field(default=None)
    latest_dec: float = Field(default=None)
    distpsnr1: float = Field(default=None)
    sgscore1: float = Field(default=None)
    is_tde: bool = Field(default=False)
    age: Optional[float] = Field(default=None)
    fail_step: Optional[str] = Field(default=None)
    tdescore: Optional[float] = Field(default=None)
    tdescore_best: Optional[str] = Field(default=None)
    tdescore_hostfast: Optional[float] = Field(default=None)
    tdescore_host: Optional[float] = Field(default=None)
    tdescore_infant: Optional[float] = Field(default=None)
    tdescore_week: Optional[float] = Field(default=None)
    tdescore_month: Optional[float] = Field(default=None)
    tdescore_thermal: Optional[float] = Field(default=None)
    tdescore_full: Optional[float] = Field(default=None)
