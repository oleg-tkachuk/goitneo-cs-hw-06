try:
    from modules.logger import logger_mongo
    from pymongo.server_api import ServerApi
    from pymongo.mongo_client import MongoClient
    from pymongo.errors import ConnectionFailure, PyMongoError
except ModuleNotFoundError as e:
    print(f"Import error in the mongo module: {e}")
    exit(1)


def insert_data_into_mongo(data, mongo_client_params):
    username = mongo_client_params.get('username')
    password = mongo_client_params.get('password')
    hostname = mongo_client_params.get('hostname')
    port = mongo_client_params.get('port')

    auth_source = mongo_client_params.get('auth_source')
    db_name = mongo_client_params.get('db_name')
    collection_name = mongo_client_params.get('collection_name')
    server_api_version = mongo_client_params.get('server_api_version')

    uri = f"mongodb://{username}:{password}@{hostname}:{port}/?authSource={auth_source}"
    uri_to_log = f"mongodb://{username}:<password_hidden>@{hostname}:{port}/?authSource={auth_source}"

    try:
        logger_mongo.info(
            f"Connecting to MongoDB: {uri_to_log}, server API version: {server_api_version}")
        logger_mongo.info(
            f"Database: {db_name}, collection: {collection_name}")
        client = MongoClient(uri, server_api=ServerApi(server_api_version))

        db = client.get_database(db_name)
        collection = db.get_collection(collection_name)

        logger_mongo.info(f"Inserting data...")
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)
        logger_mongo.info(f"Data inserted successfully.")
    except ConnectionFailure as e:
        logger_mongo.error(f"Connection failed: {e}")
    except PyMongoError as e:
        logger_mongo.error(f"An error has occurred: {e}")
    except Exception as e:
        logger_mongo.error(f"An unexpected error occurred: {e}")
    finally:
        try:
            client.close()
            logger_mongo.info(f"Connection closed.")
        except NameError:
            pass
