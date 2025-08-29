from fastapi import APIRouter, Query, HTTPException
from bson import ObjectId
from typing import List, Optional
from app.models.error import Error
from app.db.mongo import ride_services_db
from app.util.common import clean_mongo_doc
from pydantic import BaseModel
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

class ObjectIdRequest(BaseModel):
    object_id: str

def parse_errors(docs):
    return [Error(**clean_mongo_doc(doc)) for doc in docs]

@router.get(
    "/",
    response_model=List[Error],
    tags=["error"],
    summary="Get list of error records with optional filters",
)
async def get_errors(
    fixed: Optional[bool] = Query(default=None),
    under_analysis: Optional[bool] = Query(default=None)
):
    query = {}

    if fixed is not None:
        if fixed:
            query["fixed"] = True
        else:
            query["$or"] = query.get("$or", []) + [
                {"fixed": False},
                {"fixed": {"$exists": False}}
            ]

    if under_analysis is not None:
        if under_analysis:
            query["under_analysis"] = True
        else:
            query["$or"] = query.get("$or", []) + [
                {"under_analysis": False},
                {"under_analysis": {"$exists": False}}
            ]

    docs = await ride_services_db["errors"].find(query).to_list(length=100)
    return parse_errors(docs)

#  Update individual record: set fixed = True, under_analysis = False
@router.post("/set-fixed", tags=["error"])
async def set_fixed_true(request: ObjectIdRequest):
    try:
        obj_id = ObjectId(request.object_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    result = await ride_services_db["errors"].update_one(
        {"_id": obj_id},
        {"$set": {"fixed": True, "under_analysis": False}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Error not found")

    return {"message": "Set fixed = true, under_analysis = false", "object_id": request.object_id}

#  Update individual record: set under_analysis = True, fixed = False
@router.post("/set-under-analysis", tags=["error"])
async def set_under_analysis_true(request: ObjectIdRequest):
    try:
        obj_id = ObjectId(request.object_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    result = await ride_services_db["errors"].update_one(
        {"_id": obj_id},
        {"$set": {"under_analysis": True, "fixed": False}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Error not found")

    return {"message": "Set under_analysis = true, fixed = false", "object_id": request.object_id}

#  Set ALL under_analysis = True, fixed = False
@router.post("/set-all-under-analysis", tags=["error"])
async def set_all_under_analysis_true():
    result = await ride_services_db["errors"].update_many(
        {},
        {"$set": {"under_analysis": True, "fixed": False}}
    )
    return {
        "message": "Set under_analysis = true, fixed = false for all",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }

#  Set ALL fixed = True, under_analysis = False
@router.post("/set-all-fixed", tags=["error"])
async def set_all_fixed_true():
    result = await ride_services_db["errors"].update_many(
        {},
        {"$set": {"fixed": True, "under_analysis": False}}
    )
    return {
        "message": "Set fixed = true, under_analysis = false for all",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }

@router.get("/fixed", response_model=List[Error], tags=["error"])
async def get_fixed_errors():
    docs = await ride_services_db["errors"].find({"fixed": True}).to_list(length=100)
    return parse_errors(docs)

@router.get("/under-analysis", response_model=List[Error], tags=["error"])
async def get_under_analysis_errors():
    docs = await ride_services_db["errors"].find({"under_analysis": True}).to_list(length=100)
    return parse_errors(docs)

@router.get("/new", response_model=List[Error], tags=["error"])
async def get_new_errors():
    query = {
        "$and": [
            {"$or": [{"fixed": False}, {"fixed": {"$exists": False}}]},
            {"$or": [{"under_analysis": False}, {"under_analysis": {"$exists": False}}]}
        ]
    }
    docs = await ride_services_db["errors"].find(query).to_list(length=100)
    return parse_errors(docs)

@router.get("/fixed/count", tags=["error"])
async def count_fixed_errors():
    count = await ride_services_db["errors"].count_documents({"fixed": True})
    return {"count": count}

@router.get("/under-analysis/count", tags=["error"])
async def count_under_analysis_errors():
    count = await ride_services_db["errors"].count_documents({"under_analysis": True})
    return {"count": count}

@router.get("/new/count", tags=["error"])
async def count_new_errors():
    query = {
        "$and": [
            {"$or": [{"fixed": False}, {"fixed": {"$exists": False}}]},
            {"$or": [{"under_analysis": False}, {"under_analysis": {"$exists": False}}]}
        ]
    }
    count = await ride_services_db["errors"].count_documents(query)
    return {"count": count}
