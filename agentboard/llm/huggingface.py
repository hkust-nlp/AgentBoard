from transformers import AutoTokenizer, AutoModel, pipeline, StoppingCriteria, AutoModelForCausalLM
from common.registry import registry
import transformers
import torch
import os
import deepspeed
import pdb
import numpy as np
from prompts.prompt_template import prompt_templates

class EosListStoppingCriteria(StoppingCriteria):
    def __init__(self, eos_sequence):
        self.eos_sequence = eos_sequence

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        last_ids = input_ids[:,-len(self.eos_sequence):].tolist()
        return self.eos_sequence in last_ids

@registry.register_llm("hg")
class HgModels:
    def __init__(self,
                 model='',
                 temperature=0,
                 max_tokens=100,
                 top_p=1.0,
                 context_length=4096,
                 stop='\n',
                 d_type='bfloat16'
                 ):
        
        access_token = os.environ["HF_KEY"]
        
        self.tokenizer = AutoTokenizer.from_pretrained(model, token=access_token)
        torch_dtype = torch.float16 if d_type == 'float16' else torch.float32
        self.engine = model
        self.model = model
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.temperature = temperature
        self.batch_size = 1
        self.context_length = context_length
        self.pad_token_id = self.tokenizer.eos_token_id
        self.eos_token_id = self.tokenizer.eos_token_id
        self.stop = stop
        self.llm = AutoModelForCausalLM.from_pretrained(model,
                                                        device_map='auto',
                                                        torch_dtype=torch_dtype)
        #self.StopCriteria = EosListStoppingCriteria(self.tokenizer(stop))

        
    def make_prompt(self, system_message, prompt):
        full_prompt = None
        system_message += "Generate your next step of action after Action. Action must not be empty. e.g. Action: put down cup. \n"
        if "codellama-13b" in self.model.lower():
            full_prompt = prompt_templates["codellama-13b"].format(system_prompt=system_message, prompt=prompt)
            full_prompt = full_prompt.strip()
        elif "codellama-34b" in self.model.lower():
            full_prompt = prompt_templates["codellama-34b"].format(system_prompt=system_message, prompt=prompt)
            full_prompt = full_prompt.strip()
            
        elif "llama" in self.model.lower():
            full_prompt = prompt_templates["llama"].format(system_prompt=system_message, prompt=prompt)
            full_prompt = full_prompt.strip()
            
        elif 'lemur' in self.model.lower():
            full_prompt = prompt_templates["lemur"].format(system_prompt=system_message, prompt=prompt)
            full_prompt = full_prompt.strip()
            
        elif 'vicuna' in self.model.lower():
            full_prompt = prompt_templates["vicuna"].format(system_prompt=system_message, prompt=prompt)
            full_prompt = full_prompt.strip()
        else:
            raise NotImplementedError
        
        return full_prompt

    def generate(self, system_message, prompt):
        full_prompt = self.make_prompt(system_message, prompt)
        assert full_prompt is not None

        with torch.no_grad():
            input = self.tokenizer([full_prompt], return_tensors="pt")
            prompt_length = len(input.input_ids[0])
            input = {k: v.to("cuda") for k, v in input.items()}
            outputs = self.llm.generate(**input,
                                        max_new_tokens=self.max_tokens,
                                        temperature=self.temperature,
                                        top_p=self.top_p,
                                        pad_token_id=self.pad_token_id,
                                        eos_token_id=self.eos_token_id,
                                        output_scores=True,
                                        do_sample=False)
        #output_texts = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        output_texts = self.tokenizer.decode(outputs[0][prompt_length:], skip_special_tokens=True)
        if self.stop is not None:
            output_texts = output_texts.split(self.stop)[0]
        if 'vicuna' in self.model.lower():
             output_texts = output_texts.replace('\_', '_')
        return True, output_texts
    
    def num_tokens_from_messages(self, messages):
        prompt = messages[1]["content"]
        system_message = messages[0]["content"]
        full_prompt = self.make_prompt(system_message, prompt)
        tokens = self.tokenizer(full_prompt)
        num_tokens = len(tokens["input_ids"])
        #print(num_tokens)
        return num_tokens
    @classmethod
    def from_config(cls, config):
        
        engine = config.get("engine", "gpt-35-turbo")
        temperature = config.get("temperature", 0)
        max_tokens = config.get("max_tokens", 100)
        top_p = config.get("top_p", 1)
        stop = config.get("stop", ["\n"])
        context_length = config.get("context_length", 4096)
        #ngpu = config.get("ngpu", 4)
        dtype = config.get("dtype", 'bfloat16')
        
        return cls(model=engine,
                  temperature=temperature,
                  max_tokens=max_tokens,
                  top_p=top_p,
                  context_length=context_length,
                  stop=stop,
                  d_type=dtype
                   )
