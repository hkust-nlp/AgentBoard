import os
import time
import numpy as np
import json
from copy import deepcopy
from typing import Any, Dict, List, Union

from llm import load_llm
from agents import load_agent
from environment import load_environment
from utils.tool.data_utils import ToolDataset
from tasks.base_task import BaseTask
from common.registry import registry

from utils.logging.logger import TaskLogger
from utils.logging.agent_logger import AgentLogger

from utils.tool.helpers import (
    extract_action_name_and_action_input,
    extract_sheet_number,
    check_credentials,
    contains_network_error,
)

logger = AgentLogger(__name__)

@registry.register_task("tool")
class EvalTool(BaseTask):
    def __init__(self,
                 run_config = None,
                 llm_config = None,
                 agent_config = None,
                 env_config = None,
                 llm = None,
                 baseline_dir = None,
                 max_num_steps = 20,
                 log_path = None
                 ):

        self.run_config = run_config
        self.agent_config = agent_config
        self.env_config = env_config
        self.max_num_steps = max_num_steps
        if llm is None:
            llm = load_llm( llm_config["name"] , llm_config)

        self.init_prompt_path = agent_config["init_prompt_path"]
        agent_config["init_prompt_path"] = None

        self.agent = load_agent( agent_config["name"] , agent_config, llm)

        self.seeds = np.array(range( run_config["env_num_per_task"] )) * 111 + env_config["seed"] # generate seeds for each environment

        
        self.baseline_dir = baseline_dir
        
        
        self.agentboard = TaskLogger(task_name= env_config["name"], log_path=log_path, max_num_steps=self.max_num_steps, baseline_dir=self.baseline_dir)

        # check credentials for movie, todo and sheet
        check_credentials()

    def evaluate(self):
        # get dataset
        self.dataset = self.load_dataset(self.env_config["name"],
                                         self.env_config["dataset_dir"],
                                         self.env_config["result_dir"])
        
        difficulties = self.dataset.difficulties
        dataset_size = len(self.dataset)
        success_rates = []
        progress_rates = []
        grounding_scores = []
        score_state_records = []
        num_steps = []

        for id in range(dataset_size):
            success, steps, progress_rate, output, grounding_acc, score_change_record = self.evaluate_env(id)

            if success:
                success_rates.append(1)
            else:
                success_rates.append(0)
            progress_rates.append(progress_rate)
            grounding_scores.append(grounding_acc)
            score_state_records.append(score_change_record)
            num_steps.append(steps)
            
            logger.finish("Example {} | Success: {} , Progress Rate: {} , Steps: {}\n".format(id, success, progress_rate, steps))

        sr = sum(success_rates) * 1.0 / len(success_rates)
        pr = sum(progress_rates) * 1.0 / len(progress_rates)
        gr = sum(grounding_scores) * 1.0 / len(grounding_scores)

        hard_sr = [sr for sr, difficulty in zip(success_rates, difficulties) if difficulty == "hard"]
        hard_sr = sum(hard_sr) / len(hard_sr) if len(hard_sr) > 0 else 0

        hard_pr = [pr for pr, difficulty in zip(progress_rates, difficulties) if difficulty == "hard"]
        hard_pr = sum(hard_pr) / len(hard_pr) if len(hard_pr) > 0 else 0

        easy_sr = [sr for sr, difficulty in zip(success_rates, difficulties) if difficulty == "easy"]
        easy_sr = sum(easy_sr) / len(easy_sr) if len(easy_sr) > 0 else 0

        easy_pr = [pr for pr, difficulty in zip(progress_rates, difficulties) if difficulty == "easy"]
        easy_pr = sum(easy_pr) / len(easy_pr) if len(easy_pr) > 0 else 0

        self.agentboard.log_summary(sr, pr, gr, score_state_records, hard_sr, hard_pr, easy_sr, easy_pr)

        return success_rates, progress_rates, grounding_scores, score_state_records,easy_sr, hard_sr, easy_pr, hard_pr

    def evaluate_env(self, id):
        dataset = self.dataset
        env_config = self.env_config.copy()

        # dataset_i is passed to env_config, and then passed to initialize env 
        dataset_i = dict()
        dataset_i["goal"] = dataset.goals[id]
        dataset_i["ground_truth"] = dataset.ground_truths[id]
        dataset_i["ground_truth_subgoals"] = dataset.ground_truth_subgoals[id]
        dataset_i["tool"] = dataset.tools[id]
        if hasattr(dataset, "action_path"):
            # sheet task does not have action_path
            dataset_i["ground_truth_action_path"] = dataset.action_path[id]

        if dataset_i["tool"] == "weather":
            #! Same operation for todo
            dataset_i["current_date"] = dataset.init_configs[id]["current_date"]
            dataset_i["current_location"] = dataset.init_configs[id]["current_location"]
        env_config["dataset"] = dataset_i
        
        self.env = load_environment( dataset_i["tool"] , env_config)

        # get task infomation 
        goal = self.dataset.goals[id]
        ground_truth = self.dataset.ground_truths[id]
        tool = self.dataset.tools[id]        
        goal_type = self.dataset.goal_types[id]
        difficulty = self.dataset.difficulties[id]

        action_path = []
        self.env.action_path = action_path


        # set self.agent.init_prompt_dict
        self.agent.init_prompt_dict = json.load( open( "/".join( [self.init_prompt_path, type(self.agent).__name__ ,f"{tool}_prompt.json"] ), "r" ) )
        self.agent.instruction = self.agent.init_prompt_dict["instruction"]
        self.agent.examples = self.agent.init_prompt_dict["examples"]

        if tool == "weather":
            init_obs ="If you want to get the latitude and longitude information of a city, you must call \"get_latitude_longitude\", do not generate it by yourself which maybe wrong. Once you have finished the goal, please remember to take 'finish' action to end this goal." 
            self.agent.reset(goal, init_obs)
        else:
            init_obs = "Once you have finished the goal, please remember to take 'finish' action to end this goal."
            self.agent.reset(goal, init_obs)

        
        if tool == "weather":
            self.env.weather_toolkits.current_date = self.dataset.init_configs[id]["current_date"]
            self.env.weather_toolkits.current_location = self.dataset.init_configs[id]["current_location"]
        elif tool == "todo":
            self.env.todo_toolkits.current_date = self.dataset.init_configs[id]["current_date"]
            self.env.todo_toolkits.current_location = self.dataset.init_configs[id]["current_location"]

        logger.goal("Example {} | Goal: {}".format(id, self.agent.goal))

        max_steps = self.run_config["max_num_steps"]

        if tool == "sheet":
            # For sheet task, we need to open the sheet first
            sheet_name = extract_sheet_number(goal)
            action_auto, observation_auto = self.env.reset_question_env(goal, sheet_name)
            self.agent.update(action = action_auto, state = observation_auto)
            logger.info("Step -1 - Message: {}".format(action_auto))
            logger.info("Step -1 - Observation: {}".format(observation_auto))

        grounding_acc_count = 0
        last_reward = 0.0
        score_change_record = []
        trajectory = []
        trajectory.append({"Goal":goal, "id":0})
        trajectory.append({"Observation":init_obs, "id":0})

        for step_id in range(max_steps):
            
            if tool == "sheet":
                time.sleep(10)

            try: 
                _, message = self.agent.run()
                message = message.strip()

                logger.info("Step {:02} - Message: {}".format(step_id, message))

                action, action_input = extract_action_name_and_action_input(message)

                logger.info("Step {:02} - Action: {}".format(step_id, action))
                logger.info("Step {:02} - Action Input: {}".format(step_id, action_input))

                trajectory.append({"Action": message, "id":step_id})

                if action_input == None:
                    observation, done =  "Format error, please response in the format of  \"Action: [your action] with Action Input: [your action input]" , False
                    reward = self.env.reward
                    self.agent.update(action="", state=observation)
                else:
                    action_with_action_input = "Action: " + action + " with Action Input: " + action_input
                    observation, _, done, _ = self.env.step(action_with_action_input, action_path = action_path)
                    
                    self.agent.update(action=action+" with Action Input: "+action_input, state=observation)
                    
                    reward = self.env.reward

                    if not observation.startswith("ERROR | "):
                        grounding_acc_count += 1.0

                logger.info("Step {:02} - Observation: {}".format(step_id, observation))
                logger.info("Step {:02} - Progress Rate: {}\n".format(step_id, reward))
                trajectory.append({"Observation": observation, "id":step_id})
                trajectory.append({"Progress Rate": reward, "id":step_id})


                if contains_network_error(observation):
                    raise Exception(observation)
                
                if reward > last_reward:
                    score_change_record.append((step_id, reward))
                last_reward = reward

                # Early stop if the agent has finished the task.
                if done:
                    if goal_type == 1 and tool == "todo":
                        output = self.get_todo_status(self.env.todo_toolkits)
                    else:
                        output = observation

                    logger.info("Example {} | Finished with {}".format(id, output))
                    break

            except Exception as e:
                done = False
                output = "Example {} | Error: {}".format(id, str(e))
                logger.info( output )
                # Since there is an Exception, we must break the evaluation of this example.
                break

        if step_id == (max_steps-1) and not done:
            output = "Example {} | Error: Exceed max steps".format(id)
            logger.info(output)
       
        reward = self.env.reward
        # logger.info("Example {} | Progress Rate: {}".format(id, reward))

        if done:
            if goal_type == 1 and tool == "todo":
                success = self.get_todo_score(output, ground_truth) and (reward == 1.0)
            else:
                success = (reward == 1.0)
        else:
            success = False
        
        logger.info("Example {} | Ground Truth: {}".format(id, str(ground_truth)) )
        
        env_details = {"task_name": tool, "goal": goal, "difficulty": difficulty}
        try: example_prompt = self.agent.get_example_prompt()
        except: example_prompt = None  
        
        progress_rate = reward
        self.agentboard.log_example(id, success, progress_rate, grounding_acc_count / (step_id + 1), score_change_record, env_details, trajectory, example_prompt)

        return success, step_id + 1, progress_rate, output, grounding_acc_count / (step_id + 1), score_change_record

    def get_todo_score(self, output, ground_truth):
        current_status = output 
        ground_truth_status = ground_truth
        return current_status == ground_truth_status

    def load_dataset(self, dataset_name, dataset_dir, result_dir):
        dataset_file = os.path.join(dataset_dir, dataset_name, "test.jsonl")

        if dataset_name == "tool-query" or dataset_name == "tool-operation":
            dataset = ToolDataset(test_file=dataset_file)
        else:
            raise NotImplementedError("Dataset {} not implemented".format(dataset_name))

        logger.info(
            "Load dataset {} with {} examples".format(
                dataset_name, len(dataset)
            )
        )
        return dataset

    def clean_answer(self, answer : Union[ List[Dict[str, Any]], Dict[str, Any] ] ):
        # remove all "id" in observation
        new_answer = deepcopy(answer)
        if isinstance(new_answer, list):
            for item in new_answer:
                item.pop("id")
        elif isinstance(new_answer, dict):
            new_answer.pop("id")
        return new_answer

    def get_todo_status(self, tool):
        # get all projects
        _, projects = tool._get_all_projects()
        projects = self.clean_answer(projects)

        # get all tasks
        _, tasks = tool._get_all_tasks()
        tasks = self.clean_answer(tasks)

        result = {
            "projects": projects,
            "tasks": tasks
        }

        return result

    @classmethod
    def from_config(cls,
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    llm = None  
                    ):
        # run_config
        run_config["max_num_trials"] = run_config.get("max_num_trials", 4)
        run_config["max_num_steps"] = run_config.get("max_num_steps", 20)
        run_config["env_num_per_task"] = run_config.get("env_num_per_task", 1)
        run_config["grounding"] = run_config.get("grounding", False)

        # llm config
        llm_config["name"] = llm_config.get("name", "gpt")

        # agent config
        agent_config["name"] = agent_config.get("name", "vanilla")
        agent_config["use_parser"] = llm_config.get("use_parser", True)

        # env config
        env_config["name"] = env_config.get("name", "tool-query")
        assert env_config["name"] in ["tool-query", "tool-operation"]
        env_config["seed"] = env_config.get("seed", 1234)

        baseline_dir = run_config.get("baseline_dir", "data/baseline_results")

        max_num_steps = run_config.get("max_num_steps", 20)
        
        log_path = run_config.get("log_path", None)

        return cls(
                    run_config = run_config,
                    llm_config = llm_config,
                    agent_config = agent_config,
                    env_config = env_config,
                    llm = llm,
                    baseline_dir = baseline_dir,
                    max_num_steps = max_num_steps,
                    log_path = log_path
                   )
