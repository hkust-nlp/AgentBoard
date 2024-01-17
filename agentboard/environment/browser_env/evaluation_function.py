import json
import pdb
import re
import time
import collections
import html
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from beartype import beartype
from typing import List, Dict, Any, Tuple, Union
from .env_config import (
    ACCOUNTS,
    GITLAB,
    REDDIT,
    SHOPPING,
    SHOPPING_ADMIN,
)
import requests

from .actions import Action
import numpy as np
import urllib
from urllib.parse import urlparse
from nltk.tokenize import word_tokenize # type: ignore
from playwright.sync_api import (
    CDPSession,
    Page
)
from .utils import StateInfo
from .actions import Action

Trajectory = List[Union[Action, StateInfo]]

###help_function###
def shopping_get_auth_token() -> str:
    response = requests.post(
        url=f"{SHOPPING}/rest/default/V1/integration/admin/token",
        headers={"content-type": "application/json"},
        data=json.dumps(
            {
                "username": ACCOUNTS["shopping_site_admin"]["username"],
                "password": ACCOUNTS["shopping_site_admin"]["password"],
            }
        ),
    )
    token: str = response.json()
    return token


def shopping_get_latest_order_url() -> str:
    """Get the latest order url from the shopping website."""

    header = {
        "Authorization": f"Bearer {shopping_get_auth_token()}",
        "Content-Type": "application/json",
    }

    params = {
        "searchCriteria[sortOrders][0][field]": "created_at",
        "searchCriteria[sortOrders][0][direction]": "DESC",
        "searchCriteria[pageSize]": "1",
    }

    response = requests.get(
        f"{SHOPPING}/rest/V1/orders", params=params, headers=header
    )
    assert response.status_code == 200
    response_obj = response.json()["items"][0]
    order_id = int(response_obj["increment_id"])
    order_url = f"{SHOPPING}/sales/order/view/order_id/{order_id}/"
    return order_url


def shopping_get_sku_latest_review_author(sku: str) -> str:
    """Get the latest review for shopping admin."""
    header = {
        "Authorization": f"Bearer {shopping_get_auth_token()}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{SHOPPING}/rest/V1/products/{sku}/reviews", headers=header
    )
    assert response.status_code == 200
    response_obj = response.json()
    if len(response_obj) == 0:
        return ""
    author: str = response_obj[-1]["nickname"]
    return author


def shopping_get_sku_latest_review_rating(sku: str) -> str:
    """Get the latest review for shopping admin."""
    header = {
        "Authorization": f"Bearer {shopping_get_auth_token()}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{SHOPPING}/rest/V1/products/{sku}/reviews", headers=header
    )
    assert response.status_code == 200
    response_obj = response.json()
    if len(response_obj) == 0:
        return ""
    assert response_obj[0]["ratings"][0]["rating_name"] == "Rating"
    rating: str = str(response_obj[-1]["ratings"][0]["percent"])
    return rating


def reddit_get_post_url(url: str) -> str:
    """Get the post url"""
    # Url is http://domain/f/subreddit/post_id/...
    # get domain, subreddit, post_id
    domain = urlparse(url).netloc
    tok_url = urlparse(url).path.split("/")
    # not a valid post/comment url, return the url as is
    if len(tok_url) < 4:
        return url
    if tok_url[1] != "f":
        return url
    subreddit = urlparse(url).path.split("/")[2]
    post_id = urlparse(url).path.split("/")[3]
    scheme = urlparse(url).scheme
    post_url = f"{scheme}://{domain}/f/{subreddit}/{post_id}/"
    return post_url


def gitlab_get_project_memeber_role(page: Page, account_name: str) -> str:
    # get the account index
    try:
        account_idx = page.evaluate(
            f"""(() => {{
                const elements = document.querySelectorAll("td[data-label='Account'] span.gl-avatar-labeled-sublabel");
                let index = -1;  // Default value if not found

                for(let i = 0; i < elements.length; i++) {{
                    if(elements[i].outerText === '@{account_name}') {{
                        index = i;
                        break;
                    }}
                }}

                return index;
            }})()"""
        )

        # get the role
        role: str = page.evaluate(
            f"""(() => {{
                return document.querySelectorAll("td.col-max-role span")[{account_idx}].outerText;
            }})()"""
        )
    except Exception:
        role = ""

    return role

def llm_fuzzy_match(pred: str, reference: str, question: str) -> float:
    """Check whether the prediction matches the reference with GPT-3.5"""
    messages: List[Dict[str, Any]] = []
    # construct the question to ask
    message = "Help a teacher to grade the answer of a student given a question. Keep in mind that the student may use different phrasing or wording to answer the question. The goal is to evaluate whether the answer is semantically equivalent to the reference answer.\n"
    message += f"question: {question}\n"
    message += f"reference answer: {reference}\n"
    message += "all the string 'N/A' that you see is a special sequence that means 'not achievable'\n"
    message += f"student answer: {pred}\n"
    message += "Conclude the judgement by correct/incorrect/partially correct."
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": message},
    ]
    response = ""
    # response = generate_from_openai_chat_completion(
    #     model="gpt-4",
    #     messages=messages,
    #     temperature=0,
    #     max_tokens=768,
    #     top_p=1.0,
    #     context_length=0,
    # ).lower()
    if "partially correct" in response or "incorrect" in response:
        return 0.0
    else:
        assert "correct" in response
        return 1.0

class PseudoPage:
    def __init__(self, original_page: Page, url: str):
        self.url = url
        self.original_page = original_page

    def __getattr__(self, attr: str) -> Any:
        # Delegate attribute access to the original page object
        if attr not in ["url"]:
            return getattr(self.original_page, attr)
        else:
            return getattr(self, attr)


class Evaluator(object):
    def __init__(self, eval_tag: str = "") -> None:
        self.eval_tag = eval_tag

    def __call__(
            self,
            trajectory: Trajectory,
            config_file: Dict,
            page: Union[Page, PseudoPage],
    ) -> float:
        raise NotImplementedError

    @staticmethod
    def get_last_action(trajectory: Trajectory) -> Action:
        try:
            last_action = trajectory[-1]
        except Exception:
            raise ValueError(
                "The last element of trajectory should be an action, add a fake stop action if needed"
            )

        return last_action  # type: ignore[return-value]

    @staticmethod
    def get_last_state(trajectory: Trajectory) -> StateInfo:
        try:
            last_state = trajectory[-2]
        except Exception:
            raise ValueError(
                "The second last element of trajectory should be a state, add a fake stop action if needed"
            )

        return last_state  # type: ignore[return-value]



class StringEvaluator(Evaluator):
    """Check whether the answer is correct with:
    exact match: the answer is exactly the same as the reference answer
    must include: each phrase in the reference answer must be included in the answer
    fuzzy match: the answer is similar to the reference answer, using LLM judge
    """

    @staticmethod
    @beartype
    def clean_answer(answer: str) -> str:
        answer = answer.strip()
        if answer.startswith("@") and answer.endswith("@"):
            answer = answer[1:-1]
        elif answer.startswith('"') and answer.endswith('"'):
            answer = answer[1:-1]
        return answer.lower()

    @staticmethod
    @beartype
    def exact_match(ref: str, pred: str) -> float:
        return float(
            StringEvaluator.clean_answer(pred)
            == StringEvaluator.clean_answer(ref)
        )

    @staticmethod
    @beartype
    def must_include(ref: str, pred: str, tokenize: bool = False) -> float:
        clean_ref = StringEvaluator.clean_answer(ref)
        clean_pred = StringEvaluator.clean_answer(pred)
        # tokenize the answer if the ref is a single word
        # prevent false positive (e.g, 0)
        if (
            tokenize
            and len(clean_ref) == 1
            and len(word_tokenize(clean_ref)) == 1
        ):
            tok_pred = word_tokenize(clean_pred)
            return float(clean_ref in tok_pred)
        else:
            return float(clean_ref in clean_pred)

    def __call__(
            self,
            trajectory: Trajectory,
            config_file: Dict,
            page: Union[Page, PseudoPage, None] = None,
    ) -> float:
        configs = config_file

        last_action = self.get_last_action(trajectory)
        pred = self.clean_answer(last_action.get("answer", ""))

        score = 1.0
        for approach, value in configs["eval"]["reference_answers"].items():
            if approach == "exact_match":
                score *= self.exact_match(ref=value, pred=pred)
            elif approach == "must_include":
                assert isinstance(value, List)
                for must_value in value:
                    score *= self.must_include(
                        ref=must_value,
                        pred=pred,
                        tokenize=(len(value) == 1),
                    )
            elif approach == "fuzzy_match":
                intent = configs["intent"]
                assert isinstance(value, List)
                for reference in value:
                    # score *= self.fuzzy_match(
                    #     ref=reference, pred=pred, intent=intent
                    # )
                    score = 0  # Not realize
        return score



class URLEvaluator(Evaluator):
    """Check whether the URL is exactly the same as of the reference URLs"""

    @beartype
    def __call__(
            self,
            trajectory: Trajectory,
            config_file: Dict,
            page: Union[Page, PseudoPage],
    ) -> float:
        configs = config_file

        def clean_url(url: str) -> str:
            url = str(url)
            url = url.rstrip("/")
            return url

        def parse_url(url: str) -> Tuple[str, Dict[str, List[str]]]:
            """Parse a URL into its base, path, and query components."""
            parsed_url = urllib.parse.urlparse(url)
            base_path = parsed_url.netloc + parsed_url.path
            query = urllib.parse.parse_qs(parsed_url.query)
            return base_path, query

        def parse_urls(
                urls: List[str],
        ) -> Tuple[List[str], Dict[str, set]]:
            """Parse a list of URLs."""
            base_paths = []
            queries = collections.defaultdict(set)
            for url in urls:
                base_path, query = parse_url(url)
                base_paths.append(base_path)
                for k, v in query.items():
                    queries[k].update(v)
            return base_paths, queries

        pred = clean_url(page.url)
        ref_urls = configs["eval"]["reference_url"].split(" |OR| ")
        ref_urls = [clean_url(url) for url in ref_urls]
        matching_rule = configs["eval"].get("url_note", "GOLD in PRED")
        if matching_rule == "GOLD in PRED":
            ref_base_paths, ref_queries = parse_urls(ref_urls)
            pred_base_paths, pred_query = parse_url(pred)

            base_score = float(
                any(
                    [
                        ref_base_path in pred_base_paths
                        for ref_base_path in ref_base_paths
                    ]
                )
            )
            query_score = 1.0
            for k, possible_values in ref_queries.items():
                query_score *= float(
                    any(
                        possible_ref_value in pred_query.get(k, [])
                        for possible_ref_value in possible_values
                    )
                )
            score = base_score * query_score
        else:
            raise ValueError(f"Unknown matching rule: {matching_rule}")

        return score



class HTMLContentEvaluator(Evaluator):
    """Check whether the contents appear in the page"""

    def __call__(
            self,
            trajectory: Trajectory,
            config_file: Dict,
            page: Union[Page, PseudoPage],
    ) -> float:

        configs = config_file

        targets = configs["eval"]["program_html"]

        score = 1.0
        for target in targets:
            target_url: str = target["url"]  # which url to check
            if target_url.startswith("func"):
                func = target_url.split("func:")[1]
                func = func.replace("__last_url__", page.url)
                target_url = eval(func)

            locator: str = target["locator"]  # js element locator

            # navigate to that url
            if target_url != "last":
                page.goto(target_url)
                time.sleep(3)

            # empty, use the full page
            if not locator.strip():
                selected_element = page.content()
            # use JS to select the element
            elif locator.startswith("document.") or locator.startswith(
                "[...document."
            ):
                if "prep_actions" in target:
                    try:
                        for prep_action in target["prep_actions"]:
                            page.evaluate(f"() => {prep_action}")
                    except Exception:
                        pass
                try:
                    selected_element = str(page.evaluate(f"() => {locator}"))
                    if not selected_element:
                        selected_element = ""
                    selected_element = str(selected_element)
                except Exception:
                    # the page is wrong, return empty
                    selected_element = ""
            # run program to call API
            elif locator.startswith("func:"):  # a helper function
                func = locator.split("func:")[1]
                func = func.replace("__page__", "page")
                selected_element = eval(func)
            else:
                raise ValueError(f"Unknown locator: {locator}")

            selected_element = html.unescape(selected_element)

            if "exact_match" in target["required_contents"]:
                required_contents = target["required_contents"]["exact_match"]
                cur_score = StringEvaluator.exact_match(
                    ref=required_contents, pred=selected_element
                )
                score *= float(cur_score)
                # print(f"[exact match] {cur_score}, selected element: {selected_element}, required contents: {required_contents}")
            elif "must_include" in target["required_contents"]:
                required_contents = target["required_contents"]["must_include"]
                assert isinstance(required_contents, list)
                for content in required_contents:
                    content_or = content.split(" |OR| ")
                    cur_score = any(
                        [
                            StringEvaluator.must_include(
                                ref=content,
                                pred=selected_element,
                                tokenize=False,
                            )
                            for content in content_or
                        ]
                    )
                    score *= float(cur_score)
                    # print(f"[must include] {cur_score}, selected element: {selected_element}, required contents: {content_or}")
            else:
                raise ValueError(
                    f"Unknown required_contents: {target['required_contents'].keys()}"
                )
        return score

class EvaluatorComb:
    def __init__(self, evaluators: List[Evaluator]) -> None:
        self.evaluators = evaluators

    def __call__(
            self,
            trajectory: Trajectory,
            config_file: Dict,
            page: Union[Page, PseudoPage],
    ) -> float:
        score = 1.0
        for evaluator in self.evaluators:
            cur_score = evaluator(trajectory, config_file, page)
            score *= cur_score

        return score



def evaluator_router(config_file: Dict) -> EvaluatorComb:
    """Router to get the evaluator class"""
    configs = config_file

    eval_types = configs["eval"]["eval_types"]
    evaluators: List[Evaluator] = []
    for eval_type in eval_types:
        if eval_type == "string_match":
            evaluators.append(StringEvaluator())
        elif eval_type == "url_match":
            evaluators.append(URLEvaluator())
        elif eval_type == "program_html":
            evaluators.append(HTMLContentEvaluator())
        else:
            raise ValueError(f"eval_type {eval_type} is not supported")

    return EvaluatorComb(evaluators)


#####################
# calculate the progress score

class EvaluatorPartial(Evaluator):

    def __call__(
            self,
            trajectory: Trajectory,
            config_file: Dict,
            page: Union[Page, PseudoPage],
    ) -> float:
        raise NotImplementedError



class URLSoftEvaluator(EvaluatorPartial):
    """Parse the URL and compare the domain, parameters and query"""

    def clean_url(self, url: str) -> str:
        url = str(url)
        url = url.rstrip("/")
        return url

    def lcs_length(self, segments_reference, segments_current):
        m = len(segments_reference)
        n = len(segments_current)

        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if segments_reference[i - 1] == segments_current[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]

    def prefix_match_score(self, reference_path, current_path):
        segments_reference = self.clean_url(reference_path).split("/")[1:]
        segments_current = self.clean_url(current_path).split("/")[1:]
        # match_length = min(len(segments_reference), len(segments_current))
        if len(segments_reference) <= 0:
            return 1.0
        elif len(segments_current) <= 0:
            return 0.0
        # count = 0
        # for i in range(match_length):
        #     if segments_reference[i] == segments_current[i]:
        #         count += 1
        count = self.lcs_length(segments_reference, segments_current)
        return count / len(segments_reference)

    def get_param_set(self, query: Dict[str, List[str]]) -> set:
        param_set = set()
        for k, v in query.items():
            for vv in v:
                param_set.add(f"{k}={vv}")
        return param_set

    def get_result(self, ref, pred):
        detail_score = []
        # parse url to get domain, parameters, etc.
        parsed_pred = urllib.parse.urlparse(self.clean_url(pred))
        parsed_ref = urllib.parse.urlparse(self.clean_url(ref))

        # Domain score
        domain_match = float(parsed_pred.netloc == parsed_ref.netloc)

        # Parameter score
        parameters_match_score = self.prefix_match_score(parsed_ref.path, parsed_pred.path)

        # calculate parameter f1
        param_set_ref = self.get_param_set(urllib.parse.parse_qs(parsed_ref.query))
        param_set_pred = self.get_param_set(
            urllib.parse.parse_qs(parsed_pred.query)
        )
        if len(param_set_pred) > 0 and len(param_set_ref) > 0:
            r = len(param_set_ref & param_set_pred) / len(param_set_ref)
            p = len(param_set_ref & param_set_pred) / len(param_set_pred)
            f1 = 2 * r * p / (r + p) if r + p > 0 else 0.0
        elif len(param_set_ref) == 0:
            progress_score = domain_match * parameters_match_score  # domain match is a must
            detail_score.extend([domain_match, parameters_match_score, 0.0])
            return detail_score, progress_score
        else:
            f1 = 0.0

        progress_score = domain_match * (f1 + parameters_match_score) * 1 / 2  # domain match is a must

        detail_score.extend([domain_match, parameters_match_score, f1])

        return detail_score, progress_score

    def __call__(
            self,
            trajectory: Trajectory,
            config_file: Dict,
            page: Union[Page, PseudoPage],
    ) -> Tuple[List[Union[int, float]], float]:
        configs = config_file

        last_state = self.get_last_state(trajectory)
        pred = last_state["info"]["page"].url
        # ref = configs["eval"]["reference_url"]
        refs = configs["eval"]["reference_url"].split(" |OR| ")
        print(f"Ref URL:{refs} _________ Present URL:{pred}")
        if len(refs) == 1:
            ref = refs[-1]
            detail_score, progress_score = self.get_result(ref, pred)
        else:
            progress_score = 0.0
            detail_score = [0.0, 0.0, 0.0]
            for ref in refs:
                tmp_detail_score, tmp_progress_score = self.get_result(ref, pred)
                if tmp_progress_score > progress_score:
                    detail_score = tmp_detail_score
                    progress_score = tmp_progress_score
            if progress_score == 0.0:
                detail_score = tmp_detail_score

        return detail_score, progress_score



class HTMLContentSoftEvaluator(EvaluatorPartial):
    """Check each target content in each step"""

    def __call__(
            self,
            trajectory: Trajectory,
            config_file: Dict,
            page: Union[Page, PseudoPage],
    ) -> Tuple[List[int], List[str]]:

        def clean(text: str) -> str:
            text = str(text)
            return text.strip().lower()

        configs = config_file

        targets = configs["eval"]["program_html"]

        content_set = []
        score_set = []
        for target in targets:
            score_s = []
            target_url: str = target["url"]  # which url to check
            if target_url.startswith("func"):  # only for final result checking not intermediate results
                pass
            # what contents to check
            required_contents = []
            if "must_include" in target["required_contents"]:
                required_contents = target["required_contents"]["must_include"]
            else:
                required_contents.append(target["required_contents"]["exact_match"])
            content_set.extend(required_contents)

            locator: str = target["locator"]  # js element locator

            # empty, use the full page
            if not locator.strip():  # used for progress detect
                selected_element = page.content()
            # use JS to select the element
            elif locator.startswith("document.") or locator.startswith(
                "[...document."
            ):  # used for progress score compute, so prep_actions is not need
                try:
                    selected_element = page.evaluate(f"() => {locator}")
                    if not selected_element:
                        selected_element = ""
                    selected_element = str(selected_element)
                except Exception:
                    # the page is wrong, return empty
                    selected_element = ""
            # run program to call API
            elif locator.startswith("func:"):  # only for final step check
                # continue
                func = locator.split("func:")[1]
                func = func.replace("__page__", "page")
                selected_element = eval(func)
            else:
                raise ValueError(f"Unknown locator: {locator}")
            required_contents_clean = [
                clean(x) for x in required_contents
            ]
            selected_element = clean(selected_element)
            for content in required_contents_clean:
                content_or = content.split(" |OR| ")
                score_s.append(int(any([x in selected_element for x in content_or])))
            score_set.extend(score_s)
        # return progress_score
        return score_set, content_set  # return score set in every step



def progress_evaluator_router(config_file: Dict):
    """Router to get the evaluator class"""
    configs = config_file

    eval_types = configs["eval"]["eval_types"]
    # reference_url = configs["eval"]["reference_url"]
    reference_url = configs["eval"]["reference_url"] if configs["eval"]["reference_url"] else None
    progress_evaluators: List[Evaluator] = []
    result_dic = {}
    for eval_type in eval_types:
        if eval_type == "string_match":
            continue
        elif eval_type == "url_match" and reference_url and reference_url.startswith('http'):
            progress_evaluators.append(URLSoftEvaluator())
            result_dic["url_score"] = 0.0
            # return result_dic, progress_evaluators
        elif eval_type == "program_html":
            progress_evaluators.append(HTMLContentSoftEvaluator())
            result_dic["content_score"] = 0.0
            # return result_dic, progress_evaluators
        else:
            raise ValueError(f"eval_type {eval_type} is not supported")
    return result_dic, progress_evaluators



