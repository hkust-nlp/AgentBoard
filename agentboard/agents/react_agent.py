from agents.base_agent import BaseAgent
from common.registry import registry

import json


@registry.register_agent("ReactAgent")
class ReactAgent(
    BaseAgent):  # the agent should receive goal, state and action, then return the next state
    def __init__(self,
                 llm_model,
                 memory_size=100,
                 # set this to a very large number if you want to keep all history till context length limit
                 examples=[],
                 instruction="",
                 init_prompt_path=None,
                 system_message="You are a helpful assistant.",
                 need_goal=False,
                 check_actions=None,
                 check_inventory=None,
                 use_parser=True,
                 max_think_iters=3
                 ):
        super().__init__()
        self.use_parser = use_parser
        self.llm_model = llm_model
        self.memory_size = memory_size
        self.goal = None
        self.init_obs = None
        if init_prompt_path is not None:  # load from file
            self.init_prompt_dict = json.load(open(init_prompt_path, 'r'))
            self.instruction = self.init_prompt_dict["instruction"]
            self.examples = self.init_prompt_dict["examples"]
        else:

            self.instruction = instruction
            self.examples = examples

            # self.reset(goal, init_obs)
            self.init_prompt_dict = {
                "examples": examples,
                "instruction": instruction,
                "system_msg": system_message
            }

        self.max_context_length = self.llm_model.context_length
        self.need_goal = need_goal
        self.check_actions = check_actions
        self.check_inventory = check_inventory
        self.think_count = 0
        self.max_think_iters = max_think_iters
        self.force_action = False   # Sometimes the agent does not generate action or think, we need to force it to take action.

        if "claude" in self.llm_model.engine:
            self.split = self.llm_model.xml_split
        else:
            self.split = {"example": [""],
                          "text": [""],
                          "rule": [""],
                          "system_msg": [""],
                          "instruction": [""],
                          "goal": [""]}

    def reset(self, goal, init_obs, init_act=None):
        self.goal = goal
        self.init_obs = init_obs
        self.memory = [("Action", init_act), ('Observation', self.init_obs)] if init_act \
            else [
            ('Observation', self.init_obs)]  # list of [('State', "xxx"), ('Action', "xxx"), ...]
        self.steps = 0
        self.done = False
        self.think_count = 0

    def extract_think(self, response):
        if response.startswith("Think"):
            return response.split("Think: ")[-1].split("\n")[0]
    
    def extract_action(self, response):
        if response.startswith("Action"):
            return response.split("Action: ")[-1].split("\n")[0]

    def update(self, action='', state=''):
        self.steps += 1
        self.memory.append(("Action", action))
        self.memory.append(("Observation", state))

    def make_prompt(self,
                    need_goal=False,
                    check_actions="check valid actions",
                    check_inventory="inventory",
                    system_message=""):
        query = ""
        query += self.split["instruction"][0] + self.instruction + self.split["instruction"][-1]

        if isinstance(self.examples, str):
            self.examples = [self.examples]

        if len(self.examples) > 0:
            query += "\nHere are examples:\n" + self.split["example"][0]
            for example in self.examples:
                query += example + "\n"
            query += self.split["example"][-1]

        if need_goal:
            query += self.split["goal"][0] + "You should perform actions to accomplish the goal: " + self.goal + "\n" + \
                     self.split["goal"][-1]
        if check_actions is not None:
            query += "You should use the following commands for help when your action cannot be understood: " + check_actions + "\n"
        if check_inventory is not None:
            query += "You should use the following commands for help when your action cannot be understood: inventory\n"

        history = self.memory[-self.memory_size:]
        input_prompt = query + "\n".join([item[0] + ": " + item[1] for item in history])

        if self.think_count >= self.max_think_iters:
            input_prompt +="\nPlease stop thinking and start taking action on the task."
        elif self.force_action:
            input_prompt += "\nPlease take action on the task."
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": input_prompt}     
        ]

        num_of_tokens = self.llm_model.num_tokens_from_messages(messages)
        while num_of_tokens > self.max_context_length - self.llm_model.max_tokens:
            history = history[1:]
            input_prompt = query + "\n".join([item[0] + ": " + item[1] for item in history])

            if self.think_count >= self.max_think_iters:
                input_prompt +="\nPlease stop thinking and start taking action on the task."
            elif self.force_action:
                input_prompt += "\nPlease take action on the task."

            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": input_prompt}
            ]
            num_of_tokens = self.llm_model.num_tokens_from_messages(messages)

        return input_prompt

    def action_parser_for_special_llms(self, action):
        
        '''
        This function is used to parse the action for special llms, e.g. codellama-13b, codellama-34b, llama, lemur, vicuna, etc.
        These llms often struggle to generate the format of the action correctly, so we need to parse the action to make it executable.
        '''
        
        origin_action = action
        if 'action' in action.lower():
            action_temp = action.split('\n')
            for act in action_temp:
                if "next action" in act and ':' in act: # zzh: in Claude will return "Here is the next action to take:"
                    idx = action_temp.index(act)
                    while idx + 1 < len(action_temp):
                        if action_temp[idx + 1]:
                            action = action_temp[idx + 1]
                            break
                        idx += 1
                if act.split(':')[0].lower().endswith('with action input'): # chang: in case parse tool output
                    action = act
                    break
                if 'action' in act.lower() and ':' in act:
                    action_temp = ':'.join(act.split(':')[1:])
                    if action_temp != "":
                        action = action_temp
                        break
                if 'action' in act.lower() and 'is to' in act:
                    action_temp = act.split('is to')[1]
                    if action_temp != "":
                        action = action_temp
                        break
                        
        if action.strip() == "":
            action = origin_action.split('\n')[0]   # temperary comment this line for codellama
        action = action.strip()
        action = action.strip("'/")
        action = action.split('\n')[0]
        return action

    def run(self, init_prompt_dict=None):
        # note that these configs are originally provided when initialized, but you can choose to override them here with parameters
        if init_prompt_dict is not None:
            self.init_prompt_dict = init_prompt_dict
            self.instruction = init_prompt_dict['instruction']
            self.examples = init_prompt_dict['examples']
        system_message = self.init_prompt_dict['system_msg']

        flag = False    # flag to indicate whether the agent has generated an **action**

        while not flag:
            input_prompt = self.make_prompt(need_goal=self.need_goal,
                                            check_actions=self.check_actions,
                                            check_inventory=self.check_inventory,
                                            system_message=system_message)

            success, response = self.llm_model.generate(system_message, input_prompt)
            # print(input_prompt)

            if response.startswith("Action"):
                flag = True
                self.think_count = 0
                self.force_action = False
                response = self.extract_action(response)
                if self.use_parser:
                    response = self.action_parser_for_special_llms(response)

            elif response.startswith("Think"):
                flag = False
                self.think_count += 1
                self.force_action = False
                response = self.extract_think(response)
                print("Step {:02} - Think: {}".format(self.steps, response))
                self.memory.append(
                    ("Think", response)
                )
            
            else:
                flag = False
                self.think_count = 0
                self.force_action = True

        return success, response

    @classmethod
    def from_config(cls, llm_model, config):
        memory_size = config.get("memory_size", 100)
        instruction = config.get("instruction", "")
        examples = config.get("examples", [])
        init_prompt_path = config.get("init_prompt_path", None)
        system_message = config.get("system_message", "You are a helpful assistant.")
        check_actions = config.get("check_actions", None)
        check_inventory = config.get("check_inventory", None)
        use_parser = config.get("use_parser", True)
        need_goal = config.get("need_goal", False)
        max_think_iters = config.get("max_think_iters", 3)

        return cls(llm_model, memory_size, examples, instruction, init_prompt_path, system_message, 
                   need_goal, check_actions, check_inventory, use_parser, max_think_iters=max_think_iters) 
