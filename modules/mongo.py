try:
    from urllib.parse import unquote_plus
    from modules.logger import logger_mongo
    from pymongo.server_api import ServerApi
    from pymongo.mongo_client import MongoClient
except ModuleNotFoundError as e:
    print(f"Import error in the mongo module: {e}")
    exit(1)


def insert_data_into_mongo(data, mongo_uri,
                           mongo_server_api_version,
                           mongo_db_name,
                           mongo_collection_name):

    client = MongoClient(mongo_uri, server_api=ServerApi(mongo_server_api_version))
    db = client.get_database(mongo_db_name)
    collection = db.get_collection(mongo_collection_name)

    parse_data = unquote_plus(data.decode())

    try:
        parse_data = {key: value for key, value in
                      [item.split('=') for item in parse_data.split('&')]}
        if isinstance(parse_data, list):
            result = collection.insert_many(parse_data)
        else:
            result = collection.insert_one(parse_data)
        return result
    except ValueError as e:
        logger_mongo.error(f'Parse error: {e}')
    except Exception as e:
        logger_mongo.error(f'Failed to insert: {e}')
    finally:
        client.close()
