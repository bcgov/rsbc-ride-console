from pydantic import BaseModel, Field
from typing import Optional, Union
from bson import ObjectId
from app.models.pyobjectid import PyObjectId   

class EventMetadata(BaseModel):
    eventid: str

class Payload(BaseModel):
    ticket_number: str
    event: dict  

class Event(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    errorReason: Optional[str] = None
    eventType: str  
    apipath: str 
    datasource: str
    recon_count: Optional[int] = None    
    retry_count: Optional[int] = None  
    eventid: Union[str, int]    
    payloadstr: str

model_config = {
        "validate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: {ObjectId: str},
        }
    }


    
       
