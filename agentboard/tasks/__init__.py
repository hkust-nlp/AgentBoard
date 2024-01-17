from .webshop import EvalWebshop
from .alfworld import Evalalfworld
from .webbrowse import EvalWebBrowse
from .babyai import EvalBabyai
from .pddl import EvalPddl
from .scienceworld import EvalScienceworld
from .jericho import EvalJericho
from .tool import EvalTool

from common.registry import registry

__all__ = [
    "Evalalfworld",
    "EvalBabyai",
    "EvalPddl",
    "EvalWebBrowse",
    "EvalWebshop",
    "EvalJericho",
    "EvalTool",
    "EvalWebshop",
    "EvalScienceworld"
]


def load_task(name, run_config, llm_config, agent_config, env_config, llm=None):
    task = registry.get_task_class(name).from_config(run_config, llm_config, agent_config, env_config, llm=llm)

    return task

