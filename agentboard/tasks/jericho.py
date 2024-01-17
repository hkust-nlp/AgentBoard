import os
import json
import numpy as np

from llm import load_llm
from agents import load_agent
from environment import load_environment
from common.registry import registry
from utils.logging.logger import TaskLogger
from utils.logging.agent_logger import AgentLogger

from .base_task import BaseTask

logger = AgentLogger(__name__)


@registry.register_task("jericho")
class EvalJericho(BaseTask):
    
    # default problem config: 
    
    
    def __init__(self,
                 llm_name = "gpt",
                 llm_config = None,
                 agent_name = "POMDPAgent",
                 agent_config = None,
                 env_config = None,
                 max_num_steps = 20,
                 llm = None,
                 baseline_dir = None,
                 log_path = None
                ):
        if llm is None:
            llm = load_llm(llm_name, llm_config)
        self.agent = load_agent(agent_name, agent_config, llm)
        self.game_name = env_config.get("game_name", [])
        self.game_dir = env_config.get("game_dir", None ) # list of game levels
        self.label_path = env_config.get("label_path", None)
        
        self.env_configs = self.get_all_environment_configs(env_config=env_config)
        self.max_num_steps = max_num_steps
        
        self.baseline_dir = baseline_dir
        
        self.agentboard = TaskLogger(task_name="jericho", log_path=log_path, max_num_steps=self.max_num_steps, baseline_dir=self.baseline_dir)
    
    def load_annotation(self, path):
        all_annotations = []
        difficulty = []
        with open(path, 'r') as f:
            for line in f:
                if line.strip() == '':
                    continue
                line = json.loads(line.strip())
                if "subgoals" in line and "subgoals_1" not in line:
                    all_annotations.append(line["subgoals"])
                else:
                    for key in line:
                        annotation = []
                        if "subgoals" in key:
                            annotation.append(line[key])
                    all_annotations.append(annotation)
                    
                if "difficulty" in line:
                    difficulty.append(line["difficulty"])
                else:
                    raise ValueError("No difficulty in annotation file")
        return all_annotations, difficulty
    
    
    def load_seq(self, path):
        all_seqs = []
        with open(path, 'r') as f:
            for line in f:
                if line.strip() == '':
                    continue
                all_seqs.append(line.strip())
        return all_seqs
    
    
    def get_all_environment_configs(self, env_config):
        
        if self.label_path is not None:
            annotations, difficulties = self.load_annotation(self.label_path)  # todo : fix jericho beyond here
        iter = 0
        env_configs = []
        for game in self.game_name:
            problem_config = env_config.copy()
            problem_config["game_name"] = game
            if game not in ["afflicted", "anchor", "snacktime", "partyfoul"]:
                problem_config["game_file"] = os.path.join(self.game_dir, game + ".z5")
            else:
                problem_config["game_file"] = os.path.join(self.game_dir, game + ".z8")
            problem_config["obs_to_reward"] = annotations[iter]
            problem_config["difficulty"] = difficulties[iter]
            env_configs.append(problem_config)
            iter += 1
        return env_configs
    
    def parse_action(self, action): # in case of action is to long results in buffer overflow
        action = action.split(',')[0]
        action = action.split('.')[0]
        action_words = action.split(' ')
        action = " ".join(action_words[:20])
        return action
    
    def evaluate_env(self, id):
        env = load_environment("jericho", self.env_configs[id])
        init_obs = env._get_obs()
        goal = env._get_goal()
        self.agent.reset(goal, init_obs)
        
        logger.goal("Example {} | Goal: {}".format(id, self.agent.goal))
        logger.info("Step {:02} - Message: {}".format(0, init_obs))
        
        max_steps = self.max_num_steps
        reward = 0
        last_reward = 0
        grounding_acc_count = 0
        score_change_record = [] 
        
        trajectory = []
        trajectory.append({"Goal":goal, "id":0})
        trajectory.append({"Observation":init_obs, "id":0})   
         
    
        for step_id in range(max_steps):
            
            success, action = self.agent.run()
            
            if not success:
                break
            action = self.parse_action(action)
            
            logger.info("Step {:02} - Action: {}".format(step_id, action))
            trajectory.append({"Action":action, "id":step_id})
            
            state, reward, done, infos = env.step(action)
            trajectory.append({"Observation":state, "id":step_id})
            trajectory.append({"Progress Rate":reward, "id":step_id})
            
            if infos.get("action_is_valid", False): 
                grounding_acc_count += 1
            
            if reward > last_reward:
                score_change_record.append((step_id, reward))
            last_reward = reward
            
            logger.info("Step {:02} - Observation: {}".format(step_id, state))
            logger.info("Step {:02} - Progress Rate: {}\n".format(step_id, reward))
            self.agent.update(action, state)
            if done:
                env_details = {"task_name": env.game_name, "goal": self.agent.goal, "difficulty": env.difficulty}
                
                progress_rate = reward
                
                self.agentboard.log_example(id, True, progress_rate, grounding_acc_count / (step_id + 1), score_change_record, env_details, trajectory)

                return env.won, progress_rate, step_id + 1, grounding_acc_count / (step_id + 1), score_change_record # return success, completion steps
            
        env_details = {"goal": self.agent.goal, "task_name": env.game_name, "difficulty": env.difficulty}
        try: example_prompt = self.agent.get_example_prompt()
        except: example_prompt = None  
        
        progress_rate = reward
        
        self.agentboard.log_example(id, False, progress_rate, grounding_acc_count / (step_id + 1), score_change_record, env_details, trajectory, example_prompt)
        
        return False, progress_rate, step_id + 1, grounding_acc_count / (step_id + 1), score_change_record
    
    def evaluate(self):
        num_envs = len(self.env_configs)
        success_rate = []
        num_steps = []
        all_progress_rates = []
        score_state_records = []
        grounding_accs = []
        difficulties = []
        
        for id in range(num_envs):
            
            success, progress_rate, steps, grounding_acc_count, score_change_record = self.evaluate_env(id)
            all_progress_rates.append(progress_rate)
            grounding_accs.append(grounding_acc_count)
            score_state_records.append(score_change_record)
            difficulties.append(self.env_configs[id]["difficulty"])

            if success:
                success_rate.append(1)
            else:
                success_rate.append(0)
            logger.finish("Example {} | Success: {} , Progress Rate: {} , Steps: {}\n".format(id, success, progress_rate, steps))

        sr = sum(success_rate) * 1.0 / len(success_rate)
        pr = sum(all_progress_rates) * 1.0 / len(all_progress_rates)
        gr = sum(grounding_accs) * 1.0 / len(grounding_accs)

        hard_sr = [sr for sr, difficulty in zip(success_rate, difficulties) if difficulty == "hard"]
        hard_sr = sum(hard_sr) / len(hard_sr) if len(hard_sr) > 0 else 0

        hard_pr = [pr for pr, difficulty in zip(all_progress_rates, difficulties) if difficulty == "hard"]
        hard_pr = sum(hard_pr) / len(hard_pr) if len(hard_pr) > 0 else 0

        easy_sr = [sr for sr, difficulty in zip(success_rate, difficulties) if difficulty == "easy"]
        easy_sr = sum(easy_sr) / len(easy_sr) if len(easy_sr) > 0 else 0

        easy_pr = [pr for pr, difficulty in zip(all_progress_rates, difficulties) if difficulty == "easy"]
        easy_pr = sum(easy_pr) / len(easy_pr) if len(easy_pr) > 0 else 0


        self.agentboard.log_summary(sr, pr, gr, score_state_records, hard_sr, hard_pr, easy_sr, easy_pr)
        
        return success_rate, all_progress_rates, grounding_accs, score_state_records, easy_sr, hard_sr, easy_pr, hard_pr
    
    @classmethod
    def from_config(cls, 
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    llm = None,
                    ):
        env_name = env_config.get("name", "jericho")
        assert env_name == "jericho"
         
        max_num_steps = run_config.get("max_num_steps", 20)
        baseline_dir = run_config.get("baseline_dir", "data/baseline_results")
        llm_name = llm_config.get("name", "gpt")
        agent_name = agent_config.get("name", "POMDPAgent")
        log_path = run_config.get("log_path", None)
        
        return cls(llm_name = llm_name,
                 llm_config = llm_config,
                 agent_name = agent_name,
                 agent_config = agent_config,
                 env_config = env_config,
                 max_num_steps = max_num_steps,
                 llm = llm,
                 baseline_dir = baseline_dir,
                 log_path = log_path
                )