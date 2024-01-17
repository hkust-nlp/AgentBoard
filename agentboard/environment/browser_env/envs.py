import json
import os
import pdb
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List, Dict, Any, TypedDict, Union
import logging
import numpy as np
import numpy.typing as npt
from beartype import beartype
from beartype.door import is_bearable
from gymnasium import Env
from gymnasium.spaces import Box, Text
from common.registry import registry
from playwright.sync_api import (
    CDPSession,
    Page,
    Playwright,
    ViewportSize,
    expect,
    sync_playwright,
)

from utils.logging.agent_logger import AgentLogger, ColoredFormatter
from .actions import Action, execute_action, get_action_space
from .processors import ObservationHandler, ObservationMetadata
from .utils import (
    StateInfo,
    AccessibilityTree,
    DetachedPage,
    Observation,
    png_bytes_to_numpy,
)
from .evaluation_function import (
    Evaluator,
    StringEvaluator,
    URLEvaluator,
    HTMLContentEvaluator,
    EvaluatorComb,
    evaluator_router,
    EvaluatorPartial,
    URLSoftEvaluator,
    HTMLContentSoftEvaluator,
    progress_evaluator_router,
)

Trajectory = List[Union[Action, StateInfo]]

@dataclass
class PlaywrightScript:
    function: str  # goto, get_by_role
    destination: str  # https://www.google.com/, combobox
    name: Union[str, None] = None  # Search, Avatar 2009
    operation: Union[str, None] = None  # click, fill, press
    value: Union[str, None] = None  # avatar movie, Enter


@registry.register_environment("BrowserEnv")
class ScriptBrowserEnv(Env[Dict[str, Observation], Action]):
    """
    The goal of this environment is to produce a prototype of a browser environment.
    In the end, we want to support a fully configurable browser environment with wide
    range of action spaces and observation spaces, both structured and unstructured.
    But in this prototype, we just support action space specified by Playwright script,
    and observation space is the html content of the page.
    """

    @beartype
    def __init__(
        self,
        max_page_length: int = 8192,
        headless: bool = True,
        slow_mo: int = 0,
        observation_type: str = "html",
        current_viewport_only: bool = False,
        viewport_size: ViewportSize = {"width": 1280, "height": 720},
        save_trace_enabled: bool = False,
        sleep_after_execution: float = 0.0,
    ):
        self.goal = None
        self.reward = 0.0
        self.obs = None
        self.history: Trajectory = []
        self.state: StateInfo = {}
        self.config_file = None
        self.action_space = get_action_space()  # type: ignore[assignment]
        self.headless = headless
        self.slow_mo = slow_mo
        self.current_viewport_only = current_viewport_only
        self.reset_finished = False
        self.viewport_size = viewport_size
        self.save_trace_enabled = save_trace_enabled
        self.sleep_after_execution = sleep_after_execution
        self.env_config = None
        self.temp_trajectory = []
        self.progress_score = 0.0
        self.progress_score_url = 0
        self.progress_score_content = 0
        self.detail_score = []
        self.content_detail_score = []
        self.progress_content = None
        

        if observation_type == "html" or observation_type == "accessibility_tree":
            self.text_observation_type = observation_type
            self.image_observation_type = ""
            self.main_observation_type = "text"
        elif observation_type == "image":
            self.image_observation_type = observation_type
            self.text_observation_type = ""  # type: ignore[assignment]
            self.main_observation_type = "image"
        else:
            raise ValueError(
                f"Unsupported observation type: {observation_type}"
            )

        self.observation_handler = ObservationHandler(
            self.main_observation_type,
            self.text_observation_type,
            self.image_observation_type,
            self.current_viewport_only,
            self.viewport_size,
        )

        self.observation_space = (
            self.observation_handler.get_observation_space()
        )

    def get_info(self):
        pass

    def get_obs(self) -> Dict[str, Observation]:
        obs = self.observation_handler.get_observation(
            self.page, self.get_page_client(self.page)
        )
        self.obs = obs
        return obs

    def get_obs_metadata(self) -> Dict[str, ObservationMetadata]:
        metadata = self.observation_handler.get_observation_metadata()
        return metadata

    def get_goal(self):
        return self.goal

    def get_history(self):
        return self.history

    def get_action_space(self):
        actions = [
            "click [id]",
            "type [id] [content] [press_enter_after=0|1]",
            "hover [id]",
            "press [key_comb]",
            "scroll [direction=down|up]",
            "new_tab",
            "tab_focus [tab_index]",
            "close_tab",
            "goto [url]",
            "go_back",
            "go_forward",
            "stop [answer]"
        ]

        action_space = [[action] for action in actions]
        return action_space

    def is_done(self):  # not valid in Web browse :)
        pass

    def update(self, action, obs, reward, done, infos):
        pass

    @beartype
    def setup(self, config_file) -> None:  # setup env in reset step
        self.context_manager = sync_playwright()
        self.playwright = self.context_manager.__enter__()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless, slow_mo=self.slow_mo
        )

        if config_file:
            instance_config = config_file
        else:
            instance_config = {}
        self.env_config = instance_config

        storage_state = instance_config.get("storage_state", None)
        start_url = instance_config.get("start_url", None)
        geolocation = instance_config.get("geolocation", None)
        self.goal = instance_config.get("intent", None)

        self.context = self.browser.new_context(
            viewport=self.viewport_size,
            storage_state=storage_state,
            geolocation=geolocation,
            device_scale_factor=1,
        )
        if self.save_trace_enabled:
            self.context.tracing.start(screenshots=True, snapshots=True)
        if start_url:
            start_urls = start_url.split(" |AND| ")
            for url in start_urls:
                page = self.context.new_page()
                client = page.context.new_cdp_session(
                    page
                )  # talk to chrome devtools
                if self.text_observation_type == "accessibility_tree":
                    client.send("Accessibility.enable")
                page.client = client
                page.goto(url, timeout=180000)
            # set the first page as the current page
            self.page = self.context.pages[0]
            self.page.bring_to_front()
        else:
            self.page = self.context.new_page()
            client = self.page.context.new_cdp_session(self.page)
            if self.text_observation_type == "accessibility_tree":
                client.send("Accessibility.enable")
            self.page.client = client

    @beartype
    def reset(
        self,
        *,
        seed: Union[int, None] = None,
        options: Union[Dict[str, Dict], None] = None):
        """
        Reset the environment.
        :param options: options for the environment. The current supported options are:
            - "config_file": a json.
        """
        super().reset(seed=seed, options=options)
        if self.reset_finished:
            self.context_manager.__exit__()

        self.progress_score = 0.0
        self.progress_score_url = 0
        self.progress_score_content = 0
        self.url_detail_score = 0
        self.content_detail_score = []
        self.detail_score = []
        self.progress_content = None

        if options is not None and "config_file" in options:
            self.setup(config_file=options["config_file"])
            self.config_file = options["config_file"]
        else:
            self.setup()
        self.reset_finished = True

        if self.sleep_after_execution > 0:
            time.sleep(self.sleep_after_execution)

        observation = self.get_obs()
        observation_metadata = self.get_obs_metadata()
        info = {
            "page": DetachedPage(self.page.url, ""),
            "fail_error": "",
            "observation_metadata": observation_metadata,
        }
        self.state = {"observation": observation, "info": info}  # init state
        self.history = [self.state]

    def step(
            self, action: Action
    ) -> Tuple[Dict[str, Observation], float, bool, Dict[str, Any]]:
        if not self.reset_finished:
            raise RuntimeError("Call reset first before calling step.")

        success = False
        fail_error = ""
        try:
            self.page = execute_action(
                action,
                self.page,
                self.context,
                self.observation_handler.action_processor,
            )
            success = True
        except Exception as e:
            fail_error = str(e)

        if self.sleep_after_execution > 0:
            time.sleep(self.sleep_after_execution)

        observation = self.get_obs()
        observation_metadata = self.get_obs_metadata()

        info = {
            "page": DetachedPage(self.page.url, self.page.content()),
            "fail_error": fail_error,
            "observation_metadata": observation_metadata,
        }

        # reward cal
        state_info = {"observation": observation, "info": info}
        self.temp_trajectory.append(state_info)
        self.temp_trajectory.append(action)
        try:
            result_dic, progress_evaluators = progress_evaluator_router(self.config_file)

            if "url_score" in result_dic and "content_score" in result_dic:
                detail_score, step_url_score = progress_evaluators[0](
                    trajectory=self.temp_trajectory,
                    config_file=self.config_file,
                    page=self.page,
                )
                if self.progress_score_url < step_url_score:
                    self.progress_score_url = step_url_score
                self.url_detail_score = detail_score

                score_set, content_set = progress_evaluators[-1](
                    trajectory=self.temp_trajectory,
                    config_file=self.config_file,
                    page=self.page,
                )
                if len(self.content_detail_score) == 0:
                    self.content_detail_score = score_set.copy()
                # pdb.set_trace()
                self.content_detail_score = [x1 or x2 for x1, x2 in zip(score_set, self.content_detail_score)]
                progress_score = sum(self.content_detail_score) / len(self.content_detail_score)
                self.progress_score_content = progress_score
                self.progress_content = content_set
                tmp_progress_score = (3 / (len(score_set) + 3)) * self.progress_score_url + (
                            len(score_set) / (len(score_set) + 3)) * self.progress_score_content
                if self.progress_score < tmp_progress_score:
                    self.progress_score = tmp_progress_score
                self.detail_score = self.url_detail_score + ['<split>'] + self.content_detail_score

            elif "url_score" in result_dic:
                detail_score, step_url_score = progress_evaluators[0](
                    trajectory=self.temp_trajectory,
                    config_file=self.config_file,
                    page=self.page,
                )
                if self.progress_score < step_url_score:
                    self.progress_score = step_url_score
                self.detail_score = detail_score

            elif "content_score" in result_dic:
                score_set, content_set = progress_evaluators[-1](
                    trajectory=self.temp_trajectory,
                    config_file=self.config_file,
                    page=self.page,
                )
                if len(self.detail_score) == 0:
                    self.detail_score = score_set.copy()
                self.detail_score = [x1 or x2 for x1, x2 in zip(score_set, self.detail_score)]
                progress_score = sum(self.detail_score) / len(self.detail_score)
                self.progress_score = progress_score
                self.progress_content = content_set
            self.reward = self.progress_score
        except Exception as e:
            print(f"Progress score ERROR: {str(e)}")
            #####
        # pdb.set_trace()
        msg = (
            observation,
            float(success),
            False,  # truncated
            info,
        )
        self.state = {"observation": observation, "info": info}
        self.history.append(self.state)
        return msg

    def save_log(self, task_name, output_dir):  # result_dir contains more detailed log. (e.g. Screenshot and error.log)
        log_dir = os.path.join(output_dir, 'trajectory')
        os.makedirs(log_dir, exist_ok=True)
        log_file_name = f'{task_name}.log'
        log_file_path = os.path.join(log_dir, log_file_name)
        logger = AgentLogger(__name__, filepath=log_file_path)

        return logger

    def get_page_client(self, page: Page) -> CDPSession:
        return page.client

    def save_trace(self, trace_path: Union[str, Path]) -> None:
        if self.save_trace_enabled:
            self.context.tracing.stop(path=trace_path)

    def close(self) -> None:
        if self.reset_finished:
            self.context_manager.__exit__()

    @classmethod
    def from_config(cls, cfg):
        headless = cfg.get("headless", True)
        slow_mo = cfg.get("slow_mo", 0)
        observation_type = cfg.get("observation_type", "html")
        current_viewport_only = cfg.get("current_viewport_only", False)
        viewport_size = cfg.get("viewport_size", {"width": 1280, "height": 720})
        save_trace_enabled = cfg.get("save_trace_enabled", False)
        sleep_after_execution = cfg.get("sleep_after_execution", 0.0)

        env = cls(headless=headless,
                  slow_mo = slow_mo,
                  observation_type = observation_type,
                  current_viewport_only = current_viewport_only,
                  viewport_size = viewport_size,
                  save_trace_enabled = save_trace_enabled,
                  sleep_after_execution = sleep_after_execution)
        return env


