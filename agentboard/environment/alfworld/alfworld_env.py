from common.registry import registry
import alfworld
import alfworld.agents.environment
import pdb
import yaml
import random
import jsonlines
import re


@registry.register_environment("alfworld")
class AlfWorld:
    def __init__(self,
                 split,
                 base_config,
                 batch_size,
                 seed,
                 label_path
                 ):
        with open(base_config) as reader:
            config = yaml.safe_load(reader)
        env = getattr(alfworld.agents.environment, config["env"]["type"])(config, train_eval=split)
        env.game_files.sort()
        self.env = env.init_env(batch_size)
        self.valid_actions = []
        self.init_obs = ''
        self.isdone = False
        self.env_ob = self.init_obs
        self.finished_sub_goal = []
        self.labeled_data = {}
        self.sub_goal = []
        with open(label_path, 'r+', encoding='utf-8') as f:
            for item in jsonlines.Reader(f):
                self.labeled_data[item["additional_info"]['description']] = item
        random.seed(seed)
        self.cur_task_name = ""
        self.reward = 0.

    def reset(self):

        ob, info = self.env.reset()
        self.valid_actions = info["admissible_commands"][0]

        # self.init_obs = ob[0]
        #ob = '\n'.join(ob[0].split('\n\n')[1:])

        self.init_obs = ('\n'.join(ob[0].split('\n\n')[1:])).split('\n')[0]
        self.goal = ('\n'.join(ob[0].split('\n\n')[1:])).split('\n')[1]
        self.env_ob = self.init_obs
        self.cur_task_name = '/'.join(info['extra.gamefile'][0].split('/')[-3:-1])
        self.sub_goal = self.labeled_data[self.cur_task_name]["subgoals"]
        
        self.difficulty = self.labeled_data[self.cur_task_name]["difficulty"]
        
        self.finished_sub_goal = [0 for i in range(len(self.sub_goal) + 1)]

        self.reward = 0
        self.isdone = False
        return ob, info

    def step(self, action):
        info = None
        done = self.isdone
        if action.endswith('.'):
            action = action[:-1]
        if action == "look":
            observation, _, done, info = self.env.step([action])
            observation = [self.env_ob]
            done = done[0]
        elif action == "check valid actions":
            valid_actions = ", ".join(self.valid_actions)
            observation = [f"Choose an action from these valid actions: {valid_actions}"]
      #  elif action not in self.valid_actions:
      #      observation = "Your action is invalid. Please change a new one."
      #      return observation, self.reward, done, info
        else:
            observation, _, done, info = self.env.step([action])
            done = done[0]
        if "go to" in action or "open" in action:
            if "Nothing happens" not in observation[0]:
                self.env_ob = observation[0]
        if info:
            self.valid_actions = info["admissible_commands"][0]
        observation = self._process_ob(observation[0])
        self.isdone = done
        self._check_temperature_string(s=observation, selected_obs=self.sub_goal)
        self.reward = self._get_reward()
        return observation, self.reward, done, info
    def GetPlanning(self):
        return self.planning

    def GetWorldModel(self):
        return self.world_model

    def _process_ob(self, ob):
        if ob.startswith('You arrive at loc '):
            ob = ob[ob.find('. ') + 2:]
        return ob

    def _get_reward(self):
        if self.isdone:
            return 1.0
        else:
            return sum(self.finished_sub_goal) * 1.0 / len(self.finished_sub_goal)


    def _check_temperature_string(self, s, selected_obs):
        for i, pattern in enumerate(selected_obs):
            #if self.finished_sub_goal[i] == 1.:
            #    continue
            match = re.search(pattern, s)
            if match:
                self.finished_sub_goal[i] = 1.


    def get_action_space(self):
        if "look" not in self.valid_actions:
            self.valid_actions.append("look")
        if "check valid actions" not in self.valid_actions:
            self.valid_actions.append("check valid actions")

        return self.valid_actions

    @classmethod
    def from_config(cls, cfg):
        split = cfg.get("split", "eval_out_of_distribution")
        base_config = cfg.get("base_config", "base_config.yaml")
        batch_size = cfg.get("batch_size", 1)
        seed = cfg.get("seed", 0)
        label_path = cfg.get("label_path", "data/alfworld/alfworld_label.jsonl")
        env = cls(split=split,
                  base_config=base_config,
                  batch_size=batch_size,
                  seed=seed,
                  label_path=label_path)
        return env