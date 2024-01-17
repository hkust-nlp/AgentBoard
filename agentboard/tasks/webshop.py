import pdb

import openai
import json
import sys
import os
import re
import requests
import logging
from pathlib import Path
from bs4 import BeautifulSoup
from bs4.element import Comment
from llm import load_llm
from dotenv import load_dotenv
from agents import load_agent
from environment import load_environment
from utils.common_exception import PageNumberError

from agents.vanilla_agent import VanillaAgent
from common.registry import registry
from utils.logging.logger import TaskLogger

from .base_task import BaseTask


@registry.register_task("webshop")
class EvalWebshop(BaseTask):
    def __init__(self,
                max_num_steps,
                start_idx,
                end_idx,
                task_name=None,
                llm_name ="gpt",
                agent_name ="VanillaAgent",
                output_log_dir ="./trajectory_log/",
                llm_config=None,
                agent_config=None,
                env_config=None,
                llm=None,
                baseline_dir = None,
                log_path = None
                ):
        
        super().__init__()
        
        if llm is None:
            llm = load_llm(llm_name, llm_config)
        self.task_name = task_name
        self.agent = load_agent(agent_name, agent_config, llm)
        self.max_num_steps = max_num_steps
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.llm_config = llm_config
        self.output_log_dir = output_log_dir
        self.llm = llm
        self.env_cfg = env_config
        
        self.baseline_dir = baseline_dir
        
        self.label_path = env_config.get("label_path", None)
        
        self.agentboard = TaskLogger(task_name="webshop", log_path=log_path, max_num_steps=self.max_num_steps, baseline_dir=self.baseline_dir)
    
    def load_annotation(self, path):
        all_annotations = None  
        difficulty = []
        with open(path, 'r') as f:
            for line in f:
                if line.strip() == '':
                    continue
                line = json.loads(line.strip())
                if "difficulty" in line:
                    difficulty.append(line["difficulty"])
                else:
                    raise ValueError("No difficulty in annotation file")
        return all_annotations, difficulty

    def clean_action(self, message):
        pattern = r"(click\[|search\[).*"
        match = re.search(pattern, message)
        if match:
            action = message[match.start():]
            return action
        else:
            return message

    def evaluate_env(self, idx):
        action = 'reset[]'
        last_ava_ob = ''
        max_num_steps = self.max_num_steps
        reward = 0.
        done = 0
        last_reward = 0.
        grounding_acc_count = 0
        score_change_record = []
        trajectory = []
        
        for step_id in range(max_num_steps):
            if step_id == 0:
                self.env.sub_reward = 0.0
                self.env.reward = 0.0  
            try:
                observation, reward, done, sub_reward, grounding = self.env.step(idx, action)
                last_ava_ob = observation
                if grounding:
                    grounding_acc_count += 1
                if sub_reward > last_reward:
                    score_change_record.append((step_id, sub_reward))
                    self.env.sub_reward = sub_reward
                last_reward = sub_reward
            except AssertionError:
                observation = f'You can only click the button showed in the observation. Elements within square brackets (like [Buy Now]) indicate clickable buttons or links. The recent observation is: \n{last_ava_ob}'
            except PageNumberError:
                observation = f'The page number is limited to 5, please choose another action. The recent observation is: \n{last_ava_ob}'
            except Exception as e:
                print(f"Unexpected error occurred: {repr(e)}")
                break
            if step_id:
                if isinstance(self.agent, VanillaAgent):
                    self.agent.update(action=action, state=observation)
                else:
                    raise TypeError("Agent type is wrong")
            else:
                goal = self.env.get_goal()
                self.agent.reset(goal, init_obs=observation, init_act=action)
                trajectory.append({"Goal":goal, "id":0})
                trajectory.append({"Observation":observation, "id":0})
            trajectory.append({"Action":action, "id":step_id})
            trajectory.append({"Observation":observation, "id":step_id})
            trajectory.append({"Progress Rate":self.env.sub_reward, "id":step_id})
            if done:
                id = int(idx.split("_")[1])
                env_details = {"task_name": "webshop", "goal": self.agent.goal, "difficulty": self.difficulties[id]}
                self.agentboard.log_example(id, reward==1, self.env.sub_reward, grounding_acc_count / (step_id + 1), score_change_record, env_details, trajectory)

                return reward, self.env.sub_reward, grounding_acc_count / (step_id + 1), score_change_record, step_id + 1
            succ, message = self.agent.run(init_prompt_dict=None)
            action = self.clean_action(message)
        # Send a Failed request URL
        url = 'http://127.0.0.1:3000/failed'
        request_id = 'Resquest: ' + url
        print("Failed! Reached the max step")
        headers = {'X-Request-ID': request_id}
        response = requests.head(url, headers=headers)
        id = int(idx.split("_")[1])
        env_details = {"task_name": "webshop", "goal": self.agent.goal, "difficulty": self.difficulties[id]}
        try: example_prompt = self.agent.get_example_prompt()
        except: example_prompt = None  
        
        progress_rate = self.env.sub_reward
        
        self.agentboard.log_example(id, bool(done), progress_rate, grounding_acc_count / (step_id + 1), score_change_record, env_details, trajectory, example_prompt)
        
        return 0, progress_rate, grounding_acc_count / (step_id + 1), score_change_record, step_id + 1

    def evaluate(self):
        _, self.difficulties = self.load_annotation(self.label_path)
        self.env = load_environment('webshop', self.env_cfg)
        score_list = []  # score list
        all_progress_rates = []  # sub-reward list
        grounding_acc_list = []
        score_states = []
        cnt = 0
        for id in range(self.start_idx, self.end_idx):
            try:
                score, progress_rate, grounding_acc, score_state, steps = self.evaluate_env(f'fixed_{id}')
            except Exception as e:
                score = 0
                cnt += 1
                print(f"Unexpected error occurred: {repr(e)}")
                break
            score_list.append(score)
            all_progress_rates.append(progress_rate)
            grounding_acc_list.append(grounding_acc)
            score_states.append(score_state)

        difficulties = self.difficulties
        success_rate = [1 if x == 1 else 0 for x in score_list]
        sr = sum(success_rate) * 1.0 / len(success_rate)
        pr = sum(all_progress_rates) * 1.0 / len(all_progress_rates)
        gr = sum(grounding_acc_list) * 1.0 / len(grounding_acc_list)

        hard_sr = [sr for sr, difficulty in zip(success_rate, difficulties) if difficulty == "hard"]
        hard_sr = sum(hard_sr) / len(hard_sr) if len(hard_sr) > 0 else 0

        hard_pr = [pr for pr, difficulty in zip(all_progress_rates, difficulties) if difficulty == "hard"]
        hard_pr = sum(hard_pr) / len(hard_pr) if len(hard_pr) > 0 else 0

        easy_sr = [sr for sr, difficulty in zip(success_rate, difficulties) if difficulty == "easy"]
        easy_sr = sum(easy_sr) / len(easy_sr) if len(easy_sr) > 0 else 0

        easy_pr = [pr for pr, difficulty in zip(all_progress_rates, difficulties) if difficulty == "easy"]
        easy_pr = sum(easy_pr) / len(easy_pr) if len(easy_pr) > 0 else 0

        
        self.agentboard.log_summary(sr, pr, gr, score_states, hard_sr, hard_pr, easy_sr, easy_pr)

        return [1 if x == 1 else 0 for x in score_list], all_progress_rates, grounding_acc_list, score_states, easy_sr, hard_sr, easy_pr, hard_pr

    @classmethod
    def from_config(cls,
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    llm=None
                    ):
        max_num_steps = run_config.get('max_num_steps', 20)
        baseline_dir = run_config.get("baseline_dir", "data/baseline_results")
        output_log_dir = run_config.get("log_path", "./results/")
        agent_name = agent_config.get("name", "VanillaAgent")
        llm_name = llm_config.get("name", "gpt")
        task_name = env_config.get("name", "webshop")
        start_idx = env_config.get('start_idx', 1)
        end_idx = env_config.get('end_idx', 20)
        log_path = run_config.get("log_path", None)
        
        return cls(max_num_steps=max_num_steps,
                   start_idx=start_idx,
                   end_idx=end_idx,
                   task_name=task_name,
                   llm_name=llm_name,
                   agent_name=agent_name,
                   output_log_dir=output_log_dir,
                   llm_config=llm_config,
                   agent_config=agent_config,
                   env_config=env_config,
                   llm=llm,
                   baseline_dir=baseline_dir,
                   log_path = log_path
                   )

