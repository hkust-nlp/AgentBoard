from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
import os
import time
from common.registry import registry
import pdb
import tiktoken


@registry.register_llm("claude")
class CLAUDE:
    def __init__(self,
                 engine="claude-2",
                 temperature=0,
                 max_tokens=200,
                 top_p=1,
                 stop=["\n\nHuman:"],
                 retry_delays=60,  # in seconds
                 max_retry_iters=5,
                 system_message='',
                 context_length=100000,
                 split=None
                 ):
        # self.url = "https://api.anthropic.com/v1/complete"
        # self.base_url = "http://172.17.0.1:18829"  # for request
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.stop = stop
        self.retry_delays = retry_delays
        self.max_retry_iters = max_retry_iters
        self.system_message = system_message
        self.context_length = context_length
        self.xml_split = split
        self.anthropic = None
        self.init_api_key()
        self.default_tokens_fixed = self.anthropic.count_tokens(
            "\n\nHuman: \n\nAssistant:Do you only want to output the next Action? \n\nHuman: Yes, please do. \n\nAssistant:")
    def init_api_key(self):
        self.anthropic = Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY")
        )

    def llm_inference(self, messages):
        # pdb.set_trace()
        response = self.anthropic.completions.create(
            model=self.engine,
            max_tokens_to_sample=self.max_tokens,
            prompt=messages,
            stop_sequences=self.stop,
            temperature=self.temperature
        )
        return response.completion

    def generate(self, system_message, prompt):
        # print(f"{self.num_tokens_from_messages(prompt, self.engine)} prompt tokens counted by num_tokens_from_messages().")

        # self.llm_inference(prompt)
        extra_prompt = " \n\nAssistant:Do you only want to output the next Action? \n\nHuman: Yes, please do. "
        prompt = HUMAN_PROMPT + system_message + prompt + extra_prompt + AI_PROMPT
        for attempt in range(self.max_retry_iters):
            try:
                return True, self.llm_inference(prompt)  # return success, completion
            except Exception as e:
                print(f"Error on attempt {attempt + 1}")
                if attempt < self.max_retry_iters - 1:  # If not the last attempt
                    time.sleep(self.retry_delays)  # Wait before retrying

                else:
                    print("Failed to get completion after multiple attempts.")
                    raise e

        return False, None

    def num_tokens_from_messages(self, messages, model="claude-2"):
        """Return the number of tokens used by a list of messages."""
        default_tokens_fixed = self.default_tokens_fixed
        if "claude-2" in model:
            default_tokens_fixed = default_tokens_fixed  # tokens of HUMAN_PROMPT and AI_PROMPT
        elif "claude-instant-1" in model:
            default_tokens_fixed = default_tokens_fixed
        else:
            raise NotImplementedError(
                f"""Not implemented for model {model}."""
            )
        num_tokens = 0
        for message in messages:
            num_tokens += self.anthropic.count_tokens(message["content"])
        num_tokens += default_tokens_fixed
        return num_tokens

    @classmethod
    def from_config(cls, config):

        engine = config.get("engine", "claude-2")
        temperature = config.get("temperature", 0)
        max_tokens = config.get("max_tokens", 100)
        system_message = config.get("system_message", "You are a helpful assistant.")
        top_p = config.get("top_p", 1)
        stop = config.get("stop", ["\n\nHuman:"])
        retry_delays = config.get("retry_delays", 10)
        max_retry_iters = config.get("max_retry_iters", 15)
        context_length = config.get("context_length", 100000)
        xml_split = config.get("xml_split", {"example": ["<example>", "</example>"]})
        return cls(engine=engine,
                   temperature=temperature,
                   max_tokens=max_tokens,
                   top_p=top_p,
                   stop=stop,
                   retry_delays=retry_delays,
                   max_retry_iters=max_retry_iters,
                   system_message=system_message,
                   context_length=context_length,
                   split=xml_split)
