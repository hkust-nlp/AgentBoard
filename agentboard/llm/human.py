from common.registry import registry

@registry.register_llm("human")
class HUMAN:
    def __init__(self):
        self.engine = "human"
        self.context_length = 100000000
        self.max_tokens = 10000

    def generate(self, system_message, prompt):
        return True, input("")

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        return 0

    @classmethod
    def from_config(cls, config):
        return cls()
