import pytest
import yaml

from definition import CONFIG_PATH
# from repositories.db_selector import MongoDB


@pytest.fixture()
def config():
    with open(CONFIG_PATH, 'r') as file:
        config_file = yaml.safe_load(file)
        return config_file


# @pytest.fixture()
# def db_session(config):
#     obj = MongoDB(config)
#     db = obj.get_db()
#     yield db
#     obj.db_close()