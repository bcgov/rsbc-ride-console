import os
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import Config

from dotenv import load_dotenv

load_dotenv()
MONGO_URI = Config.MONGO_URI
client = AsyncIOMotorClient(MONGO_URI)
recon_db =  client["recon-db"]
ride_services_db = client["ride-services-db"]
