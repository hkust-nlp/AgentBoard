import os
import numpy as np

from llm import load_llm
from agents import load_agent
from environment import load_environment
from common.registry import registry



def get_textworld_config(game_file, 
                         game_name,
                         seed):
    
    game_config = {"game_file": game_file,
                   "game_name": game_name,
                   "seed": seed,
    }
    return game_config


@registry.register_task("textworld")
class EvalTextworld:
    def __init__(self,
                 game_dir,
                 test = True,
                 seed = 1234,
                 env_num_per_task = 1,
                 max_num_trials = 4,
                 max_num_steps = 20,
                 llm_name = "gpt",
                 llm_config = None,
                 agent_name = "POMDPAgent",
                 agent_config = None,
                 game_name = ["tw-simple"],
                 ):
    
        self.game_dir = game_dir
        self.test = test
        self.max_num_trials = max_num_trials
        self.max_num_steps = max_num_steps
        
        llm = load_llm(llm_name, llm_config)
        self.agent = load_agent(agent_name, agent_config, llm)

        self.seeds = np.array(range(env_num_per_task)) * 111 + seed # generate seeds for each environment
        self.game_name = game_name
        self.env_configs = self.get_all_environment_configs()
        
    def get_all_environment_configs(self):
        env_configs = []
        for game_name in self.game_name:
            for seed in self.seeds:
                game_file = os.path.join(self.game_dir, game_name + '_' + str(seed) + ".z8")
                game_config = get_textworld_config(game_file, game_name, seed)
                
                env_configs.append(game_config)
                
        return env_configs
    
    def evaluate_env(self, id):
        env = load_environment("textworld", self.env_configs[id])
        init_obs = env._get_obs()
        goal = env._get_goal()
        self.agent.reset(goal, init_obs)
        
        print("Goal: {}".format(self.agent.goal))
        print("Init obs: {}".format(self.agent.init_obs))

        max_steps = self.max_num_steps
        for step_id in range(max_steps):
            success, action = self.agent.run()
            if not success:
                break
            print("Step {}: Action: {}".format(step_id, action))
            state, reward, done, infos = env.step(action)
            print("Step {}: State: {}".format(step_id, state))
            print("Step {}: Reward: {}, Is done: {}".format(step_id, reward, done))
            self.agent.update(action, state, reward)
            if done:
                return True, step_id + 1 # return success, completion steps
            
        return False, None
    
    def evaluate(self):
        num_envs = len(self.env_configs)
        num_success = 0
        num_steps = []
        for id in range(num_envs):
            success, steps = self.evaluate_env(id)
            if success:
                num_success += 1
                num_steps.append(steps)
            print("Env {}: Success: {}, Steps: {}".format(id, success, steps))
            
        # calculate success rate within 1, 2, ..., max_num_steps
        
        success_nums = [0] * self.max_num_steps
        for i in range(self.max_num_steps):
            for num_step in num_steps:
                if num_step <= i + 1:
                    success_nums[i] += 1
        
        success_rate = [success_num / num_envs for success_num in success_nums]
        
        return success_rate
        
    
    @classmethod
    def from_config(cls, 
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    ):
        
        max_num_trials = run_config.get("max_num_trials", 4)
        max_num_steps = run_config.get("max_num_steps", 20)
        env_num_per_task = run_config.get("env_num_per_task", 1)
        
        llm_name = llm_config.get("name", "gpt")
        agent_name = agent_config.get("name", "POMDPAgent")
        
        env_name = env_config.get("name", "textworld")
        assert env_name == "textworld" 
        
        test = env_config.get("test", True)
        game_dir = env_config.get("game_dir")
        game_name = env_config["game_name"]
        seed = env_config.get("seed", 1234)
    
        return cls(game_dir = game_dir,
                   test = test,
                   seed = seed,
                   env_num_per_task = env_num_per_task,
                   max_num_trials = max_num_trials,
                   max_num_steps = max_num_steps,
                   llm_name = llm_name,
                   llm_config = llm_config,
                   agent_name = agent_name,
                   agent_config = agent_config,
                   game_name = game_name,
                )
                   
                   
                
                 
    
        
        
        
        
        
        
        
        
        