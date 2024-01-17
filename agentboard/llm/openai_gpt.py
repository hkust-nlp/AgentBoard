import openai
import os
import time
from common.registry import registry
import pdb
import tiktoken

@registry.register_llm("gpt")
class OPENAI_GPT:
    def __init__(self,
                 engine="gpt-3.5-turbo-0631",
                 temperature=0,
                 max_tokens=200,
                 use_azure=True,
                 top_p=1,
                 stop=["\n"],
                 retry_delays=60, # in seconds
                 max_retry_iters=5,
                 context_length=4096,
                 system_message=''
                 ):
        
        
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.use_azure = use_azure
        self.top_p = top_p
        self.stop = stop
        self.retry_delays = retry_delays
        self.max_retry_iters = max_retry_iters
        self.context_length = context_length
        self.system_message = system_message
        self.init_api_key()


        
    def init_api_key(self):
        if self.use_azure:
            openai.api_type = os.environ['OPENAI_API_TYPE']
            openai.api_version = os.environ['OPENAI_API_VERSION']
        else:
            if 'OPENAI_API_KEY' not in os.environ:
                raise Exception("OPENAI_API_KEY environment variable not set.")
            else:
                openai.api_key = os.environ['OPENAI_API_KEY']
            openai.api_base = os.environ['OPENAI_API_BASE'] if 'OPENAI_API_BASE' in os.environ else openai.api_base

    def llm_inference(self, messages):

        response = openai.ChatCompletion.create(
            model=self.engine, # engine = "deployment_name".
            messages=messages,
            stop = self.stop,
            temperature = self.temperature,
            max_tokens = self.max_tokens,
        )
        return response['choices'][0]['message']['content']

    def generate(self, system_message, prompt):
        # print(f"{self.num_tokens_from_messages(prompt, self.engine)} prompt tokens counted by num_tokens_from_messages().")

        # self.llm_inference(prompt)
        prompt=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt}
        ]
        for attempt in range(self.max_retry_iters):
            try:
                return True, self.llm_inference(prompt) # return success, completion
            except Exception as e:
                print(f"Error on attempt {attempt + 1}")
                if attempt < self.max_retry_iters - 1:  # If not the last attempt
                    time.sleep(self.retry_delays)  # Wait before retrying

                else:
                    print("Failed to get completion after multiple attempts.")
                    # raise e

        return False, None

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        model = self.engine
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            print("Warning: model not found. Using cl100k_base encoding.")
            encoding = tiktoken.get_encoding("cl100k_base")
        
        tokens_per_message = 0
        tokens_per_name = 0
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613",
            }:
            tokens_per_message = 3
            tokens_per_name = 1
        
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    @classmethod
    def from_config(cls, config):
        
        engine = config.get("engine", "gpt-35-turbo")
        temperature = config.get("temperature", 0)
        max_tokens = config.get("max_tokens", 100)
        system_message = config.get("system_message", "You are a helpful assistant.")
        use_azure = config.get("use_azure", True)
        top_p = config.get("top_p", 1)
        stop = config.get("stop", ["\n"])
        retry_delays = config.get("retry_delays", 10)
        context_length = config.get("context_length", 4096)
        return cls(engine=engine,
                   temperature=temperature,
                   max_tokens=max_tokens,
                   use_azure=use_azure,
                   top_p=top_p,
                   retry_delays=retry_delays,
                   system_message=system_message,
                   context_length=context_length,
                   stop=stop)
