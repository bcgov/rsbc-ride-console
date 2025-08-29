from fastapi import APIRouter,  HTTPException, Body, Path, Depends
from typing import List
from app.models.event import Event
from app.db.mongo import recon_db
from app.auth.auth import authenticate_user
from app.util.common import clean_mongo_doc
from bson import ObjectId
from bson.errors import InvalidId
import logging

from pydantic import BaseModel

class ResetRequest(BaseModel):
    object_id: str


router = APIRouter()
logger = logging.getLogger(__name__)

async def get_collection_count(collection_name: str, query: dict = {}):
    count = await recon_db[collection_name].count_documents(query)
    return {"count": count}



def get_events(docs):
    return [Event(**clean_mongo_doc(doc)) for doc in docs]

async def delete_event_by_id(collection_name: str, object_id: str):
    try:
        obj_id = ObjectId(object_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    result = await recon_db[collection_name].delete_one({"_id": obj_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Object not found")

    return {"message": "Document deleted successfully", "object_id": object_id}

async def delete_all_events(collection_name: str):
    result = await recon_db[collection_name].delete_many({})
    return {
        "message": f"All documents deleted from '{collection_name}'",
        "deleted_count": result.deleted_count

    }

async def reset_all_field(collection_name: str, field_name: str):
    result = await recon_db[collection_name].update_many(
        {}, {"$set": {field_name: 0}}
    )
    return {
        "message": f"All {field_name} values reset to 0 in '{collection_name}'",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }




MOCK_EVENTS = [
    {
        "errorReason": "Missing field in payloaddata",
        "eventType": "CREATE",
        "datasource": "source_A",
        "eventid": "evt123",
        "_id": "obj456",
        "recon_count": 11,
        "payloaddata": {
            "ticket_number": "TKT-789",
            "event": {
                "eventid": "evt123"
            }
        }
    },
    {
        
        "event_type": "UPDATE",
        "datasource": "source_B",
        "eventid": "evt999",
        "_id": "obj888",
        "retry_count": 3,
        "payloaddata": {
            "ticket_number": "TKT-101",
            "event": {
                "eventid": "evt999"
            }
        }
    }
]

def without_errorReason(events):
    return [{k: v for k, v in e.items() if k != "errorReason"} for e in events]

# 1. Retry Exceptions
@router.get(
    "/retry-exceptions",
    response_model=List[Event],
    tags=["recon"],
    responses={
        200: {
            "description": "List of retry exceptions",
            "content": {
                "application/json": {
                    "example": without_errorReason(MOCK_EVENTS)
                }
            }
        }
    }
)

#async def get_retry_exceptions(user: dict = Depends(authenticate_user)):
async def get_retry_exceptions():
   
    query = {"recon_count": {"$gt": 10}}
    docs = await recon_db["mainstaging"].find(query).to_list(length=100)
    return get_events(docs)

@router.delete(
    "/retry-exceptions/{object_id}",
    tags=["recon"],
    summary="Delete retry exception event by ObjectId"
)
async def delete_retry_exception(object_id: str = Path(..., description="MongoDB ObjectId")):
    return await delete_event_by_id("mainstaging", object_id)

@router.delete(
    "/retry-exceptions",
    tags=["recon"],
    summary="Delete all retry exception events"
)
async def delete_all_retry_exceptions():
    return await delete_all_events("mainstaging")





@router.post(
    "/retry-exceptions/reset",
    tags=["recon"],
    summary="Reset recon_count to 0 for a given object ID",
    response_description="Recon count reset result"
)
async def reset_recon_count(request: ResetRequest):
    try:
        object_id = ObjectId(request.object_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    try:
        result = await recon_db["mainstaging"].update_one(
            {"_id": object_id},
            {"$set": {"recon_count": 0}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Object not found")

        return {"message": "Recon count reset successfully", "object_id": request.object_id}

    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Failed to reset recon_count: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post(
    "/retry-exceptions/reset-all",
    tags=["recon"],
    summary="Reset recon_count to 0 for all documents in mainstaging"
)
async def reset_all_retry_exceptions():
    return await reset_all_field("mainstaging", "recon_count")




@router.post(
    "/error_count/reset-all",
    tags=["recon"],
    summary="Reset recon_count to 0 for all documents in errortable"
)
async def reset_all_error_count():
    return await reset_all_field("errortable", "retry_count")


@router.post(
    "/error_staging/reset-all",
    tags=["recon"],
    summary="Reset recon_count to 0 for all documents in errorstaging"
)
async def reset_all_error_staging():
    return await reset_all_field("errorstaging", "retry_count")

@router.post(
    "/staging_count/reset-all",
    tags=["recon"],
    summary="Reset recon_count to 0 for all documents in mainstaging"
)
async def reset_all_retry_exceptions():
    return await reset_all_field("mainstaging", "recon_count")

#  Error Count
@router.get(
    "/error_count",
    response_model=List[Event],
    tags=["recon"],
    responses={
        200: {
            "description": "List of error count events",
            "content": {
                "application/json": {
                    "example": MOCK_EVENTS
                }
            }
        }
    }
)
async def get_error_count(user: dict = Depends(authenticate_user)):
    docs = await recon_db["errortable"].find().to_list(length=100)
    return get_events(docs)


@router.delete(
    "/error_count/{object_id}",
    tags=["recon"],
    summary="Delete error count event by ObjectId"
)
async def delete_error_count(object_id: str = Path(..., description="MongoDB ObjectId")):
    return await delete_event_by_id("errortable", object_id)

@router.delete(
    "/error_count",
    tags=["recon"],
    summary="Delete all error count events"
)
async def delete_all_error_count():
    return await delete_all_events("errortable")


@router.post(
    "/error_count/reset",
    tags=["recon"],
    summary="Reset retry_count to 0 for a given object ID",
    response_description="Retry count reset result"
)
async def reset_retry_count(request: ResetRequest):
    try:
        object_id = ObjectId(request.object_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    try:
        result = await recon_db["errortable"].update_one(
            {"_id": object_id},
            {"$set": {"retry_count": 0}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Object not found")

        return {"message": "Retry count reset successfully", "object_id": request.object_id}

    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Failed to reset retry_count: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")



#  Error Staging
@router.get(
    "/error_staging",
    response_model=List[Event],
    tags=["recon"],
    responses={
        200: {
            "description": "List of error staging events",
            "content": {
                "application/json": {
                    "example": MOCK_EVENTS
                }
            }
        }
    }
)
async def get_error_staging():
    docs = await recon_db["errorstaging"].find().to_list(length=100)
    return get_events(docs)

@router.post(
    "/error_staging/reset",
    tags=["recon"],
    summary="Reset retry_count to 0 for a given object ID",
    response_description="Retry count reset result"
)
async def reset_retry_count_staging(request: ResetRequest):
    try:
        object_id = ObjectId(request.object_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    try:
        result = await recon_db["errorstaging"].update_one(
            {"_id": object_id},
            {"$set": {"retry_count": 0}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Object not found")

        return {"message": "Retry count reset successfully", "object_id": request.object_id}

    except HTTPException:
        raise  
    except Exception as e:
        logger.error(f"Failed to reset retry_count: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete(
    "/error_staging/{object_id}",
    tags=["recon"],
    summary="Delete error staging event by ObjectId"
)
async def delete_error_staging(object_id: str = Path(..., description="MongoDB ObjectId")):
    return await delete_event_by_id("errorstaging", object_id)


@router.delete(
    "/error_staging",
    tags=["recon"],
    summary="Delete all error staging events"
)
async def delete_all_error_staging():
    return await delete_all_events("errorstaging")


# 4. Staging Count
@router.get(
    "/staging_count",
    response_model=List[Event],
    tags=["recon"],
    responses={
        200: {
            "description": "List of staging count events",
            "content": {
                "application/json": {
                    "example": without_errorReason(MOCK_EVENTS)
                }
            }
        }
    }
)
async def get_staging_count():
   
    docs = await recon_db["mainstaging"].find().to_list(length=100)
    return get_events(docs)

@router.delete(
    "/staging_count/{object_id}",
    tags=["recon"],
    summary="Delete staging count event by ObjectId"
)
async def delete_staging_count(object_id: str = Path(..., description="MongoDB ObjectId")):
    return await delete_event_by_id("mainstaging", object_id)


@router.delete(
    "/staging_count",
    tags=["recon"],
    summary="Delete all staging count events"
)
async def delete_all_staging_count():
    return await delete_all_documents("mainstaging")


@router.get(
    "/retry-exceptions/count",
    tags=["recon"],
    summary="Get count of retry exceptions"
)
async def get_retry_exceptions_count():
    query = {"recon_count": {"$gt": 10}}
    return await get_collection_count("mainstaging", query)


@router.get(
    "/error_count/count",
    tags=["recon"],
    summary="Get count of error count events"
)
async def get_error_count_count():
    return await get_collection_count("errortable")


@router.get(
    "/error_staging/count",
    tags=["recon"],
    summary="Get count of error staging events"
)
async def get_error_staging_count():
    return await get_collection_count("errorstaging")


@router.get(
    "/staging_count/count",
    tags=["recon"],
    summary="Get count of staging count events"
)
async def get_staging_count_count():
    return await get_collection_count("mainstaging")


