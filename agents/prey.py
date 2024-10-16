from agents.random_agent import Random
from utils.utils import HARE_NAME, STAG_NAME


class Prey(Random):
    def __init__(self, name: str) -> None:
        assert name == HARE_NAME or name == STAG_NAME
        Random.__init__(self, name)
