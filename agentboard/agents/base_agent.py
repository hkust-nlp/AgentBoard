class BaseAgent: # the agent should receive goal, state and action, then return the next state
    def __init__(self):
        super().__init__()
    
    def reset(self, goal, init_obs, init_act=None):
        pass
    
    def update(self, action, state):
        pass
    
    def run(self):
        pass
    
    @classmethod
    def from_config(cls, llm_model, config):
        pass