import subprocess
import json
import os
import pdb
import logging
import requests
from pathlib import Path
from typing import List, Dict, Any, Tuple, Union
from common.registry import registry
import traceback
from beartype import beartype
from beartype.door import is_bearable
from playwright._impl._api_types import TimeoutError
from agents import load_agent
from agents.vanilla_agent import VanillaAgent
from llm import load_llm
from environment.browser_env.actions import Action, create_id_based_action, create_playwright_action, \
    ActionParsingError, create_none_action, ActionTypes, create_stop_action
from environment.browser_env.utils import StateInfo
from environment.browser_env.help_function import RenderHelper, map_url_to_real, extract_action, \
    log_progress_score, transform_format, get_action_description, early_stop
from environment.browser_env.evaluation_function import (
    evaluator_router,
    progress_evaluator_router,
)
from environment import load_environment
from utils.logging.logger import TaskLogger

from .base_task import BaseTask


@registry.register_task("webarena")
class EvalWebBrowse(BaseTask):
    def __init__(self,
                 llm_name="gpt",
                 llm_config=None,
                 env_config=None,
                 agent_name="VanillaAgent",
                 agent_config=None,
                 max_num_steps=30,
                 parsing_failure_th=3,
                 repeating_action_failure_th=3,
                 task_name=None,
                 start_test_id=0,
                 test_case_count=20,
                 label_path=None,
                 llm=None,
                 baseline_dir = None,
                 log_path = None
                 ):
        
        super().__init__()
        
        if llm is None:
            llm = load_llm(llm_name, llm_config)
        self.agent = load_agent(agent_name, agent_config, llm)
        self.max_num_steps = max_num_steps
        self.parsing_failure_th = parsing_failure_th
        self.repeating_action_failure_th = repeating_action_failure_th
        self.early_stop_thresholds = {
            "parsing_failure": self.parsing_failure_th,
            "repeating_action": self.repeating_action_failure_th,
        }
        self.task_name = task_name
        self.llm_config = llm_config
        self.output_log_dir = log_path
        self.result_dir = os.path.join(log_path, f'logs/{task_name}_tracks')
        # webarena provide detailed trajectory. (e.g. html_screenshot ,trace and error.log)
        os.makedirs(self.result_dir, exist_ok=True)
        self.start_test_id = start_test_id,
        self.test_case_count = test_case_count,
        self.label_path = label_path
        self.test_file_list = []
        self.difficulties = []
        self.env_config = env_config
        self.render_screenshot = self.env_config["render_screenshot"]
        self.render_helper = None
        self.action_set_tag = self.env_config["action_set_tag"]
        
        self.baseline_dir = baseline_dir
        
        self.agentboard = TaskLogger(task_name="webarena", log_path=log_path, max_num_steps=self.max_num_steps, baseline_dir=self.baseline_dir)


    def get_test_list(self):
        start_test_id = int(self.start_test_id[0])
        test_case_count = int(self.test_case_count[0])
        label_path = self.label_path  # Result directory
        with open(label_path, 'r', encoding='utf-8') as infile:
            for line in infile:
                jsonl_item = json.loads(line.strip())
                json_file = transform_format(jsonl_item)
                self.test_file_list.append(json_file)
                self.difficulties.append(jsonl_item["difficulty"])
            line_count = len(self.test_file_list)
        self.test_file_list = self.test_file_list[start_test_id: min(start_test_id + test_case_count, line_count)]

        print(f"Total {len(self.test_file_list)} tasks left")

    def evaluate_env(self, idx: int):
        config_file = self.test_file_list[idx]
        meta_data = {"action_history": ["None"]}
        template = """WINDOWED PAGE:{{
{observation}
}}
URL: {url}"""
        last_reward = 0.
        grounding_error_count = 0
        score_change_record = []
        error_happened = 0
        error_obs = None
        reset_session = 0
        step_id = 0
        trajectory = []
        
        trajectory.append({"Goal":self.env.goal, "id":0})
        
        while step_id < self.max_num_steps:
            obs_step = self.env.state["observation"]["text"]
            page_step = self.env.state["info"]["page"]
            url_step = page_step.url
            current_step = template.format(
                url=map_url_to_real(url_step),
                observation=obs_step,
            )
            current_state = str(current_step)

           
            try:
                early_stop_flag, action_invalid, stop_info = early_stop(
                    self.env.history, self.early_stop_thresholds
                )

                if early_stop_flag:
                    action = create_stop_action("N/A")
                    if action_invalid:
                        grounding_error_count += 1
                    break
                if step_id == 1 and not reset_session:
                    # reset logout problem
                    if "sign in" in obs_step.lower() and not url_step.startswith("https"):
                        try:
                            # reset env
                            completed_process = subprocess.run(["bash", "./scripts/prepare_webbrowse.sh"], check=True)
                            print("Script executed successfully!")
                            self.env.reset(options={"config_file": config_file})
                            reset_session = 1
                            continue

                        except subprocess.CalledProcessError as e:
                            print(f"Error occurred while executing script: {str(e)}")
                if step_id:
                    if isinstance(self.agent, VanillaAgent):
                        self.agent.update(action=response[1], state=current_state)
                elif step_id == 0:
                    self.agent.reset(self.env.goal, init_obs=current_state, init_act=None)
                response = self.agent.run(init_prompt_dict=None)
                try:
                    parsed_response = extract_action(response[1])
                    trajectory.append({"Action":parsed_response, "id":step_id})
                    
                    if self.action_set_tag == "id_accessibility_tree":
                        action = create_id_based_action(parsed_response)
                    elif self.action_set_tag == "playwright":
                        action = create_playwright_action(parsed_response)
                    else:
                        raise ValueError(f"Unknown action type {self.action_set_tag}")
                    action["raw_prediction"] = response[1]
                except ActionParsingError as e:
                    error_happened = 1
                    error_obs = str(e)
                    action = create_none_action()
                    action["raw_prediction"] = response[1]
            
            except ValueError as e:
                # get the error message
                action = create_stop_action(f"ERROR: {str(e)}")

            self.env.history.append(action)
            action_str = get_action_description(
                action,
                self.env.state["info"]["observation_metadata"],
                action_set_tag=self.action_set_tag,
            )
            self.render_helper.render(
                action, self.env.state, meta_data, self.render_screenshot
            )
            meta_data["action_history"].append(action_str)
            if action["action_type"] == ActionTypes.STOP:
                break
            result_dic, progress_evaluators = progress_evaluator_router(config_file)
            try:
                obs, _, _, info = self.env.step(action)
                if error_happened:
                    obs["text"] = error_obs
                    error_happened = 0
                    grounding_error_count += 1
                reward = self.env.reward
                if reward > last_reward:
                    score_change_record.append((step_id, reward))
                last_reward = reward
                
                trajectory.append({"Observation":obs["text"], "id":step_id})
                trajectory.append({"Reward":last_reward, "id":step_id})
            except TimeoutError as e:
                raise
            except Exception as e:
                raise
            step_id += 1
            if step_id == self.max_num_steps:
                self.env.history.append(create_stop_action(""))
                break
            if last_reward == 1.0:  # early stop when success
                break

        evaluator = evaluator_router(config_file)
        success = evaluator(
            trajectory=self.env.history,
            config_file=config_file,
            page=self.env.page,
        )
        progress_score = self.env.progress_score
        success = 1.0 if progress_score == 1.0 else success

        grounding_acc = (step_id + 1 - grounding_error_count) / (step_id + 1)
        
        
        env_details = {"task_name": "webbrowse", "goal": self.agent.goal, "difficulty": self.difficulties[int(idx)]}
        try: example_prompt = self.agent.get_example_prompt()
        except: example_prompt = None  
        self.agentboard.log_example(idx, success, progress_score, grounding_acc, score_change_record, env_details, trajectory, example_prompt)

        return success, progress_score, grounding_acc, score_change_record, step_id + 1

    def evaluate(self):
        print("Session Refreshing!")
        try:
            completed_process = subprocess.run(["bash", "./scripts/prepare_webbrowse.sh"], check=True)
            print("Session Refreshed!")
        except Exception as e:
            print("Error: Session refreshed failed. Please check logs/webarena_tracks/error.txt for more details.")
        self.env = load_environment('BrowserEnv', self.env_config)
        if not (Path(self.result_dir) / "traces").exists():
            (Path(self.result_dir) / "traces").mkdir(parents=True)
        self.get_test_list()
        scores = []
        success = 0
        steps = 0
        progress_scores = []
        grounding_acc_avg = []
        score_state_avg = []

        for idx, config_file in enumerate(self.test_file_list):
            
            try:
                self.render_helper = RenderHelper(
                    config_file, self.result_dir, self.action_set_tag
                )
                self.env.reset(options={"config_file": config_file})
                task_id = self.env.env_config.get('task_id', None)

                success, progress_score, grounding_acc, score_state, steps = self.evaluate_env(idx=idx)
                progress_scores.append(progress_score)
                scores.append(success)
                grounding_acc_avg.append(grounding_acc)
                score_state_avg.append(score_state)

                if self.env_config["save_trace_enabled"]:
                    self.env.save_trace(
                        Path(self.result_dir) / "traces" / f"{task_id}.zip"
                    )

            except TimeoutError as e:
                with open(Path(self.result_dir) / "error.txt", "a") as f:
                    f.write(f"[Config file id]: {config_file['task_id']}\n")
                    f.write(f"[Timeout Error] {repr(e)}\n")
                    f.write(traceback.format_exc())  # write stack trace to file
            except requests.ConnectionError as e:
                with open(Path(self.result_dir) / "error.txt", "a") as f:
                    f.write(f"[Config file id]: {config_file['task_id']}\n")
                    f.write(f"[Connection Error] {repr(e)}\n")
                    f.write(traceback.format_exc())
            except Exception as e:
                progress_scores.append(self.env.progress_score)
                scores.append(0.0)
                with open(Path(self.result_dir) / "error.txt", "a") as f:
                    f.write(f"[Config file id]: {config_file['task_id']}\n")
                    f.write(f"[Unhandled Error] {repr(e)}\n")
                    f.write(traceback.format_exc())
                break
            self.render_helper.close()

        self.env.close()
        difficulties = self.difficulties
        success_rate = scores
        sr = sum(success_rate) * 1.0 / len(success_rate)
        pr = sum(progress_scores) * 1.0 / len(progress_scores)
        gr = sum(grounding_acc_avg) * 1.0 / len(grounding_acc_avg)

        hard_sr = [sr for sr, difficulty in zip(success_rate, difficulties) if difficulty == "hard"]
        hard_sr = sum(hard_sr) / len(hard_sr) if len(hard_sr) > 0 else 0

        hard_pr = [pr for pr, difficulty in zip(progress_scores, difficulties) if difficulty == "hard"]
        hard_pr = sum(hard_pr) / len(hard_pr) if len(hard_pr) > 0 else 0

        easy_sr = [sr for sr, difficulty in zip(success_rate, difficulties) if difficulty == "easy"]
        easy_sr = sum(easy_sr) / len(easy_sr) if len(easy_sr) > 0 else 0

        easy_pr = [pr for pr, difficulty in zip(progress_scores, difficulties) if difficulty == "easy"]
        easy_pr = sum(easy_pr) / len(easy_pr) if len(easy_pr) > 0 else 0

        
                        
        self.agentboard.log_summary(sr, pr, gr, score_state_avg, hard_sr, hard_pr, easy_sr, easy_pr)
        
        return scores, progress_scores, grounding_acc_avg, score_state_avg, easy_sr, hard_sr, easy_pr, hard_pr

    @classmethod
    def from_config(cls,
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    llm=None
                    ):
        llm_name = llm_config.get("name", "gpt")
        agent_name = agent_config.get("name", "VanillaAgent")
        max_num_steps = run_config.get("max_num_steps", 30)
        baseline_dir = run_config.get("baseline_dir", "data/baseline_results")
        log_path = run_config.get("log_path", None)
        task_name = env_config.get("name", 'webarena')
        parsing_failure_th = env_config.get("parsing_failure_th", 3)
        repeating_action_failure_th = env_config.get("repeating_action_failure_th", 3)
        label_path = env_config.get("label_path", './data/webarena/test.jsonl')
        start_test_id = env_config.get("start_test_id", 0)
        test_case_count = env_config.get("test_case_count", 5)

        return cls(llm_name=llm_name,
                   llm_config=llm_config,
                   env_config=env_config,
                   agent_name=agent_name,
                   agent_config=agent_config,
                   max_num_steps=max_num_steps,
                   parsing_failure_th=parsing_failure_th,
                   repeating_action_failure_th=repeating_action_failure_th,
                   task_name=task_name,
                   log_path=log_path,
                   start_test_id=start_test_id,
                   test_case_count=test_case_count,
                   label_path=label_path,
                   llm=llm,
                   baseline_dir=baseline_dir
                   )
