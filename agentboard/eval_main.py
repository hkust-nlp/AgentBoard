import pdb
import sys
import os
import re
import wandb
import warnings
import yaml
import json
import time
import argparse
from dotenv import load_dotenv
from tasks import load_task
from llm import load_llm
from utils.logging.agent_logger import AgentLogger
from utils.logging.logger import SummaryLogger


logger = AgentLogger(__name__)
warnings.filterwarnings("ignore")

TASKS=["alfworld", "jericho", "pddl", "webshop", "webarena", "tool-query", "tool-operation", "babyai", "scienceworld"]


def parse_args():
    parser = argparse.ArgumentParser(description="Testing")

    parser.add_argument("--cfg-path", required=True, help="path to configuration file.")
    parser.add_argument("--tasks", required=True, type=str, nargs='+',help="specify the tasks")
    parser.add_argument("--model", required=True ,help="specify the models, available models are stated in the configuration file")
    parser.add_argument("--wandb", action="store_true", help="specify whether the wandb board is needed")
    parser.add_argument("--log_path", required=False, default='', help="specify the place to store the resuls")
    parser.add_argument("--project_name", required=False, default='', help="specify the project name for wandb")
    parser.add_argument("--baseline_dir", required=False, default='', help="specify the baseline loggings for wandb baseline comparison visualization")
    parser.add_argument("--max_num_steps", required=False, default=30, help="specify the maximum number of steps used to finish the problems")
    args = parser.parse_args()

    return args

def path_constructor(loader, node):
    path_matcher = re.compile(r'\$\{([^}^{]+)\}')
    ''' Extract the matched value, expand env variable, and replace the match '''
    value = node.value
    match = path_matcher.match(value)
    env_var = match.group()[2:-1]
    return os.environ.get(env_var) + value[match.end():]

def load_config(cfg_path, args):
    path_matcher = re.compile(r'\$\{([^}^{]+)\}')
    yaml.add_implicit_resolver('!path', path_matcher)
    yaml.add_constructor('!path', path_constructor)
    with open(cfg_path, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    llm_config = config["llm"]
    agent_config = config["agent"]
    env_config = config["env"]
    run_config = config["run"]
    
    if args.log_path != '':
        run_config["log_path"] = args.log_path
    if args.project_name != '':
        run_config["project_name"] = args.project_name
    if args.baseline_dir != '':
        run_config["baseline_dir"] = args.baseline_dir
        
    run_config["wandb"] = args.wandb
    run_config["max_num_steps"] = args.max_num_steps
    
    return llm_config, agent_config, env_config, run_config
  
def check_log_paths_are_ready(log_dir, baseline_dir):

    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
        
    if not os.path.exists(os.path.join(log_dir, "logs")):
        os.makedirs(os.path.join(log_dir, "logs"))
    
    if not os.path.exists(baseline_dir):
        os.makedirs(baseline_dir)
    
    if not os.path.exists(os.path.join(log_dir, 'all_results.txt')):
        with open(os.path.join(log_dir, 'all_results.txt'), "w") as f:
            f.write("")
            f.close()
            
    return True

def main():
    load_dotenv()  # take environment variables from .env., load openai api key, tool key, wandb key, project path...

    args = parse_args()
    llm_config, agent_config, env_config, run_config = load_config(args.cfg_path, args) 
    llm_config = llm_config[args.model]
    
    #---------------------------------------------- load llm -----------------------------------------------------
    logger.info("Start loading language model")
    
    llm = load_llm(llm_config["name"], llm_config)
    
    logger.info("Finished loading language model")
    
    
    
    #------------------------------------------------ initialize agentboard ------------------------------------
    if not run_config.get("wandb", False):
        os.environ["WANDB_MODE"] = "disabled"
        logger.info("Wandb is not enabled")
        
        wandb.init(mode="disabled")
    else:
        wandb.init(
            project=run_config["project_name"],
            name="{model_name}_{engine_name}".format(model_name=llm_config["name"], engine_name=llm_config["engine"]),
            notes="An evaluation of LLM agent",
            config= {'llm_config': llm_config,
                        'agent_config': agent_config,
                        'env_config': env_config,
                        'run_config': run_config},
            
        )

    log_dir = run_config.get("log_path", None)
    

    baseline_path = run_config.get('baseline_dir', 'data/baseline_results_details')
    
    assert check_log_paths_are_ready(log_dir, baseline_path)
    
    # agentboard is the main launcher of visualizations and metrics calculation, 
    agentboard = SummaryLogger(baseline_dir=baseline_path, log_path=log_dir) 
    
    log_history = dict()
    for line in open(os.path.join(log_dir, 'all_results.txt'), "r"):
        logger.info(line)
        if "_summary" not in line: 
            log_history[json.loads(line.strip())["task_name"]] = json.loads(line.strip())

    task_names = args.tasks if args.tasks != ["all"] else TASKS

    logger.info("Tested tasks: " + " ".join(log_history))
    
    #------------------------------------------------- start evaluation -------------------------------------------
    for task_name in task_names:
        
        # If the results of the task is already available at {log_path}/all_results.txt, skip the evaluation of this task to avoid rerunning. 
        # If you wish to rerun a task, make sure to remove the line recording previous task results from {log_path}/all_results.txt
        
        if task_name in log_history:
            logger.info(f"Task {task_name} has been evaluated, skip")
            
            
            agentboard.log_run_result(task_name, log_history[task_name]["success_rate"], log_history[task_name]["progress_rate"], log_history[task_name]["grounding_acc"],
                                      log_history[task_name]["success_rate_hard"], log_history[task_name]["success_rate_hard"], log_history[task_name]["progress_rate_hard"],
                                      log_history[task_name]["progress_rate_easy"])

            continue
        
        logger.info(f"Start evaluating task {task_name}")

        agent_task_config = agent_config.copy()
        for key in env_config[task_name]:
            if key in ["check_actions", "check_inventory", "init_prompt_path"]:
                agent_task_config[key] = env_config[task_name][key]
        
        if 'tool' in task_name:
            task = load_task('tool', run_config, llm_config, agent_task_config, env_config[task_name], llm=llm)
        else:
            task = load_task(task_name, run_config, llm_config, agent_task_config, env_config[task_name], llm=llm)

        
        success_rates, progress_rates, grounding_accs, score_state_records,\
            easy_sr, hard_sr, easy_pr, hard_pr = task.evaluate()
        
        success_rate = sum(success_rates) * 1.0 / len(success_rates)
        progress_rate = sum(progress_rates) * 1.0 / len(progress_rates)
        grounding_acc = sum(grounding_accs) * 1.0 / len(grounding_accs)

        
        logger.finish(f"Task {task_name} | Success Rate: {success_rate} , Progress Rate: {progress_rate} , Easy SR: {easy_sr}."
                      f"Hard SR: {hard_sr}, Easy PR: {easy_pr}, Hard PR: {hard_pr}, Grounding Accuracy: {grounding_acc}")
        

        agentboard.log_run_result(task_name, success_rate, progress_rate, grounding_acc, hard_sr, easy_sr, hard_pr, easy_pr)
        
            
    logger.info("Finish evaluating all tasks")
    
    
    agentboard.log_summary()
        

if __name__ == "__main__":
    main()