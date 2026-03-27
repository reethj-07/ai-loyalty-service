from abc import ABC, abstractmethod
from typing import Dict, List


class BehaviorRepository(ABC):

    @abstractmethod
    def get_behavior_state(self, member_id: str) -> Dict:
        pass

    @abstractmethod
    def save_behavior_state(self, member_id: str, state: Dict):
        pass

    @abstractmethod
    def store_event(self, member_id: str, event: Dict):
        pass
