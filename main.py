import os

from src.config_parser import Config
from src.tools import Logger

if __name__=="__main__":
    config = Config.deserialize("config/config.json")
    config.serialize(os.getcwd(), "processed_json.json")

    Logger.instance().debug("program terminated")