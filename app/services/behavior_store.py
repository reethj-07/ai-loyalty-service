# app/services/behavior_store.py

from app.domain.behavior import BehaviorSignal
from app.repositories.behavior_repository import BehaviorRepository


class BehaviorStore:
    def __init__(self, repo: BehaviorRepository):
        self.repo = repo

    def save(self, signal: BehaviorSignal):
        self.repo.insert(signal)
