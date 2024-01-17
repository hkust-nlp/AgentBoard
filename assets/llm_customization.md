# LLM Customization

We provide a user-friendly way to evaluate your own model.

<p align="right"> <a href="../README.md">🔙Back to README.md</a> </p>


## Evaluate Your Model

### Step 1: Add your model configs

You should add your model config to `eval_configs/main_results_all_tasks.yaml`, for example:
```yaml
  codellama-34b
      name: vllm 
      engine:  [PATH TO YOUR MODEL]
      max_tokens: 100
      temperature: 0
      top_p: 1
      stop:
      context_length: 16384
      dtype: float32
      ngpu: 4
      use_parser: True
```
Arguments for the configs are as follows,
* `name`: name of the inference framework (e.g., `vllm`,`hg`, `gpt`,`gpt_azure`, `claude`)
* `engine`: path to your model or the huggingface model name
* `max_tokens`: the max number of newly generated tokens
* `temperature`: temperature for generation
* `top_p`: top-$p$ for generation
*  `stop`: stop tokens for generation
* `context_length`: the maximum context length of the LLM
* `dtype`: float32 or float16
* `ngpu`: this argument works for the vllm framework
* `usr_parser`: bool, post-process the generated actions




### Step 2: Inference your model with vLLM or huggingface

Please check whether your model is supported by [vLLM](https://xianbai.me/learn-md/article/syntax/links.html). 
We recommend to use vLLM because it is usually much faster than naive `model.generate()` in huggingface.


If you decide to use the vLLM, you should set the argument of `name` above as **vllm**, otherwise **hg**.

Note： The results of inferencing with huggingface and vLLM can be different because their different implementations.
### Step 3: Write the prompt_templates of your model
If your model need customized input template, you should write it in `agentboard/prompts/prompt_template`, for example:
```python
"codellama-34b":
"""
<s>[INST]{system_prompt}{prompt}[/INST]
""",
```
Arguments for this template are as follows,

* `system_prompt`: system prompt of your agent
* `prompt`: the user prompt of your agent
