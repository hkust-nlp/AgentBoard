import os
import json
import numpy as np
import random
from llm import load_llm
from agents import load_agent
from environment import load_environment
from common.registry import registry


@registry.register_task("game24")
class EvalGame24:   
    
    # default problem config: 
    
    def __init__(self,
                 llm_name = "gpt",
                 llm_config = None,
                 agent_name = "POMDPAgent",
                 agent_config = None,
                 env_config = None,
                 max_num_steps = 20,
                 grounding = False,
                 given_plan = False,
                 llm = None
                #  ablation_dimension = False,
                ):
        if llm is None:
            llm = load_llm(llm_name, llm_config)
        self.agent = load_agent(agent_name, agent_config, llm)
        
        self.env_num_per_task = env_config.get("env_num_per_task", 1)
        self.game_level = env_config.get("game_level", []) # list of game levels
        self.game_file_path = env_config.get("game_file_path", None)
        self.env_configs = self.get_all_environment_configs()
        self.max_num_steps = max_num_steps
    
        self.save_log_path = env_config.get("save_log_path", None)
        if self.save_log_path is not None:
            os.makedirs(self.save_log_path, exist_ok=True)
            
        self.grounding = grounding
        self.given_plan = given_plan
        # self.ablation_dimension = ablation_dimension
        
        
        self.given_plan_path = env_config.get("given_plan_path", None)
        if self.given_plan and self.given_plan_path is not None:
            self.given_plan_annotation = self.load_seq(self.given_plan_path)
    
    
    def load_seq(self, path):
        all_seqs = []
        with open(path, 'r') as f:
            for line in f:
                if line.strip() == '':
                    continue
                all_seqs.append(line.strip())
        return all_seqs
    
    def get_all_environment_configs(self):
        env_configs = []
        
        for i in range(self.env_num_per_task):
            env_configs.append({
                "problem_index": i,
                "game_file_path": self.game_file_path,
            })
                
        return env_configs
    
    def parse_action(self, action):
        if ',' in action:
            action = action.split(',')[0]
        if action == '.':
            action = action.split('.')[0]
        return action
    
    def evaluate_env(self, id):
        env = load_environment("game24", self.env_configs[id])
        init_obs = env._get_obs()
        goal = env._get_goal()
        self.agent.reset(goal, init_obs)
        
        print("Goal: {}".format(self.agent.goal))
        print("Init obs: {}".format(self.agent.init_obs))

        max_steps = self.max_num_steps 
        reward = 0.
        last_reward = 0.
        grounding_acc_count = 0
        score_change_record = []
        
        for step_id in range(max_steps):
            if self.grounding:
                action_space = env._get_action_space()
            else:
                action_space = None
            
            if self.given_plan:
                given_plan_hint = self.given_plan_annotation[id] 
            else:
                given_plan_hint = None
                
            success, action = self.agent.run(action_space=action_space, plan=given_plan_hint)
            
            if not success:
                break
            
            action = self.parse_action(action)
            print("Step {}: Action: {}".format(step_id, action))
            state, reward, done, infos = env.step(action)
            
            if infos.get("action_is_valid", False): 
                grounding_acc_count += 1
            
            if reward > last_reward:
                score_change_record.append((step_id, reward))
            last_reward = reward
            
            print("Step {}: State: {}".format(step_id, state))
            print("Step {}: Reward: {}, Is done: {}".format(step_id, reward, done))
            self.agent.update(action, state, reward)
            if done:
                if done:
                    if self.save_log_path is not None:
                        self.agent.save_log(os.path.join(self.save_log_path, "env_{}.txt".format(id)))
                    return env.won, reward, step_id + 1, grounding_acc_count / (step_id + 1), score_change_record # return success, completion steps
        
        if self.save_log_path is not None:
            self.agent.save_log(os.path.join(self.save_log_path, "env_{}.txt".format(id)))
        return False, reward, None, grounding_acc_count / (step_id + 1), score_change_record
                
    
    def evaluate(self):
        num_envs = len(self.env_configs)
        success_rate = []
        num_steps = []
        all_rewards = []
        score_state_records = []
        grounding_accs = []
        
        for id in range(num_envs):
            success, reward, steps, grounding_acc_count, score_change_record = self.evaluate_env(id)
            all_rewards.append(reward)
            grounding_accs.append(grounding_acc_count)
            score_state_records.append(score_change_record)
            if success:
                success_rate.append(1)
            else:
                success_rate.append(0)
            print("Env {}: Success: {}, Reward: {}, Steps: {}".format(id, success, reward, steps))
            
        # calculate success rate within 1, 2, ..., max_num_steps
        
        # success_nums = [0] * self.max_num_steps
        # for i in range(self.max_num_steps):
        #     for num_step in num_steps:
        #         if num_step <= i + 1:
        #             success_nums[i] += 1
        
        # success_rate = [success_num / num_envs for success_num in success_nums]
        
        return success_rate, all_rewards, grounding_accs, score_state_records
    
    @classmethod
    def from_config(cls, 
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    llm = None
                    ):
        env_name = env_config.get("name", "game24")
        assert env_name == "game24"
         
        max_num_steps = run_config.get("max_num_steps", 20)
        llm_name = llm_config.get("name", "gpt")
        agent_name = agent_config.get("name", "POMDPAgent")
        
        given_plan = run_config.get("given_plan", False)
        grounding = run_config.get("grounding", False)
        
        return cls(llm_name = llm_name,
                 llm_config = llm_config,
                 agent_name = agent_name,
                 agent_config = agent_config,
                 env_config = env_config,
                 max_num_steps = max_num_steps,
                 grounding = grounding,
                 given_plan = given_plan,
                 llm = llm
                )