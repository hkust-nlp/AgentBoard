import nltk

from environment.base_env import BaseEnvironment
from common.registry import registry

@registry.register_environment("game24")
class Game24(BaseEnvironment):
    def __init__(self, problem_index=0, 
                 max_episode_steps=50, 
                 game_name="game24",
                 game_file_path = None,
                 game_config=None,
                 allow_restart=True,
                 ):
        
        super().__init__()
        
        self.max_episode_steps = max_episode_steps
        
        self.game_name = game_name
        
        self.game_config = game_config
        
        self.allow_restart = allow_restart
        
        self.game_file_path = game_file_path
        self.env = self.load_game24_env(problem_index)
        
        self.last_obs = None
        
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
        all_actions = []
        for i in range(len(self.env["present"])):
            for j in range(len(self.env["present"])):
                if i == j:
                    continue
                if i>j:
                    for predicate in ["+","*"]:
                        result = self.execute_action(predicate, [self.env["present"][i], self.env["present"][j]])
                        if result is not None:
                            all_actions.append(str(self.env["present"][i]) + " " + predicate + " " + str(self.env["present"][j]))
                        
                if self.env["present"][j]!=0 and self.env["present"][i] % self.env["present"][j] == 0:
                    all_actions.append(str(self.env["present"][i]) + " / " + str(self.env["present"][j]))
                if self.env["present"][i] >= self.env["present"][j]:
                    all_actions.append(str(self.env["present"][i]) + " - " + str(self.env["present"][j]))
                
                
        
        # for action_temp in all_actions:
        #     try:
        #         action, variables = self.parse_action(action_temp)
        #         result = self.execute_action(action, variables)
        #         if int(result) != result:
        #             all_actions.remove(action_temp)
        #             continue
                
        #     except:
        #         all_actions.remove(action_temp)
        
        all_actions = list(set(all_actions))
        
        return all_actions 
    
    def load_game24_env(self, problem_index):
        with open(self.game_file_path, "r") as f:
            games = f.readlines()
        game = games[problem_index].strip()
        numbers = [int(n) for n in game.split(",")]
        return {"start": numbers, "goal": 24, "present": numbers}
    
    def reset(self):
        self.env["present"] = self.env["start"].copy() # s0
        obs = "Numbers left: " + ", ".join([str(n) for n in self.env["present"]])
        self.init_obs = obs
        self.goal = "Goal is to get " + str(self.env["goal"]) # g
        self.infos = dict() # record last step info
        self.states = [self.init_obs]  # record a stream of states
        self.history = [("state", self.init_obs)] # record a stream of s0, a0, r0, s1, a1, r1, ...
        self.steps = 0
        
        self.infos["goal"] = self.goal
        self.infos["states"] = self.states
        self.infos["history"] = self.history
        self.infos["steps"] = self.steps
        self.infos["state"] = self.states[-1]
        
        self.reward = 0
        self.done = False
        self.won = False

        self.states_to_award = self.build_search_tree()
    
    def list_to_str(self, l):
        return ",".join([str(n) for n in l])
    
    def str_to_list(self, s):
        return [int(n) for n in s.split(",")]
    
    def build_search_tree(self):
        annotated_path = [] # annotate all states that should be rewarded
        start_state = self.env["start"].copy()
        goal = self.env["goal"]
        
        # write a bfs search tree to find the solution
        queue = set()
        all_states = []
        graph = dict()
        start_state.sort()
        queue.add(tuple(start_state))
        
        
        
        while len(queue) > 0:
            state = queue.pop()
            
            all_states.append(state)
            if len(state) == 1:
                continue
                
            for i in range(len(state)):
                for j in range(len(state)):
                    if i == j:
                        continue
                    for predicate in ["+", "-", "*", "/"]:
                        new_state = list(state)
                        new_state.remove(state[i])
                        new_state.remove(state[j])
                        if predicate == "/" and state[j] == 0:
                            continue
                        
                        output = self.execute_action(predicate, [state[i], state[j]])
                        if int(output) != output:
                            continue
                        
                        if output < 0:
                            continue
                        
                        output = int(output)
                        
                        new_state.append(output)
                        
                        new_state.sort()
                        
                        queue.add(tuple(new_state))
                        all_states.append(new_state)
                        
                        if tuple(new_state) not in graph:
                            graph[tuple(new_state)] = [tuple(state)]
                        else:
                            graph[tuple(new_state)].append(tuple(state))
                            
        
        # list all possible paths from start to goal
        
        good_states = set()
        children =  [tuple([goal])]
        
        while len(children) > 0:
            child = children.pop(0)
            good_states.add(child)
            parents = graph.get(child, None)    
            if parents is None:
                continue
            for parent in parents:
                children.append(parent)
        
        # good_states frozen set to set:
        return good_states
                
    
    def execute_action(self, predicate, variables):
        if predicate == "+":
            return variables[0] + variables[1]
        elif predicate == "-":
            return variables[0] - variables[1]
        elif predicate == "*":
            return variables[0] * variables[1]
        else:
            return variables[0] / variables[1]
    
    def parse_action(self, action):
        action = action.split("\n")[0].strip()
        if "=" in action:
            action = action.split("=")[0]
        action_tokens = nltk.word_tokenize(action)
        predicate = None
        for token in action_tokens:
            if token in ["+", "-", "*", "/"]:
                predicate = token
                break
        if predicate is None:
            return None, None
        
        variables = []
        for token in action_tokens:
            if token.isdigit():
                variables.append(int(token))
        if len(variables) != 2:
            return None, None
        
        # for variable in variables:
        #     if variable not in self.env["present"]:
        #         return None, None
        
        return predicate, variables
            
    
    def step(self, action):
        if "check" in action and "action"  in action:
            obs = "Valid actions: " + ", ".join(self._get_action_space())
            self.update_info(action, obs)
            return obs, self.reward, self.done, self._get_info()
        
        predicate, variables = self.parse_action(action)
        
        if predicate is None or variables is None:
            obs = "Invalid action. Please check valid actions." + "Numbers left: " + ", ".join([str(n) for n in self.env["present"]])
            self.update_info(action, obs)
            infos = self._get_info()
            infos["action_is_valid"] = False
            return obs, self.reward, self.done, self._get_info()
        
        valid = True
        valid_variables = self.env["present"].copy()
        for variable in variables:
            if variable not in valid_variables:
                valid = False
                break
            valid_variables.remove(variable)
        # if variables not in self.env["present"]:
        #     valid = False
        
        if not valid:
            obs = "Invalid variables. Please check valid actions." + "You can only use: " + ", ".join([str(n) for n in self.env["present"]])
            self.update_info(action, obs)
            return obs, self.reward, self.done, self._get_info()

        
        if predicate is not None:
            executed_number = self.execute_action(predicate, variables)
            
            if int(executed_number) != executed_number:
                obs = "Cannot obtain an integer. Please try again." + "Numbers left: " + ", ".join([str(n) for n in self.env["present"]])
                self.update_info(action, obs)
                infos = self._get_info()
                infos["action_is_valid"] = False
                return obs, self.reward, self.done, infos
            
            if predicate == "/" and variables[1] == 0:
                obs = "Cannot divide by 0. Please try again." + "Numbers left: " + ", ".join([str(n) for n in self.env["present"]])
                self.update_info(action, obs)
                infos = self._get_info()
                infos["action_is_valid"] = False
                return obs, self.reward, self.done, infos
            
            if executed_number < 0:
                obs = "Cannot obtain a positive number. Please try again." + "Numbers left: " + ", ".join([str(n) for n in self.env["present"]])
                self.update_info(action, obs)
                infos = self._get_info()
                infos["action_is_valid"] = False
                return obs, self.reward, self.done, infos
            
            self.env["present"].remove(variables[0])
            self.env["present"].remove(variables[1])
            self.env["present"].append(int(executed_number))
            won = False
            done = False
            # reward = self.reward if self.reward is not None else 0
            
            
            
            if len(self.env["present"]) == 1:
                done = True
                if executed_number == self.env["goal"]:
                    won = True
                    
            obs = "Numbers left: " + ", ".join([str(n) for n in self.env["present"]])
                
                
            self.update(action, obs, 0, won, done)
            infos = self._get_info()
            infos["action_is_valid"] = True
            return obs, self.reward, self.done, infos
        else:
            obs = "Invalid action. Please try again."
            self.update_info(action, obs)
            infos = self._get_info()
            infos["action_is_valid"] = False
            return obs, self.reward, self.done, infos
    
    
    def update(self, action, obs, reward, won, done): # update the environment after taking an action
        # self.reward = reward
        self.env["present"].sort()
        if tuple(self.env["present"]) in self.states_to_award:
            reward = (4-len(self.env["present"]))/3
            self.reward = max(self.reward, reward)
        else:
            self.reward = max(self.reward, reward)
        self.done = done
        self.history.append(("action", action))
        self.history.append(("reward", self.reward))
        self.history.append(("state", obs))
        self.states.append(obs)
        self.won = won # whether the game is won
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
    
    @classmethod
    def from_config(cls, cfg):
        problem_index = cfg.get("problem_index", 0)
        game_config = dict()
        game_name = cfg.get("game_name", "game24") # The name of the game: tw-simple, tw-cooking, tw-treasure_hunter, tw-coin_collector
        allow_restart = cfg.get("allow_restart", True) # Whether to allow the agent to restart the game.
        game_file_path = cfg.get("game_file_path", None)
        
        return cls(problem_index=problem_index,
                 max_episode_steps=50, 
                 game_name="game24",
                 game_config=game_config,
                 allow_restart=True,
                 game_file_path=game_file_path
                 )