# Agent Customization

We provide a user-friendly way to evaluate your own agent.

<p align="right"> <a href="../README.md">🔙Back to README.md</a> </p>


## Evaluate Your Agent
In AgentBoard, you can implement your own LLM-based agent in `agentboard/agents/`.


### Step 1: write codes for your agent

Defaultly, we experiment with the `VanillaAgent` in `agentboard/gents/vanilla_agent.py`, which is based on acting-only prompting.

> Note: Before you customize your own agent, we recommend you to first run the `VanillaAgent` to understand the evaluation process and the behavior of the LLM agent.

If you want to customize your own agent (e.g., ReactAgent), please follow `CustomAgent` in `agentboard/agents/custom_agent.py` and implement the following methods:

```python
def __init__(self):
  pass

def reset(self):
  pass

def update(self):
  pass

def run(self):
  pass

@classmethod
def from_config(cls):
  pass

# other self-defined methods
```

### Step 2: modify the prompt file
In AgentBoard, we adopt a one-shot prompt for generation.

So, when you customize your own agent, you should modify the corresponding prompt file for each task under `prompts/`.

You can refer to the `agentboard/prompts/VanillaAgent/` for the format of the prompt file.


### Step 3: add your agent configs
Please change the `agent` configs in `eval_configs/main_results_all_tasks.yaml` to your own agent and prompt file, for example:

```yaml
agent:
  name: ${YOUR_AGENT_NAME}
  memory_size: 100
  need_goal: True
```


```yaml
scienceworld:
  ...
  init_prompt_path: ${YOUR_PROMPT_PATH}
  ...
```

### Example
We provide an example of the ReactAgent in `agentboard/agents/react_agent.py`.
And the corresponding prompt files of Tool-Query task are in `agentboard/prompts/ReactAgent/`.

