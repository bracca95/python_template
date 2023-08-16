import os
import sys

"""Adjust the path to point to the root of your project

The following instructions are needed in case I wanted to use this program as a python module. The ideal solution would
be executing an instance of `main.py` that lies outside the project. In that case, I would not need `project_root`, but
what is defined here in `current_dir` would be enough. Consider this solution as a test for the module itself. Notice,
indeed, that the linter complains when importing the library because in this file we are ACTUALLY already inside the 
named folder.
"""


current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, project_root)

from python_template.src.config_parser import Config
from python_template.src.tools import Logger

if __name__=="__main__":
    config = Config.deserialize("config/config.json")
    config.serialize(current_dir, "processed_json.json")

    Logger.instance().debug("program terminated")