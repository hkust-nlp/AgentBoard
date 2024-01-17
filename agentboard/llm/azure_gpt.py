import openai
import os
import tiktoken
import time
import timeout_decorator
import numpy as np
from common.registry import registry

from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


@registry.register_llm("gpt_azure")
class OPENAI_GPT_AZURE:
    def __init__(self,
                 engine="gpt-35-turbo",
                 temperature=0,
                 max_tokens=100,
                 system_message="You are a helpful assistant.",
                 use_azure=True,
                 top_p=1,
                 stop='\n',
                 retry_delays=5, # in seconds
                 max_retry_iters=5,
                 context_length=4096,
                 ):
        
        
        self.engine = engine
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.system_message = system_message
        self.use_azure = use_azure
        self.top_p = top_p
        self.stop = stop
        self.retry_delays = retry_delays
        self.max_retry_iters = max_retry_iters
        self.context_length = context_length
        self.init_api_key()
        
        
    def init_api_key(self):
        if self.use_azure:
            openai.api_type = os.environ['OPENAI_API_TYPE']
            openai.api_base = os.environ['OPENAI_API_BASE']
            openai.api_version = os.environ['OPENAI_API_VERSION']
            openai.api_key = os.environ['OPENAI_API_KEY']
        else:
            openai.api_key = os.environ['OPENAI_API_KEY']

    @timeout_decorator.timeout(10)
    def chat_inference(self, messages):
        assert self.engine in ["gpt-35-turbo", "gpt-4", "gpt-35-turbo-16k"], "engine not supported in ChatCompletion"

        response = openai.ChatCompletion.create(
            engine=self.engine, # engine = "deployment_name".
            messages=messages,
            stop = self.stop,
            temperature = self.temperature,
            max_tokens = self.max_tokens,
        )

        return response['choices'][0]['message']['content']
        
    

    @timeout_decorator.timeout(10)
    def completion_inference(self, prompt, num_return_sequences=1, use_beam_search=False, logprobs=5):
        assert self.engine in ["text-davinci-003"], "engine not supported in Completion"
        
        if use_beam_search:
            response = openai.Completion.create(
                engine = self.engine,
                prompt = prompt,
                logprobs = logprobs,
                n = num_return_sequences,
                temperature = self.temperature,
                stop = self.stop,
                max_tokens = self.max_tokens,
            )
            
            text=[choice["text"] for choice in response["choices"]],
            log_prob=[choice["logprobs"] for choice in response["choices"]]
            
            return text, log_prob
        else:
            response = openai.Completion.create(
                engine = self.engine,
                prompt = prompt,
                stop = self.stop,
                temperature = self.temperature,
                max_tokens = self.max_tokens
            )
            
            return response['choices'][0]['text']

    def generate(self, system_message, prompt):
        
        if 'gpt' in self.engine:
        
            prompt=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            for attempt in range(self.max_retry_iters):  
                try:
                    output = self.chat_inference(prompt)
                    output = output.split("\n")[0]
                    return True, output # return success, completion
                except Exception as e:
                    print(f"Error on attempt {attempt + 1}") 
                    if attempt < self.max_retry_iters - 1:  # If not the last attempt
                        time.sleep(self.retry_delays)  # Wait before retrying
                    
                    else:
                        print("Failed to get completion after multiple attempts.")
                        # raise e
                        
            return False, None
        
        elif 'text' in self.engine:
            
            prompt = system_message + '\n' + prompt
            
            for attempt in range(self.max_retry_iters):  
                try:
                    output = self.completion_inference(prompt)
                    output = output.split("\n")[0]
                    return True, output # return success, completion
                except Exception as e:
                    print(e)
                    print(f"Error on attempt {attempt + 1}") 
                    if attempt < self.max_retry_iters - 1:  # If not the last attempt
                        time.sleep(self.retry_delays)  # Wait before retrying
                    
                    else:
                        print("Failed to get completion after multiple attempts.")
                        raise e
                        
            return False, None
    

    def num_tokens_from_messages(self, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        model = self.engine
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # print("Warning: model not found. Using cl100k_base encoding.")
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
            "gpt-4",
            "gpt-35-turbo",
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
        context_length = config.get("context_length", 4096)
        return cls(engine=engine,
                   temperature=temperature,
                   max_tokens=max_tokens,
                   system_message=system_message,
                   use_azure=use_azure,
                   context_length=context_length,
                   top_p=top_p,
                   stop=stop)