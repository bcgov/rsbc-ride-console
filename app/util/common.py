from bson import ObjectId


def clean_mongo_doc(doc):
    """Convert ObjectId to string for '_id' field."""
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc
