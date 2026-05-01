from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional, List, Dict

@dataclass
class CalendarEvent:
    title: str
    start: str
    end: Optional[str] = None
    all_day: bool = True
    description: str = ""
    location: str = ""
    categories: List[str] = field(default_factory=list)
    uid_seed: str = ""

def plugin_name() -> str:
    raise NotImplementedError

def generate(config: Dict) -> List[CalendarEvent]:
    return []
