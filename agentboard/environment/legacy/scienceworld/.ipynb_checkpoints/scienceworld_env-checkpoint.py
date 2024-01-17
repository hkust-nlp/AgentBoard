import pdb

import jsonlines
from common.registry import registry
from scienceworld import ScienceWorldEnv
import re
import random
@registry.register_environment("scienceworld")
class Scienceworld:
    def __init__(self,
                 serverPath=None,
                 envStepLimit=100,
                 label_path=''
                 ):
        self.env = ScienceWorldEnv("", serverPath, envStepLimit=envStepLimit)
        self.reward = 0.
        self.done = False
        self.label_path = label_path
        self.labels = {}
        self.cur_label = None
        self.modified_goal = ''
        self.selected_obs = ''
        self.finished_sub_goal = []
        with open(self.label_path, 'r+', encoding='utf-8') as f:
            for item in jsonlines.Reader(f):
                task_name = item["additional_info"]["env_name"]
                var = item["additional_info"]["var"]
                self.labels[f"{task_name}_{var}"] = {
                    "task_name": task_name,
                    "var": var,
                    "modified_goal": item["goal"],
                    "subgoals": item['subgoals'],
                }


    def load(self, task_name, var, simplificationStr):
        env = self.env.load(task_name, var, simplificationStr=simplificationStr)
        self.cur_label = self.labels[f"{task_name}_{var}"]
        self.selected_obs = self.cur_label["subgoals"]
        self.modified_goal = self.cur_label["modified_goal"]
        self.finished_sub_goal = [0 for i in range(len(self.selected_obs))]
        return env
    
    def inventory(self):
        return self.env.inventory()
    
    def parseAction(self, action):
        action = action.strip()
        return action
    
    def step(self, action):
        action = self.parseAction(action)
        observation = ''
        # reward = self.reward
        if action == "check valid actions":
            valid_actions = ", ".join(self.get_action_space())
            observation = f"Choose an action from these valid actions: {valid_actions}"
            return observation, self.reward, self.done, None
        else:
            observation, _, _, info = self.env.step(action)
            self._check_temperature_string(observation, self.selected_obs)
            self.reward = self.get_reward()
            self.done = self._check_is_done(self.selected_obs)
            return observation, self.reward, self.done, info

    def get_action_space(self, abstract=True):

        # print("Valid action-object combinations:")
        svalid_actions = []
        if abstract:
            for a in self.env.getPossibleActions():
                if "reset" not in a:
                    svalid_actions.append(a)
        else:
            valid_actions = self.env.getValidActionObjectCombinationsWithTemplates()
            forbidden_words = ["teleport",
                               "connect",
                               "dunk",
                               "eat",
                               "flush",
                               "close door",
                               ]
            for valid_action in valid_actions:
                v = valid_action['action']
                for fw in forbidden_words:
                    if fw in v:
                        break
                svalid_actions.append(valid_action['action'])
        if "check valid actions" not in svalid_actions:
            svalid_actions.append("check valid actions")
        return svalid_actions

    def getTaskDescription(self):
        return self.env.getTaskDescription()

    def getGoalProgressStr(self):
        return self.env.getGoalProgressStr()

    def getGoldActionSequence(self):
        return self.env.getGoldActionSequence()
    
    def reset(self):
        self.reward = 0.
        self.done = False
        return self.env.reset()

    def _check_temperature_string(self, s, selected_obs):
        for i, pattern in enumerate(selected_obs):
            match = re.search(pattern, s)
            if match:
                self.finished_sub_goal[i] = 1.

    def get_reward(self):
        return sum(self.finished_sub_goal) * 1.0 / len(self.finished_sub_goal)
    
    def _check_is_done(self, selected_obs):
        return sum(self.finished_sub_goal) >= len(selected_obs)
    
    @classmethod
    def from_config(cls, cfg):
        serverPath = cfg.get("serverPath", None)
        envStepLimit = cfg.get("envStepLimit", 50)
        label_path = cfg.get("label_path", '')
        env = cls(serverPath=serverPath,
                  envStepLimit=envStepLimit,
                  label_path=label_path
                   )
        return env






