from pydantic import BaseModel


class LiveStream(BaseModel):
    num: int
    name: str
    stream_type: str = ""
    stream_icon: str = ""
    stream_id: int
    epg_channel_id: str | None = ""
    added: str = ""
    category_id: str = ""
    custom_sid: str = ""
    tv_archive: int
    direct_source: str = ""
    tv_archive_duration: int


class Category(BaseModel):
    category_id: str
    category_name: str
    parent_id: int
