from agents.base_agent import BaseAgent
from common.registry import registry


@registry.register_agent("YourAgentName")
class CustomAgent(BaseAgent):
    def __init__(self,
                 llm_model,
                 memory_size=100,
                 ):
        super().__init__()

        '''
        To use the agent, follow these steps:

        1. Initialize the agent by calling the `reset` method, providing the initial goal and initial observation as parameters.
            Example: `agent.reset(goal, init_obs)`

        2. Run the agent in an episode by iterating over the desired number of steps.
            Example:
            ```
            for step in episode:
                action = agent.run()
                state, _ = env.step(action)
                agent.update(action, state)
            ```

        The `run` method generates the next action based on the agent's internal state and the current goal. You can customize the agent's behavior by designing your own memory and action generation strategy.

        Note: Make sure to update the agent's internal state using the `update` method after each step to maintain consistency between the agent and the environment.
        '''
        
        self.llm_model = llm_model
        self.memory_size = memory_size
        

    def reset(self, goal, init_obs):
        '''
        reset() is called at the beginning of each episode.
        
        You can use this function to reset your agent's internal state.
        Args:
            goal: The goal string.
            init_obs: The initial observation string.
        
        '''
        self.goal = goal
        self.init_obs = init_obs
        self.memory = []
        

    def run(self):
        '''
        
        run() is called at each time step to generate an action based on the agent current state.
    
        
        '''
        action = "your action"
        return action 
    
    def update(self, action, state):
        
        '''
        update() is called at each time step to update the agent internal state based on the current action and state.
        Memory is could be updated here to keep track of the past actions and states.
        
        Args:
            action: The action string.
            state: The state string.
        
        '''
        self.memory.append(("Action", action))
        self.memory.append(("Observation", state))