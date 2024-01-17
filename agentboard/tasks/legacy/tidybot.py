from dataclasses import dataclass
from typing import List
from llm import load_llm
import yaml
from agents import load_agent
from prompts.temp.tidybot_gpt import construct_placement_prompt, construct_summarization_prompt_template
from common.registry import registry

@dataclass
class Scenario:
    room: str
    receptacles: List[str]
    seen_objects: List[str]
    seen_placements: List[List[str]]
    unseen_objects: List[str]
    unseen_placements: List[List[str]]
    annotator_notes: str
    tags: List[str]

def load_scenarios(path='scenarios.yml'):
    with open(path, 'r', encoding='utf8') as f:
        scenarios = list(map(lambda x: Scenario(**x), yaml.safe_load(f)))
    return scenarios

def parse_summary(summarization_completion):
    lines = [l for l in map(str.strip, summarization_completion.split('\n')) if len(l) > 0]
    if len(lines) > 1:
        print('Warning: Using first line of multi-line summary')
    return lines[0]

def parse_placements(placement_completion, objects):
    placements = []
    first_line = True
    for line in placement_completion.strip().split('\n'):
        if first_line:
            obj = objects[0]
            recep = line
            first_line = False
        else:
            if len(line) == 0:
                print('Warning: Stopping since newline was encountered')
                break
            placement_args = line.split(',')
            if len(placement_args) != 2:
                print('Warning: Skipping invalid placement')
                continue
            obj, recep = placement_args
            if '(' in obj:
                obj = obj.split('(')[1].strip().replace('"', '')
            else:
                print('Warning: Found possibly invalid placement')
                obj = obj.strip().replace('"', '')
        recep = recep.strip().replace(')', '').replace('"', '')
        placements.append([obj, recep])
    return placements

def check_placements(predicted_placements, correct_placements):
    correct_placements_dict = {}
    for obj, recep in correct_placements:
        correct_placements_dict[obj] = recep

    corrects = []
    for obj, recep in predicted_placements:  # Note that for repeats, this will only score the first instance
        corrects.append(obj in correct_placements_dict and recep == correct_placements_dict.pop(obj))

    accuracy = sum(corrects) / len(correct_placements)

    return corrects, accuracy

@registry.register_task("tidybot")
class EvalTidyBot:
    def __init__(self,
                 data_path = './data/tidybot/scenarios.yml',
                 llm_name = "gpt",
                 llm_config = None,
                 agent_name = "GPTAgent",
                 agent_config = None,
                 ):
        self.data_path = data_path
        llm = load_llm(llm_name, llm_config)
        self.agent = load_agent(agent_name, agent_config, llm)

    def evaluate_env(self, scenarios, eval_split='unseen', verbose=False):
        assert eval_split in {'unseen', 'seen'}
        accuracies = []
        for i, scenario in enumerate(scenarios):
            print(f'Scenario {i + 1} of {len(scenarios)}\n')
            # Summarization
            summarization_prompt = construct_summarization_prompt_template(
                scenario.seen_objects, scenario.receptacles, scenario.seen_placements)
            is_succ, summarization_completion = self.agent.run(summarization_prompt)


            if verbose:
                print(summarization_prompt, end='')
                utils.print_colored(summarization_completion, 'blue')
                print('\n' + 10 * '-' + '\n')

            # Object placement
            summary = parse_summary(summarization_completion)
            objects = scenario.seen_objects if eval_split == 'seen' else scenario.unseen_objects
            placement_prompt = construct_placement_prompt(summary, objects, scenario.receptacles)
            # print(placement_prompt)
            is_succ, placement_completion = self.agent.run(placement_prompt)

            if verbose:
                print(placement_prompt, end='')
                utils.print_colored(placement_completion, 'blue')
                print('\n' + 10 * '-' + '\n')

            # Analysis
            predicted_placements = parse_placements(placement_completion, objects)
            correct_placements = scenario.seen_placements if eval_split == 'seen' else scenario.unseen_placements
            corrects, accuracy = check_placements(predicted_placements, correct_placements)
            accuracies.append(accuracy)
            if verbose:
                print(f'Annotator notes: {scenario.annotator_notes}\n')
                print('Correct placements:')
                for placement in correct_placements:
                    print(placement)
                print('\nParsed placements:')
                for placement, correct in zip(predicted_placements, corrects):
                    utils.print_colored(placement, 'green' if correct else 'red')
                print(f'\nAccuracy: {accuracy:.2f}')
                print('\n' + 80 * '-' + '\n')
        return accuracies

    def evaluate(self):
        scenarios = load_scenarios(path=self.data_path)
        print(f"Number of test examples: {len(scenarios)}")

        print("start test the unseen objects")
        accuracies_unseen = self.evaluate_env(scenarios, eval_split='unseen')
        print(f"acc: {np.mean(accuracies_unseen).round(3)}")
        print("start test the seen objects")
        accuracies_seen = self.evaluate_env(scenarios, eval_split='seen')
        print(f"acc: {np.mean(accuracies_seen).round(3)}")
        return None

    @classmethod
    def from_config(cls,
                    run_config,
                    llm_config,
                    agent_config,
                    env_config,
                    ):
        data_path = env_config.get('data_path', './data/tidybot/scenarios.yml')
        llm_name = llm_config.get("llm_name", "gpt")
        agent_name = agent_config.get('agent_name', "GPTAgent")

        return cls(data_path=data_path,
                   llm_name=llm_name,
                   llm_config=llm_config,
                   agent_name=agent_name,
                   agent_config=agent_config,
                   )

