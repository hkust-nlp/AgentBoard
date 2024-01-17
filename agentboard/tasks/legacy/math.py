import os
import numpy as np

from utils.math.expression_utils import extract_action
import re
from llm import load_llm
from agents import load_agent
from environment import load_environment
import json
import logging
from torch.utils.data import Dataset
from utils.math.data_utils import GSM8k_XL_Dataset, FUNCQA_OH_Dataset, FUNCQA_MH_Dataset
from utils.math.math_utils import check_equal
from tasks.base_task import BaseTask

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

def get_math_config(result_file,
                    dataset_file,
                    dataset,
                    seed):
    
    dataset_config = {
        "result_file": result_file,
        "dataset_file": dataset_file,
        "dataset": dataset,
        "seed": seed,
    }
    
    return dataset_config

class EvalMath(BaseTask):
    def __init__(self,
                 run_config = None,
                 llm_config = None,
                 agent_config = None,
                 env_config = None
                 ):
        self.run_config = run_config

        llm = load_llm( llm_config["name"] , llm_config)
        self.agent = load_agent( agent_config["name"] , agent_config, llm)

        self.seeds = np.array(range( run_config["env_num_per_task"] )) * 111 + env_config["seed"] # generate seeds for each environment
        self.env_config = env_config

    def evaluate(self):
        # get math environment
        self.env = load_environment("math", self.env_config)
        self.dataset = self.load_dataset(self.run_config["dataset_name"],
                                         self.run_config["dataset_dir"],
                                         self.run_config["result_dir"])
        
        dataset_size = len(self.dataset)
        num_success = 0
        num_correct = 0
        num_steps = []
        for id in list(range(dataset_size))[self.dataset.num_skip:]:
            success, correct, steps = self.evaluate_step(id)
            if success:
                num_success += 1
            if correct:
                num_correct += 1
            num_steps.append(steps)
            
            # write to file
            self.dataset.write_result(id, self.dataset.questions[id], self.dataset.ground_truths[id], self.agent.memory)
            
            logger.info("Example {}: Success: {}, Correct: {}, Steps: {}\n".format(id, success, correct, steps))

        success_rate = num_success / dataset_size
        correct_rate = num_correct / dataset_size

        return success_rate, correct_rate


    def evaluate_step(self, id):
        # example = self.dataset[id]
        question = self.dataset.questions[id]
        ground_truth = self.dataset.ground_truths[id]
        self.agent.reset(question, "")

        logger.info("Example {} | Goal: {}".format(id, self.agent.goal))

        max_steps = self.run_config["max_num_steps"]
        for step_id in range(max_steps):
            
            success, message = self.agent.run(mode="thought")
            if not success:
                break
            # thought = message[ 9:message.index("Action")].strip()
            thought = message.strip()
            self.agent.thought = thought
            logger.info("Step {} - Thought: {}".format(step_id, thought) )

            # check if the action is valid
            # action = extract_action(message)
            success, message = self.agent.run(mode="action")
            action = message.strip()
            logger.info("Step {} - Action: {}".format(step_id, action.split("\n")[0]))
            logger.info("Step {} - Action Input: {}".format(step_id, action.split("\n")[1][len("Action Input: "):]))

            observation, done = self.env.step(action)
            logger.info("Step {} - Observation: {}".format(step_id, observation))
            
            self.agent.update(thought, action, observation, done)

            if done:
                logger.info("Example {} | Ground_truth: {}".format(id, ground_truth) )
                if self.is_correct(observation, ground_truth):
                    return True, True, step_id + 1 # return success, completion steps
                else:
                    return True, False, step_id + 1

        return False, False, None

    def is_correct(self, observation, ground_truth) -> bool:
        return check_equal(observation, ground_truth)

    def load_dataset(self, dataset_name, dataset_dir, result_dir):
        dataset_file = os.path.join(dataset_dir, dataset_name, "test.json")
        result_file = os.path.join(result_dir, dataset_name, "result.json")
        if dataset_name == "gsm8k-xl":
            dataset = GSM8k_XL_Dataset(test_file=dataset_file, result_file=result_file)
        elif dataset_name == "funcqa-oh":
            dataset = FUNCQA_OH_Dataset(test_fil=dataset_file, result_file=result_file)
        elif dataset_name == "funcqa-mh":
            dataset = FUNCQA_MH_Dataset(test_file=dataset_file, result_file=result_file)
        else:
            raise NotImplementedError("Dataset {} not implemented".format(dataset_name))

        logger.info(
            "Loaded dataset {} with {} examples".format(
                dataset_name, len(dataset)
            )
        )
        return dataset

    @classmethod
    def from_config(cls,
                    run_config,
                    llm_config,
                    agent_config,
                    env_config):
        # run_config
        run_config["max_num_trials"] = run_config.get("max_num_trials", 4)
        run_config["max_num_steps"] = run_config.get("max_num_steps", 20)
        run_config["env_num_per_task"] = run_config.get("env_num_per_task", 1)    #! what does that mean?
        run_config["result_dir"] = run_config["result_dir"]
        run_config["test"] = run_config.get("test", True)
        # llm config
        llm_config["name"] = llm_config.get("name", "gpt")

        # agent config
        agent_config["name"] = agent_config.get("name", "react")

        # env config
        env_config["name"] = env_config.get("name", "math")
        assert env_config["name"] == "math"
        env_config["seed"] = env_config.get("seed", 1234)
        env_config["dataset"] = run_config.get("dataset_name", "funcqa-mh")

        return cls(
                   run_config=run_config,
                   llm_config=llm_config,
                   agent_config=agent_config,
                   env_config=env_config
                   )
