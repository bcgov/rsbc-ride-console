from fastapi import APIRouter, Query, HTTPException

from bson import ObjectId
from typing import List, Optional
from app.models.error import Error
from app.db.mongo import ride_services_db
from app.util.common import clean_mongo_doc
from pydantic import BaseModel

import logging






router = APIRouter()
logger = logging.getLogger(__name__)
class ObjectIdRequest(BaseModel):
    object_id: str



def parse_errors(docs):
    return [Error(**clean_mongo_doc(doc)) for doc in docs]



from datetime import datetime

MOCK_ERRORS = [
    {
        "_id": "64f9e4f82fa9e00e8f6bba11",
        "errorCategoryCd": "DATA_QUALITY",
        "errorSeverityLevelCd": "HIGH",
        "ticketNo": "TKT-1001",
        "detailsTxt": "Missing required field 'customerId' in payload.",
        "serviceNm": "ride-booking-service",
        "_class": "com.example.ErrorRecord",
        "fixed": False,
        "under_analysis": True,
        "comments": [
            {
                "userName": "alice",
                "comment": "Investigated and confirmed issue.",
                "date": datetime(2025, 8, 1, 14, 30)
            },
            {
                "userName": "bob",
                "comment": "Fix deployed to production.",
                "date": datetime(2025, 8, 2, 10, 15)
            }
        ]
    },
    {
        "_id": "64f9e4f82fa9e00e8f6bba12",
        "errorCategoryCd": "TRANSFORMATION",
        "errorSeverityLevelCd": "MEDIUM",
        "ticketNo": "TKT-1002",
        "detailsTxt": "Incorrect date format in transformed payload.",
        "serviceNm": "ride-transformation-service",
        "_class": "com.example.ErrorRecord",
        "fixed": False,
        "under_analysis": True,
        "comments": None
    }
]


@router.get(
    "/errors",
    response_model=List[Error],
    tags=["error"],
    summary="Get list of error records with optional filters",
    responses={
        200: {
            "description": "List of errors",
            "content": {
                "application/json": {
                    "example": MOCK_ERRORS
                }
            }
        }
    }
)
async def get_errors(
    fixed: Optional[bool] = Query(default=None, description="Filter by fixed status"),
    under_analysis: Optional[bool] = Query(default=None, description="Filter by analysis status")
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


@router.post(
    "/errors/set-fixed",
    tags=["error"],
    summary="Set 'fixed' to true for a given error"
)
async def set_fixed_true(request: ObjectIdRequest):
    try:
        obj_id = ObjectId(request.object_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    result = await ride_services_db["errors"].update_one(
        {"_id": obj_id},
        {"$set": {"fixed": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Error not found")

    return {
        "message": "Field 'fixed' set to true",
        "object_id": request.object_id
    }

@router.post(
    "/errors/set-under-analysis",
    tags=["error"],
    summary="Set 'under_analysis' to true for a given error"
)
async def set_under_analysis_true(request: ObjectIdRequest):
    try:
        obj_id = ObjectId(request.object_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId format")

    result = await ride_services_db["errors"].update_one(
        {"_id": obj_id},
        {"$set": {"under_analysis": True}}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Error not found")

    return {
        "message": "Field 'under_analysis' set to true",
        "object_id": request.object_id
    }


@router.post(
    "/errors/set-all-under-analysis",
    tags=["error"],
    summary="Set 'under_analysis' = true for all errors"
)
async def set_all_under_analysis_true():
    result = await ride_services_db["errors"].update_many(
        {}, {"$set": {"under_analysis": True}}
    )

    return {
        "message": "Field 'under_analysis' set to true for all documents",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }


@router.post(
    "/errors/set-all-fixed",
    tags=["error"],
    summary="Set 'fixed' = true for all errors"
)
async def set_all_fixed_true():
    result = await ride_services_db["errors"].update_many(
        {}, {"$set": {"fixed": True}}
    )

    return {
        "message": "Field 'fixed' set to true for all documents",
        "matched_count": result.matched_count,
        "modified_count": result.modified_count
    }


