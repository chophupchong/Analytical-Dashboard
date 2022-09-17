from pydantic import BaseModel


class BasicMetrics(BaseModel):
    day: str
    views: int
    comments: int
    likes: int
    dislikes: int
    estimatedMinutesWatched: int
    averageViewDuration: int

    class Config:
        schema_extra = {
            "example": {
                "day": "2022-09-01",
                "views": 1,
                "comments": 1,
                "likes": 1,
                "dislikes": 1,
                "estimatedMinutesWatched": 1,
                "averageViewDuration": 1
            }
        }
