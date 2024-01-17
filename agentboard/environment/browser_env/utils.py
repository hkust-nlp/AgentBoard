from dataclasses import dataclass
from io import BytesIO
from typing import List, Dict, Any, TypedDict, Union
import numpy as np
import numpy.typing as npt
from PIL import Image
import re
from beartype import beartype
from beartype.door import is_bearable

@dataclass
class DetachedPage:
    url: str
    content: str  # html


def png_bytes_to_numpy(png: bytes) -> npt.NDArray[np.uint8]:
    return np.array(Image.open(BytesIO(png)))


class AccessibilityTreeNode(TypedDict):
    nodeId: str
    ignored: bool
    role: Dict[str, Any]
    chromeRole: Dict[str, Any]
    name: Dict[str, Any]
    properties: List[Dict[str, Any]]
    childIds: List[str]
    parentId: str
    backendDOMNodeId: str
    frameId: str
    bound: Union[List[float], None]
    union_bound: Union[List[float], None]
    offsetrect_bound: Union[List[float], None]


class DOMNode(TypedDict):
    nodeId: str
    nodeType: str
    nodeName: str
    nodeValue: str
    attributes: str
    backendNodeId: str
    parentId: str
    childIds: List[str]
    cursor: int
    union_bound: Union[List[float], None]


class BrowserConfig(TypedDict):
    win_top_bound: float
    win_left_bound: float
    win_width: float
    win_height: float
    win_right_bound: float
    win_lower_bound: float
    device_pixel_ratio: float


class BrowserInfo(TypedDict):
    DOMTree: Dict[str, Any]
    config: BrowserConfig


AccessibilityTree = List[AccessibilityTreeNode]
DOMTree = List[DOMNode]

Observation = Union[str, npt.NDArray[np.uint8]]


class StateInfo(TypedDict):
    observation: Dict[str, Observation]
    info: Dict[str, Any]