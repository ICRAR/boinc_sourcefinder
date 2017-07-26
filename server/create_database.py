import argparse
from sqlalchemy import create_engine
from config import get_config
from utils import module_import


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--app', type=str, required=True, help='The name of the app to use.')
    parser.add_argument('action', type=str, choices=["create", "destroy"], required=True, help='The action to perform.')
    parser.add_argument('schema', type=str, required=True, help="The schema name to use")
    args = vars(parser.parse_args())

    return args

if __name__ == "__main__":
    args = parse_args()
    app = args["app"]
    action = args["action"]
    schema = args["schema"]

    sql = ';'

    config = get_config(app)

    if action == "create":
        module = module_import("database_sql", app)
        sql = module.SQL.format(schema)
    elif action == "destroy":
        sql = "DROP SCHEMA IF EXISTS {0};".format(schema)

    engine = create_engine(config["BASE_DB_LOGIN"])
    connection = engine.connect()
    transaction = connection.begin()

    connection.execute(sql)

    transaction.commit()
    connection.close()
