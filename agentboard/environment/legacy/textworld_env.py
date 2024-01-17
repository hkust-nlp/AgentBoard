import gym
import textworld.gym
import subprocess
import os
import re
from environment.base_env import BaseEnvironment
from common.registry import registry

@registry.register_environment("textworld")
class TextWorld(BaseEnvironment):
    def __int__(self, game_file=None,
                 max_episode_steps=50, 
                 game_name="tw-simple",
                 seed=1234,
                 game_config=None,
                 ):
        
        super().__init__()
        self.game_file = game_file
        self.max_episode_steps = max_episode_steps
        
        self.game_name = game_name
        self.seed = seed
        self.game_config = game_config
        
        
        if os.path.exists(self.game_file):
            print("Game file already made.")
        else:
            self.make_game(game_name, game_file, game_config, seed)
        
        request_infos = textworld.EnvInfos(
            admissible_commands=True,  # All commands relevant to the current state.
            entities=True              # List of all interactable entities found in the game. 
        )
        self.env_id = textworld.gym.register_game(self.game_file, request_infos)
        self.env = gym.make(self.env_id, new_step_api=True, max_episode_steps=max_episode_steps)
        
        self.reset()
        
        
        
    
    def _get_info(self):
        return self.infos
    
    def _get_obs(self):
        return self.states[-1]
    
    def _get_goal(self):
        return self.goal
    
    def _get_history(self):
        return self.history
    
    def _get_action_space(self):
        return self.infos["admissible_commands"] + ["check valid actions"] # return a list of valid actions
    
    def _is_done(self):
        return self.done
    
    def clean_up_text(self, text):
        cleaned_text = re.sub(r'\n', '', text).replace('>', '')  
        cleaned_text = re.sub(r' {2,}', ' ', cleaned_text)  
        return cleaned_text
    
    def update(self, action, obs, reward, done, infos): # update the environment after taking an action
        for k, v in infos.items():
            self.infos[k] = v
        
        self.reward = reward
        self.done = done
        self.history.append(("action", action))
        self.history.append(("reward", reward))
        self.history.append(("state", obs))
        self.states.append(obs)
        
        self.steps += 1
        
        self.infos["goal"] = self.goal
        self.infos["states"] = self.states
        self.infos["history"] = self.history
        self.infos["steps"] = self.steps
        self.infos["state"] = self.states[-1]
    
    def update_info(self, action, info):
        self.history.append(("action", action))
        self.history.append(("reward", self.reward))
        self.history.append(("state", info))
        self.states.append(info)
        
        self.steps += 1
        self.infos["goal"] = self.goal
        self.infos["states"] = self.states
        self.infos["history"] = self.history
        self.infos["steps"] = self.steps
        self.infos["state"] = self.states[-1]
        
    
    def reset(self):
        obs, infos = self.env.reset()
        # self.env.render() # not sure if this is necessary, seems to open an environment in command line
        self.goal, self.init_obs = self.get_goal_and_obs(obs) # g & s0
        self.infos = infos # record last step info
        self.states = [self.init_obs]  # record a stream of states
        self.history = [("state", self.init_obs)] # record a stream of s0, a0, r0, s1, a1, r1, ...
        self.steps = 0
        
        self.infos["goal"] = self.goal
        self.infos["states"] = self.states
        self.infos["history"] = self.history
        self.infos["steps"] = self.steps
        self.infos["state"] = self.states[-1]
        
        self.reward = None
        self.done = False
    
    def validate_check_valid_actions(self, action):
        action = action.strip().lower()
        if "check" in action and "action" in action:
            return True
        else:
            return False
        
    def step(self, action):
        if self.validate_check_valid_actions(action): # add a special action to check valid actions
            obs = "You can take the following actions: " + ", ".join(self._get_action_space())
            self.update_info(action, obs) 
            return self._get_obs(), self.reward, self.done, self.infos
        else:   
            obs, reward, done, truncated, infos = self.env.step(action) # five returns using the new step API
            obs = self.clean_up_text(obs) # remove formats of the text, including > and \n
            # self.env.render() # not sure if this is necessary, seems to update action in command line
            self.update(action, obs, reward, done, infos)
            return self._get_obs(), self.reward, self.done, self.infos
        
    def make_game(self, game_name, game_file, game_config, seed):
        command_input = ["tw-make", game_name, "--output", game_file, "--seed", str(seed)]
        for k, v in game_config.items():
            if isinstance(v, bool):
                if v:
                    command_input.extend(["--" + k])
            else:
                command_input.extend(["--" + k, str(v)])
            
        try:
            output = subprocess.run(" ".join(command_input), shell=True, check=True)
            print("Game file created.")
        except subprocess.CalledProcessError as e:
            print("Error creating game file.")
            raise e
        
        return
    
    
    def get_goal_and_obs(self, init_obs):
        cleaned_text = re.sub(r'[-_=\\\/\$\|>]', '', init_obs).strip() # Remove the logo of the game
        cleaned_text = re.sub(r'\n{2,}', '\n', cleaned_text)  
        goal = cleaned_text.strip().split('\n')[0]# Get the first line of the description, often the goal of the game.
        init_obs = ' '.join(cleaned_text.strip().split('\n')[1:]) # Remove the first line of the description
        init_obs = self.clean_up_text(init_obs)
        return goal, init_obs
    
    @classmethod
    def from_config(cls, cfg):
        game_file = cfg.get("game_file")
        game_config = dict()
        seed = cfg.get("seed", 1234)
        game_name = cfg.get("game_name", "tw-simple") # The name of the game: tw-simple, tw-cooking, tw-treasure_hunter, tw-coin_collector
        
        if game_name == "custom":
            
            game_config["world_size"] = cfg.get("world_size", 5) # The size of the game’s world. Default: 5
            game_config["quest_length"] = cfg.get("quest_length", 5) # The length of the quest. Default: 5
            game_config["quest_breadth"] = cfg.get("quest_breadth", 2) # The breadth of the quest. Default: 2
            game_config["quest_min_depth"] = cfg.get("quest_min_depth", 2) # The minimum depth of the quest. Default: 2
            game_config["quest_max_depth"] = cfg.get("quest_max_depth", 5) # The maximum depth of the quest. Default: 5
            
        if game_name == "tw-simple":
            game_config["rewards"] = cfg.get("rewards", "dense")# The reward frequency: dense, balanced, or sparse.
            game_config["goal"] = cfg.get("goal", "brief") # The description of the game’s objective shown at the beginning of the game: detailed, bried, or none.
            game_config["test"] = cfg.get("test", True) # Whether to use the test set or the training set.
        
        if game_name == "tw-cooking":
            game_config["recipe"] = cfg.get("recipe", 1) # Number of ingredients in the recipe. Default: 1
            game_config["take"] = cfg.get("recipe", 1)  # Number of objects to take. Default: 1
            game_config["go"] = cfg.get("go", 1) # Number of locations in the game (1, 6, 9, or 12). Default: 1
            game_config["cook"] = cfg.get("cook", False) # Whether some ingredients need to be cooked.
            game_config["open"] = cfg.get("open", False) # Whether containers/doors need to be opened.
            game_config["cut"] = cfg.get("cut", False) #Whether some ingredients need to be cut.
            game_config["drop"] = cfg.get("drop", False) #Whether the player’s inventory has limited capacity.
            game_config["recipe-seed"] = cfg.get("seed", 1234)
            game_config["split"] = cfg.get("split", "test") #Possible choices: train, valid, test
        
        if game_name == "tw-coin_collector":
            game_config["level"] = cfg.get("level", 1) # The level of difficulty of the game Must be between 1 and 300 (included).
        
        if game_name == "tw-treasure_hunter":
            game_config["level"] = cfg.get("level", 1)  # The level of difficulty of the game Must be between 1 and 300 (included).
        
        
        env = cls(game_file=game_file, 
                   game_name=game_name,
                   game_config=game_config,
                   seed=seed,
                   )
        return env
    

