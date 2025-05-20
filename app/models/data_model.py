from pydantic import BaseModel
from typing import List

class WordCount(BaseModel):
    keyword: str
    count: int

class Summary(BaseModel):
    title: str
    summary: str
    keywords: List[str]
    word_counts: List[WordCount]

class GmapsLink(BaseModel):
    link: str