import io
import base64
from typing import List, Dict, Any, TypedDict, Union, Tuple
import numpy as np
import numpy.typing as npt
from PIL import Image
import re
from beartype import beartype
from beartype.door import is_bearable
from pathlib import Path

from .actions import Action, ActionTypes, action2str, create_stop_action, is_equivalent, ActionParsingError
from .env_config import URL_MAPPINGS
from .processors import ObservationMetadata
from .utils import StateInfo


Trajectory = List[Union[Action, StateInfo]]

HTML_TEMPLATE = """
<!DOCTYPE html>
<head>
    <style>
        pre {{
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
    </style>
</head>
<html>
    <body>
     {body}
    </body>
</html>
"""


@beartype
def map_url_to_real(url: str) -> str:
    """Map the urls to their real world counterparts"""
    for i, j in URL_MAPPINGS.items():
        if i in url:
            url = url.replace(i, j)
    return url


@beartype
def map_url_to_local(url: str) -> str:
    """Map the urls to their local counterparts"""
    for i, j in URL_MAPPINGS.items():
        if j in url:
            url = url.replace(j, i)
    return url


@beartype
def _extract_action(response: str) -> str:
    action_splitter = "@"
    pattern = rf"{action_splitter}((.|\n)*?){action_splitter}"
    match = re.search(pattern, response)
    if match:
        return match.group(1).strip()
    else:
        raise ActionParsingError(
            f"Cannot parse action from response, please check your input and ensure that the action is wrapped inside "
            f"a pair of {action_splitter} and enclose arguments within [] as follows: {action_splitter}action [arg]"
            f"{action_splitter} "
        )


@beartype
def extract_action(response: str) -> str:
    response = _extract_action(response)
    response = map_url_to_local(response)
    return response


def get_render_action(
        action: Action,
        observation_metadata: Dict[str, ObservationMetadata],
        action_set_tag: str,
) -> str:
    """Parse the predicted actions for rendering purpose. More comprehensive information"""
    if action_set_tag == "id_accessibility_tree":
        text_meta_data = observation_metadata["text"]
        if action["element_id"] in text_meta_data["obs_nodes_info"]:
            node_content = text_meta_data["obs_nodes_info"][
                action["element_id"]
            ]["text"]
        else:
            node_content = "No match found"

        action_str = f"<div class='raw_parsed_prediction' style='background-color:grey'><pre>{action['raw_prediction']}</pre></div>"
        action_str += f"<div class='action_object' style='background-color:grey'><pre>{repr(action)}</pre></div>"
        action_str += f"<div class='parsed_action' style='background-color:yellow'><pre>{action2str(action, action_set_tag, node_content)}</pre></div>"

    elif action_set_tag == "playwright":
        action_str = action["pw_code"]
    else:
        raise ValueError(f"Unknown action type {action['action_type']}")
    return action_str


class RenderHelper(object):
    """Helper class to render text and image observations and meta data in the trajectory"""

    def __init__(
            self, config_file: Dict, result_dir: str, action_set_tag: str
    ) -> None:

        _config_str = ""
        for k, v in config_file.items():
            _config_str += f"{k}: {v}\n"
        _config_str = f"<pre>{_config_str}</pre>\n"
        task_id = config_file["task_id"]

        self.action_set_tag = action_set_tag

        self.render_file = open(
            Path(result_dir) / f"render_{task_id}.html", "a+"
        )
        self.render_file.truncate(0)
        # write init template
        self.render_file.write(HTML_TEMPLATE.format(body=f"{_config_str}"))
        self.render_file.read()
        self.render_file.flush()

    def render(
            self,
            action: Action,
            state_info: StateInfo,
            meta_data: Dict[str, Any],
            render_screenshot: bool = False,
    ) -> None:
        """Render the trajectory"""
        # text observation
        observation = state_info["observation"]
        text_obs = observation["text"]
        info = state_info["info"]
        new_content = f"<h2>New Page</h2>\n"
        new_content += f"<h3 class='url'><a href={state_info['info']['page'].url}>URL: {state_info['info']['page'].url}</a></h3>\n"
        new_content += f"<div class='state_obv'><pre>{text_obs}</pre><div>\n"

        if render_screenshot:
            # image observation
            img_obs = observation["image"]
            image = Image.fromarray(img_obs)
            byte_io = io.BytesIO()
            image.save(byte_io, format="PNG")
            byte_io.seek(0)
            image_bytes = base64.b64encode(byte_io.read())
            image_str = image_bytes.decode("utf-8")
            new_content += f"<img src='data:image/png;base64,{image_str}' style='width:50vw; height:auto;'/>\n"

        # meta data
        new_content += f"<div class='prev_action' style='background-color:pink'>{meta_data['action_history'][-1]}</div>\n"

        # action
        action_str = get_render_action(
            action,
            info["observation_metadata"],
            action_set_tag=self.action_set_tag,
        )
        # with yellow background
        action_str = f"<div class='predict_action'>{action_str}</div>"
        new_content += f"{action_str}\n"

        # add new content
        self.render_file.seek(0)
        html = self.render_file.read()
        html_body = re.findall(r"<body>(.*?)</body>", html, re.DOTALL)[0]
        html_body += new_content

        html = HTML_TEMPLATE.format(body=html_body)
        self.render_file.seek(0)
        self.render_file.truncate()
        self.render_file.write(html)
        self.render_file.flush()

    def close(self) -> None:
        self.render_file.close()


def get_action_description(
        action: Action,
        observation_metadata: Dict[str, ObservationMetadata],
        action_set_tag: str,
) -> str:
    """Generate the text version of the predicted actions to store in action history for prompt use.
    May contain hint information to recover from the failures"""

    if action_set_tag == "id_accessibility_tree":
        text_meta_data = observation_metadata["text"]
        if action["action_type"] in [
            ActionTypes.CLICK,
            ActionTypes.HOVER,
            ActionTypes.TYPE,
        ]:
            action_name = str(action["action_type"]).split(".")[1].lower()
            if action["element_id"] in text_meta_data["obs_nodes_info"]:
                node_content = text_meta_data["obs_nodes_info"][
                    action["element_id"]
                ]["text"]
                node_content = " ".join(node_content.split()[1:])
                action_str = action2str(
                    action, action_set_tag, node_content
                )
            else:
                action_str = f"Attempt to perfom \"{action_name}\" on element \"[{action['element_id']}]\" but no matching element found. Please check the observation more carefully."
        else:
            if (
                    action["action_type"] == ActionTypes.NONE
            ):
                action_splitter = "@"
                action_str = f'The previous prediction you issued was "{action["raw_prediction"]}". However, the format was incorrect. Ensure that the action is wrapped inside a pair of {action_splitter} and enclose arguments within [] as follows: {action_splitter}action [arg] ...{action_splitter}.'
            else:
                action_str = action2str(action, action_set_tag, "")

    elif action_set_tag == "playwright":
        action_str = action["pw_code"]

    else:
        raise ValueError(f"Unknown action type {action['action_type']}")

    return action_str


def log_progress_score(env, result_dic, logger):
    if "url_score" in result_dic and "content_score" in result_dic:
        score_label = "CONTENT SCORE + URL SCORE"
        score_detail = ["Domain", "Parameter", "Query"] + ['<split>'] + env.progress_content
    elif "url_score" in result_dic:
        score_label = "URL SCORE"
        score_detail = "(Domain, Parameter, Query)"
    else:
        score_label = "CONTENT SCORE"
        score_detail = env.progress_content

    logger.info(f"Progress Score({score_label}): {env.progress_score}")
    logger.info(f"Progress Score Detail:({score_detail}) {env.detail_score}")


def transform_format(data):  # transform the format from test.jsonl to available format
    return {
        "sites": data["additional_info"]["sites"],
        "task_id": data["original_task_id"],
        "require_login": data["additional_info"]["require_login"],
        "storage_state": data["additional_info"]["storage_state"],
        "start_url": data["additional_info"]["start_url"],
        "geolocation": data["additional_info"]["geolocation"],
        "intent_template": data["additional_info"]["intent_template"],
        "instantiation_dict": data["additional_info"]["instantiation_dict"],
        "intent": data["goal"],
        "require_reset": data["additional_info"]["require_reset"],
        "eval": data["additional_info"]["eval"],
        "intent_template_id": data["additional_info"]["intent_template_id"],
        "difficulty": data["difficulty"]
    }


def early_stop(  # Determine the need for early termination, including repeated output of incorrect results
        # and repeated output of the same results
        trajectory: Trajectory, thresholds: Dict[str, int]
) -> Tuple[bool, str]:
    """Check whether need to early stop"""

    last_k_actions: List[Action]
    action_seq: List[Action]

    # Case: parsing failure for k times
    k = thresholds["parsing_failure"]
    last_k_actions = trajectory[1::2][-k:]
    if len(last_k_actions) >= k:
        if all(
                [
                    action["action_type"] == ActionTypes.NONE
                    for action in last_k_actions
                ]
        ):
            return True, True, f"Failed to parse actions for {k} times"
    # Case: same action for k times
    k = thresholds["repeating_action"]
    last_k_actions = trajectory[1::2][-k:]
    action_seq = trajectory[1::2]

    if len(action_seq) == 0:
        return False, False, ""

    last_action: Action = action_seq[-1]
    if last_action["action_type"] == ActionTypes.SCROLL:  # SCROLL could be repeated more times
        if len(last_k_actions) >= k * 2:
            if all(
                    [
                        is_equivalent(action, last_action)
                        for action in last_k_actions
                    ]
            ):
                return True, False, f"Same action for {k * 2} times"

    if last_action["action_type"] != ActionTypes.TYPE and last_action["action_type"] != ActionTypes.SCROLL:
        if len(last_k_actions) >= k:
            if all(
                    [
                        is_equivalent(action, last_action)
                        for action in last_k_actions
                    ]
            ):
                return True, False, f"Same action for {k} times"
    else:
        if (
                sum([is_equivalent(action, last_action) for action in action_seq])
                >= k
        ):
            return True, False, f"Same typing action for {k} times"

    return False, False, ""
