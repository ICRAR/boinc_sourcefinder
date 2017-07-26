from ..server.config import get_config
from ..server.duchamp.create_database import create_database as duchamp_create, destroy_database as duchamp_destroy
from ..server.sofia.create_database import create_database as sofia_create, destroy_database as sofia_destroy


def create_test_schemas():
    config = get_config()
    duchamp_create("duchamp_test", config["BASE_DB_LOGIN"])
    sofia_create("sofia_test", config["BASE_DB_LOGIN"])


def destroy_test_schemas():
    config = get_config()
    duchamp_destroy("duchamp_test", config["BASE_DB_LOGIN"])
    sofia_destroy("sofia_test", config["BASE_DB_LOGIN"])
