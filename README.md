<div align="center">
<img src="./assets/agentboard.png" style="width: 20%;height: 10%">
<h1> AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents </h1>
</div>

<div align="center">

![Data License](https://img.shields.io/badge/Data%20License-GPL--2.0-blue.svg)
![Code License](https://img.shields.io/badge/Code%20License-Apache--2.0-blue.svg)
![Python 3.8+](https://img.shields.io/badge/python-3.8.13-blue.svg)
[![slack badge](https://img.shields.io/badge/Slack-Join-blueviolet?logo=slack&amp)](https://join.slack.com/t/agentboard/shared_invite/zt-28ks1f1er-DzpwLKa41p_RArKnu2yimA)

</div>

<div align="center">

  <!-- <a href="#model">Model</a> • -->
  🌐 <a href="https://hkust-nlp.github.io/agentboard">Website</a> |
  🏆 <a href="https://hkust-nlp.github.io/agentboard/static/leaderboard.html">Leaderboard</a> |
  📚 <a href="https://huggingface.co/datasets/hkust-nlp/agentboard">Data</a> |
  📃 <a href="https://arxiv.org/pdf/2401.13178.pdf">Paper</a> |
  📊 <a href="https://wandb.ai/agentboard/llm-agent-eval-gpt-35-turbo-all/reports/Using-Wandb-to-Launch-AgentBoard--Vmlldzo2MTg1Njc4">Panel</a>

</div>




## 1. What's New
- **[2024.01.15]** 📣 AgentBoard is released.



## 2. Table of Contents
<details>
<summary>
Click to expand the table of contents
</summary>

- [1. What's New](#1-whats-new)
- [2. Table of Contents](#2-table-of-contents)
- [🚀 Quick Start](#-quick-start)
- [3. Introduction](#3-introduction)
- [4. Leaderboard](#4-leaderboard)
- [5. Online Visualization and Logging](#5-agentboard-online-visualization-and-logging)
- [6. Data](#6-data)
  - [6.1 Data Overview](#61-data-overview)
  - [6.2 Download Link](#62-download-link)
  - [6.3 Data Fields](#63-data-fields)
- [7. Evaluation](#7-evaluation)
  - [7.1 Evaluation Preparation](#71-evaluation-preparation)
  - [7.2 Running Proprietary Models](#72-running-proprietary-models)
  - [7.3 Running Open-source Models](#73-running-open-source-models)
  - [7.4 Code Structure](#74-code-structure)
  - [7.5 LLM Customization](#75-llm-customization)
  - [7.6 Agent Customization](#76-agent-customization)
  - [7.7 Runtime Estimation](#77-runtime-estimation)
- [️8. Citation](#️8-citation)
- [9. License](#9-license)
</details>

## 🚀 Quick Start 

Here we provide a quick start guide to evaluate LLM agents on AgentBoard within 30 minutes. 

### Setup Environment
We provide both local setup (recommended) and docker as follows:
<details>
<summary>
Click to expand local setup procedures (~ 15 minutes).
</summary>

Setup with a setup.sh: 

**Step 1. Create a conda environment**
```shell
conda create -n ${YOUR_ENV_NAME} python=3.8.13  # python version should be 3.8.13
conda activate ${YOUR_ENV_NAME}
```

**Step 2. Git clone this repo**
```shell
git clone https://github.com/hkust-nlp/AgentBoard.git
```

**Step 3. Download the data from huggingface**
```shell
# Download the data and move it to the project root dir
cd AgentBoard
mkdir data
wget https://huggingface.co/datasets/hkust-nlp/agentboard/resolve/main/data.tar.gz
tar -zxvf data.tar.gz
```

**Step 4. Set up the environment for tasks except WebArena**
```shell
INSTALL_WEBARENA=false bash ./setup.sh

# After running the above command, the env will support other tasks than WebArena
```

**Step 5. Set up the environment for WebArena**
```shell
# Please check whether the dubs and Xvfb are installed before building it
# For Ubuntu or Debian
dpkg -l | grep dbus  # will return the info
systemctl status dbus  # will return the status(active (running))
dpkg -l | grep xvfb  # will return the info

#-----------------------------------------------------------------------#

# For CentOS
yum list installed | grep Xvfb  # will return the Xvfb info
systemctl status dbus  # will return the status(active (running))
dnf list installed | grep dbus  # will return the dbus info
```

If so, you may install the webarena environment directly.
```shell
INSTALL_WEBARENA=true bash ./setup.sh
```

If not, please jump to Step 6 or [Installation by Docker](#52-installation-by-docker)

**(Additional) Step 6. Install the dubs and Xvfb**
```shell
# You must use the sudo permission to do the following:

# For Ubuntu or Debian
# Install and start the dbus service
apt-get install dbus
/etc/init.d/dbus start

# Install ans start the Xvfb
sudo apt-get update
sudo apt-get install xvfb

INSTALL_WEBARENA=true bash ./setup.sh
#--------------------------------------------------------#

# For Centos
# Install and start the dbus service
yum install -y dbus-x11
/etc/init.d/dbus start

# Install ans start the Xvfb
yum update
yum install -y Xvfb

INSTALL_WEBARENA=true bash ./setup.sh
```
</details>

<details>
  <summary>
Click to expand docker setup procedures. (~12G, 5 minutes)
</summary>

  Docker info: CentOS

**Step 1. Pull the docker image and run docker locally**
```shell
docker pull zzh202121/agentboard:0117
docker run -itd \
    --gpus all \
    --network host \
    --name agent_space \
    --shm-size 64gb \
    -v /MODEL_PATH:/model_download \
    -v /DATA_PATH:/data \
    zzh202121/agentboard:0117 \
    /bin/bash
docker attach agent_space # YOUR_CONTAINER_NAME
```

**Step 2. activate the env**
```shell
conda activate agentboard
```

**Step 3. Download the code and data**
```shell
git clone https://github.com/hkust-nlp/AgentBoard.git  # clone repo
# Download the data and move it to the project root dir
cd AgentBoard
mkdir data
wget https://huggingface.co/datasets/hkust-nlp/agentboard/resolve/main/data.tar.gz
tar -zxvf data.tar.gz
```

**Step 3. Build search engine index(For WebShop)**
```shell
cd ./agentboard/environment/WebShop/search_engine
mkdir -p resources resources_100 resources_1k resources_100k
python convert_product_file_format.py # convert items.json => required doc format
mkdir -p indexes
./run_indexing.sh
cd ../../../
```

**Step 4. Start web service(For Webarena)**
```shell
/etc/init.d/dbus start  # start dbus
Xvfb :99 -screen 0 1280x720x24 &  # start xvfb display
export DISPLAY=:99
python -m playwright install
```
</details>

### Setup Environment Variables in `AgentBoard/.env`
Environment Variables needed for AgentBoard include:
```
PROJECT_PATH = {path to project}/AgentBoard

ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...

TODO_KEY=...
MOVIE_KEY=...
SHEET_EMAIL=...

WANDB_API_KEY=...
```
<details>
<summary>
Click to expand API key setup procedures.
</summary>
  
**Variables 1: API keys for Tool tasks**

Since API keys for **Tool** tasks are private, we do not provide them in this repo.

Please follow this detailed [guide](./assets/api_keys_tool.md) to get API keys for **Tool** tasks.

**Variables 2: Weights&Bias key for AgentBoard Online Visualization**

Please paste `WANDB_API_KEY` from here [guide](https://wandb.ai/authorize) in `.env` file to login Weights&Bias for AgentBoard Visulization.


**Variables 3: API keys for Proprietary models**

**⚠️ You don't need to setup API keys for models you don't want to use.**

If you use OpenAI models, please put your API keys in `.env` file.
```shell
OPENAI_API_TYPE="open_ai"
OPENAI_API_KEY=${YOUR_OPENAI_API_KEY}
```

If you use Anthropic models, please put your API keys in `.env` file.
```shell
ANTHROPIC_API_KEY=${YOUR_ANTHROPIC_API_KEY}
```
</details>

### Evaluate Models
Example script for `GPT-3.5-Turbo`:
```
python agentboard/eval_main.py \
    --cfg-path eval_configs/main_results_all_tasks.yaml \
    --tasks alfworld \
    --model gpt-3.5-turbo-0613 \
    --wandb \
    --log_path ./results/gpt-3.5-turbo-0613 \
    --project_name evaluate-gpt-35-turbo-0613 \
    --baseline_dir ./data/baseline_results
```
⚠️ We now offer configuration for 12 SOTA LLM models (`gpt-4`,`gpt-3.5-turbo-0613`, `text-davinci-003`,`claude2`,`deepseek-67b`,`lemur-70b`, `mistral-7b`,`codellama-13b(34b)`,`llama2-13b(70b)`,`vicuna-13b-16k`) and a simple reflex agent based on [Act](https://arxiv.org/abs/2210.03629). You could also customize your own [agents](https://github.com/hkust-nlp/AgentBoard/blob/main/assets/agent_customization.md) and [LLMs](https://github.com/hkust-nlp/AgentBoard/blob/main/assets/llm_customization.md). 
### Check and Analyze Results
In addition to online results viewing, local logs are automatically stored in `{log_path}`. In WebArena, we additionally support more detailed trajectory files, including web page screenshots and network traffic records.
<details>
  <summary>
    Log file organization: 
  </summary>
  
```
{log_path}
├── logs                    # detailed example-wise logs for each task
│  ├── webarena_tracks      # WebArena provided rendered HTML files of the execution trace and a './trace' folder which is automatically generated with Playwright
│  │  ├── traces
│  │  │  ├── 102.zip
│  │  ├── render_102.html
│  │  ├── ...
│  ├── alfworld.jsonl       # each line is a json dictionary logging the statistics, trajectory, and prompt for each example
│  ├── babyai.jsonl
│  ├── ...
├── all_results.txt         # overall metrics for each task
├── dimension.txt           # agent capability dimensional scores for current LLM agent
├── alfworld.txt            # a general log for example-wise statisitcs for each task
├── babyai.txt              
└── ...              
```
</details>

An online visualization page would be ready on Weights&Bias. The link would be provided during running `https://wandb.ai/{your_wandb_id}/{project_name}`, showing the same *main results*,*dimensional analysis*,*steps analysis*, *trajectory explorer* for your LLM agent compared to baselines. Please refer to this [blog](https://wandb.ai/agentboard/llm-agent-eval-gpt-35-turbo-all/reports/Using-Wandb-to-Launch-AgentBoard--Vmlldzo2MTg1Njc4) for a detailed tutorial on using and interpretating AgentBoard.

<div align="center">

<img src="./assets/main_graph.png">
<!-- <h1> A nice pic from our website </h1> -->

</div>



## 3. Introduction


AgentBoard explores the potential of Large Language Models (LLMs) as generalist agents capable of perceiving and acting within various environments.
AgentBoard outlines five principles for constructing a benchmark to evaluate LLMs as generalist agents:
 1. **Task Diversity**: AgentBoard incorporates 9 distinct tasks to comprehensively understand the generalist ability of LLM agents , which is built upon LLM's extensive knowledge base and exceptional scenario comprehension.
 2. **Multi-round Intercation**: AgentBoard provides multi-round interaction between agents and environment, which is necessary to reflect the evolutionary nature of human intelligence, which continuously receives information and adapts towards the environment.
 3. **Environments Partially-Observable**: In AgentBoard, the complete state of the environment is not available to the agent, which assesses agent world modeling ability as additional knowledge needs to be acquired through online
exploration.
 4. **Fine-grained Metrics**: AgentBoard provides progress rates as fine-grained metrics, which are necessary to track stage-wise progress and differentiate performance among LLM models, emphasizing their unique ability to break complex goals into manageable subgoals
 5. **Systematic Evaluation**: AgentBoard is a systematic platform: it includes a user-friendly script to construct goal-oriented reflex agents for a range of models, and features a panel for visualizing and interpreting results across multiple dimensions of agent proficiency.

## 4. Leaderboard
We provide a leaderboard for the community to rank open-source models and closed-source models.

Please check our website: [AgentBoard Leaderboard](https://hkust-nlp.github.io/agentboard/static/leaderboard.html) for more details.
## 5. AgentBoard Online Visualization and Logging
AgentBoard integrates illustrative [Weights&Bias](https://wandb.ai/site) visualization to help researchers to better systematically analyze LLM agents.

You can simply turn on `--wandb` switch in the arguments and customize the `project_name` and `baseline_dir` of your wandb project.
```shell
python agentboard/eval_main.py --cfg eval_configs/main_results_all_tasks.yaml \
                    --tasks alfworld \
                    --model  lemur-70b \
                    --log_path results/lemur-70b \
                    --wandb \
                    --project_name evaluate-lemur-70b \
                    --baseline_dir data/baseline_results \
```

Before running, you need to setup wandb login or environment variable as instructed in [quick-start](#setup-environment-variables-in-agentboardenv). The visualization results would be both stored offline at `\wandb` and online at `https://wandb.ai/{your_wandb_id}/{project_name}`. Note that if your run is not logged online, you could sync local runs to wandb online with `wandb sync [OPTIONS] [PATH]..` as detailed in [wandb docs](https://docs.wandb.ai/ref/cli/wandb-sync).

For more information about the features about Weights&Bias visualization, Pleae kindly check this [Blog](https://wandb.ai/agentboard/llm-agent-eval-gpt-35-turbo-all/reports/Using-Wandb-to-Launch-AgentBoard--Vmlldzo2MTg1Njc4) for more information.
We also provide example WandB logging pages for [GPT-4](https://wandb.ai/agentboard/llm-agent-eval-gpt-4-all), [GPT-3.5-Turbo](https://wandb.ai/agentboard/llm-agent-eval-gpt-35-turbo-all), and [DeepSeek-67b](https://wandb.ai/agentboard/llm-agent-eval-deepseek-67b-all).

## 6. Data

### 6.1 Data Overview
AgentBoard is composed of 9 diverse tasks which can be divided into 4 types, including **Embodied AI**, **Game**, **Web**, and **Tool**:



<table align="center">
  <tbody>
    <tr align="center" valign="bottom">
      <td>
        <b>Embodied AI</b>
      </td>
      <td>
        <b>Game</b>
      </td>
      <td>
        <b>Web</b>
      </td>
      <td>
        <b>Tool</b>
      </td>
    </tr>
    <tr valign="top">
<td>

- AlfWorld
- ScienceWorld
- BabyAI

</td>

<td>

- Jericho
- PDDL

</td>

<td>

- WebShop
- WebArena

</td>

<td>

- Tool-Query
- Tool-Operation

</td>

  </tr>
  </tbody>
</table>


To help researchers quickly understand evaluation data of each task, we provide **Dataset Viewer** at Huggingface Dataset: [🤗 AgentBoard](https://huggingface.co/datasets/hkust-nlp/agentboard).

> Note: Please download the dataset from the link provided below for the reason that the data in Dataset Viewer is not complete.

### 6.2 Download Link
You can download the whole evaluation data by running the following command:
```shell
wget https://huggingface.co/datasets/hkust-nlp/agentboard/resolve/main/data.tar.gz
```
Please uncommpress the file and move the data to `AgentBoard/data`.
```shell
cd AgentBoard
mkdir data
tar -zxvf data.tar.gz
```

The file structure of evaluation data is as follows:
<details>
<summary>
Click to expand the file structure
</summary>

```
data
├── baseline_results
├── alfworld
│   ├── alfred.pddl # additional data for alfworld
│   ├── alfred.twl2 # additional data for alfworld
│   ├── json_2.1.1  # additional data for alfworld
│   └── test.jsonl
├── babyai
│   └── test.jsonl
├── jericho
│   ├── test.jsonl
│   └── z-machine-games-master  # additional data for jericho
├── pddl
│   └── test.jsonl
├── scienceworld
│   └── test.jsonl
├── tool-operation
│   └── test.jsonl
├── tool-query
│   ├── academia  # additional data for academia tool
│   └── test.jsonl
├── webarena
│   └── test.jsonl
└── webshop
    └── test.jsonl
```

**We also provide baseline run loggings in `data/baseline_results`, which can be used for visualization in our panel. **

</details>

### 6.3 Data Fields
We take an instance from the `ScienceWorld` task as an example to illustrate the data fields of evaluation data.
```json
{
  "task": "scienceworld",
  "id": 0,
  "goal": "Your task is to find the animal with the longest life span.  The animals are in the 'outside' location.  Focus on the animal with the longest life span.",
  "subgoals": ["You move to the outside.", "You focus on the crocodile egg."],
  "difficulty": "easy",
  "additional_info": {"var": 5, "env_name": "lifespan-longest-lived"}
}
```
Details of the data fields are as follows:
| Field Name | Description |
|------------|-------------|
| `task` | The task name of the example, e.g. `alfworld`, `babyai`, `jericho`, `pddl`, `scienceworld`, `tool-operation`, `tool-query`, `webarena`, `webshop`. |
| `id` | The id of the example. |
| `goal` | The goal of the example. |
| `subgoals` | The subgoals of the example which adopts subgoal as progress rate metric. |
| `difficulty` | The difficulty of the example, e.g. `easy`, `hard`. |
| `additional_info` | The additional information of the example, each example has its own additional information. |

## 7. Evaluation
### 7.1 Evaluation Preparation

#### Internet Access
For regions with Internet restrictions, to evaluate the **Tool-Query**, **Tool-Operation** and **WebArena** tasks, please make sure that the machine can access the Internet.

You can check whether you have network issues by observing the output during the execution process.

#### Environment Preparation
We provide two ways to install the environment of AgentBoard, as specified in [QuickStart](#setup-environment).


### 7.2 Running Proprietary Models
In this section, we provide a script to evaluate the closed-source models on each task.

Please do not forget to set the environment variables (e.g., `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) before running the following commands.

#### For Tasks except WebShop
We provide a quick start script to evaluate the `gpt-3.5-turbo-0613` model on `alfworld` task.

```shell
python agentboard/eval_main.py \
    --cfg-path eval_configs/main_results_all_tasks.yaml \
    --tasks alfworld \
    --model gpt-3.5-turbo-0613 \
    --wandb \
    --log_path ./results/gpt-3.5-turbo-0613 \
    --project_name evaluate-gpt-35-turbo-0613 \
    --baseline_dir ./data/baseline_results
```
Parameters:
- `--cfg-path`: The path of the config file, please refer to `eval_configs/main_results_all_tasks.yaml` for more details.
- `--tasks`: The tasks to be evaluated, e.g. `tool-query`, `tool-operation`, `webarena`, `alfworld`, `babyai`, `jericho`, `pddl`, `scienceworld`.
- `--model`: The LLM to be evaluated. We provide some LLM models, including:
  - `gpt-3.5-turbo`
  - `gpt-3.5-turbo-16k`
  - `gpt-4`
  - `text-davinci-003`
  - `claude2`
- `wandb`: Online visualization will be launched given this parameter. Remove this parameter from the script if you don't need visualization, e.g. during debugging.
- `log_path`: Path to save logs, as specified [here](#check-and-analyze-results).
- `project_name`: Project name for Weights&Bias. This parameter is not necessary when wandb parameter is not used.
- `baseline_dir`: Directory to results files of baseline models you want to compare with during the run.

#### For WebShop

First, please start the WebShop server by running the following commands:
```shell
cd ./agentboard/environment/WebShop
bash ./run_dev.sh
cd ../../..
```

Then, run the following command to evaluate the `gpt-3.5-turbo-0613` model on `webshop` task.
```shell
python agentboard/eval_main.py \
    --cfg-path eval_configs/main_results_all_tasks.yaml \
    --tasks webshop \
    --model gpt-3.5-turbo-0613 \
    --wandb \
    --log_path ./results/gpt-3.5-turbo-0613 \
    --project_name evaluate-gpt-35-turbo-0613 \
    --baseline_dir ./data/baseline_results
```

### 7.3 Running Open-source Models
In AgentBoard, we have pre-supported the following 8 open-source models, by default we use `vLLM` to speed up inference.
  - `llama2-13b`
  - `llama2-34b`
  - `codellama-13b`
  - `codellama-34b`
  - `vicuna-13b-16k`
  - `lemur-70b`
  - `deepseek-67b`
  - `mistral-7b`

> Please refer to `eval_configs/main_results_all_tasks.yaml` for more details about these models.


To evaluate these models, you can run the following command:
```shell
python agentboard/eval_main.py \
    --cfg-path eval_configs/main_results_all_tasks.yaml \
    --tasks ${TASK_NAME} \
    --model ${OPEN_SOURCE_MODEL_NAME}
```
We also provide LLM customizations, please refer to [7.5 LLM Customization](#75-llm-customization) for more details.


### 7.4 Code Structure

The code structure of AgentBoard project is as follows:
```txt
AgentBoard
├── agentboard
│  ├── agents/              # Implementations of different llm-based agents
│  ├── common/              # Registers for different tasks, models and agents
│  ├── environment/         # The environment for each task
│  ├── eval_main.py         # The main python script for evaluation
│  ├── llm/                 # Inference interfaces for different LLMs
│  ├── prompts/             # Prompt files for each task
│  ├── tasks/               # The tasks for evaluation
│  ├── utils/               # Some useful utils
├── data/                # The evaluation data
├── eval_configs/        # The config files for evaluation
├── README.md
├── requirements.txt     # The requirements for running this project
├── results/             # The evaluation results after running eval_main.py
├── scripts/
├── setup.sh
└── wandb/               # The wandb files for visualization
```

There are four main parts in AgentBoard project, and the relationship between them is as follows:
<div align="center">

<img src="./assets/code_structure.png" width="400">

</div>

### 7.5 LLM Customization

Please refer to [llm_customization.md](./assets/llm_customization.md) for more details about LLM customization.


### 7.6 Agent Customization

Please refer to [agent_customization.md](./assets/agent_customization.md) for more details about agent customization.


### 7.7 Runtime Estimation

The evaluation runtime for a language model depends on the device/API, model, and inference architecture used. In the case of open-source LLMs, the vllm inference speed is approximately 10 times faster than the huggingface pipeline.

To estimate the total time needed for evaluation, you can run a few steps to measure the inference speed and multiply it by the total number of LLM inferences, which is within 15,000 rounds.

The general formula for estimating the total time is `4h * speed`. Here are some examples of our runtime:

|     Model     | Device/API | Inference Architecture | Inference Speed | Total-time |
|:-------------:|:----------:|:----------------------:|:---------------:|:----------:|
|      GPT4     |  azure API |            -           |    1.5s/round   |    5.5h    |
| GPT-3.5-Turbo |  azure API |            -           |     1s/round    |     3h     |
| DeepSpeed-67b |   8*V100   |          vllm          |     5s/round    |    18.5h   |
|   Llama2-70b  |   8*V100   |          vllm          |     8s/round    |     28h    |
|   Llama2-70b  |   4*A100   |          vllm          |     4s/round    |   13.5h    |

## ️8. Citation
If you find this repository useful, please consider giving star and citing our paper:
```
@misc{ma2024agentboard,
      title={AgentBoard: An Analytical Evaluation Board of Multi-turn LLM Agents}, 
      author={Chang Ma and Junlei Zhang and Zhihao Zhu and Cheng Yang and Yujiu Yang and Yaohui Jin and Zhenzhong Lan and Lingpeng Kong and Junxian He},
      year={2024},
      eprint={2401.13178},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}

```

## 9. License
[![Apache-2.0 license](https://img.shields.io/badge/Code%20License-Apache--2.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

The AgentBoard codebase is licensed under a [Apache-2.0 License](https://www.apache.org/licenses/LICENSE-2.0).

[![GPL-2.0](https://img.shields.io/badge/Data%20License-GPL--2.0-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html)

The AgentBoard dataset is licensed under a
[GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html).

<!-- 
## 10. Acknowledgements
- Alfworld, ScienceWorld...
- We would like to express our gratitude to [Open-Meteo](https://open-meteo.com/), [The Movie Database](https://www.themoviedb.org/), [Aminer](https://www.aminer.org/citation), [Todoist](https://todoist.com/) and [Google Sheets](https://www.google.com/sheets/about/) for making their APIs or data available. -->
