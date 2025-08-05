from pydantic import BaseModel, Field
from typing import Optional, Union, List
from bson import ObjectId
from app.models.pyobjectid import PyObjectId  
from datetime import datetime 

class ErrorMetadata(BaseModel):
    eventid: str

class ErrorComment(BaseModel):
    userName: str
    comment: str
    date: datetime



class Error(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    #errorReason: Optional[str] = None
    errorCategoryCd: str  
    errorSeverityLevelCd: str
    ticketNo: str
    detailsTxt: str
    serviceNm: str
    _class: str
    comments: Optional[List[ErrorComment]] = None

model_config = {
        "validate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {
            ObjectId: {ObjectId: str},
        }
    }


    
       
