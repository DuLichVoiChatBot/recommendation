from pydantic import BaseModel

class Location_review(BaseModel):
    location_id : str
    rate: int
    user_id: str