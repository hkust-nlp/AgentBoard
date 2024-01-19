# from environment.webshop_env import Webshop
# from environment.babyai_env import BabyAI
# from environment.jericho_env import Jericho
# from environment.pddl_env.pddl_env import PDDL
# from environment.academia_env import AcademiaEnv
# from environment.movie_env import MovieEnv
# from environment.todo_env import TodoEnv
# from environment.weather_env import WeatherEnv
# from environment.sheet_env import SheetEnv
# from environment.scienceworld_env import Scienceworld
# from environment.alfworld.alfworld_env import AlfWorld
# from environment.browser_env import *

from common.registry import registry
import json
import os

# __all__ = [
#     "BabyAI",
#     "AlfWorld",
#     "Scienceworld",
    
#     "PDDL",
#     "Jericho",
    
#     "AcademiaEnv",
#     "MovieEnv",
#     "TodoEnv",
#     "SheetEnv",
#     "WeatherEnv",
    
#     "Webshop",
#     "BrowserEnv",
# ]


def load_environment(name, config):
    
    if name not in registry.list_environments():
        if name == 'babyai': from environment.babyai_env import BabyAI
        if name == "academia": from environment.academia_env import AcademiaEnv
        if name == "todo": from environment.todo_env import TodoEnv
        if name == "jericho": from environment.jericho_env import Jericho
        if name == "webshop": from environment.webshop_env import Webshop
        if name == "alfworld": from environment.alfworld.alfworld_env import AlfWorld
        if name == "scienceworld": from environment.scienceworld_env import Scienceworld
        if name == "movie": from environment.movie_env import MovieEnv
        if name == "weather": from environment.weather_env import WeatherEnv
        if name == "pddl": from environment.pddl_env.pddl_env import PDDL
        if name == "sheet": from environment.sheet_env import SheetEnv
        if name == "BrowserEnv": from environment.browser_env.envs import ScriptBrowserEnv

    
    env = registry.get_environment_class(name).from_config(config)

    return env

