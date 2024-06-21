import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase

def load_database() -> AsyncIOMotorDatabase:
    """Initialises MongoDB Database.

    Returns
    -------
    `AsyncIOMotorDatabase`
    """
    
    cluster = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    return cluster.get_database("SnapBot_Database")


def load_database_and_collection(collection: str) -> AsyncIOMotorCollection:
    """Initialises MongoDB Database and the specified collection. If the collection name provided is not found within the database, this function will create one with that name instead.

    Parameters
    ----------
    collection : `str`
        The name of the collection to be returned or created.

    Returns
    -------
    `AsyncIOMotorCollection`
    """
    
    cluster = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    database = cluster.get_database("SnapBot_Database")
    return database.get_collection(collection)