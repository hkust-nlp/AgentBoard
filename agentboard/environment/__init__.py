from environment.webshop_env import Webshop
from environment.babyai_env import BabyAI
from environment.jericho_env import Jericho
from environment.pddl_env.pddl_env import PDDL
from environment.academia_env import AcademiaEnv
from environment.movie_env import MovieEnv
from environment.todo_env import TodoEnv
from environment.weather_env import WeatherEnv
from environment.sheet_env import SheetEnv
from environment.scienceworld_env import Scienceworld
from environment.alfworld.alfworld_env import AlfWorld
from environment.browser_env import *

from common.registry import registry
import json
import os

__all__ = [
    "BabyAI",
    "AlfWorld",
    "Scienceworld",
    
    "PDDL",
    "Jericho",
    
    "AcademiaEnv",
    "MovieEnv",
    "TodoEnv",
    "SheetEnv",
    "WeatherEnv",
    
    "Webshop",
    "BrowserEnv",
]


def load_environment(name, config):
    env = registry.get_environment_class(name).from_config(config)

    return env

