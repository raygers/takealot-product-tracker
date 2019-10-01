from typing import List, Dict, Any
from dataclasses import dataclass, field

@dataclass()
class User:
    username: str
    password: str
    name: str
    surname: str
    plds: Dict[str, Any] = field(default_factory=dict)

@dataclass()
class UserResponse:
    username: str
    name: str
    surname: str
    plds: Dict[str, Any] = field(default_factory=dict)

