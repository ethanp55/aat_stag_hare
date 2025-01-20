from aat.checker import AssumptionChecker, GreedyHareChecker, GreedyPlannerHareChecker, GreedyPlannerStagChecker, \
    TeamAwareChecker
from agents.agent import Agent
from agents.greedy import Greedy
from agents.greedy_planner import GreedyPlanner
from agents.team_aware import TeamAware
from environment.state import State
from typing import List, Optional, Tuple
from utils.utils import HARE_NAME, HARE_REWARD, N_HUNTERS, STAG_NAME, STAG_REWARD


class Generator(Agent):
    def __init__(self, name: str, generator: Agent, baseline: float, hunting_hare: bool = False,
                 checker: Optional[AssumptionChecker] = None) -> None:
        Agent.__init__(self, name)
        self.generator = generator
        self.baseline = baseline
        self.checker = checker
        self.hunting_hare = hunting_hare

    def act(self, state: State, reward: float, round_num: int) -> Tuple[int, int]:
        return self.generator.act(state, reward, round_num)

    def is_hunting_hare(self) -> bool:
        return self.hunting_hare

    def check_assumptions(self, state: State) -> None:
        assert self.checker is not None
        self.checker.check_assumptions(state)

    def assumptions(self) -> List[float]:
        assert self.checker is not None
        return self.checker.assumptions()


# Goes for stag
class TeamAwareGen(Generator):
    def __init__(self, name: str, check_assumptions: bool = False) -> None:
        generator = TeamAware(name)
        checker = TeamAwareChecker(name) if check_assumptions else None
        Generator.__init__(self, name=name, generator=generator, baseline=STAG_REWARD / N_HUNTERS, hunting_hare=False,
                           checker=checker)


# Goes for stag
class GreedyPlannerStagGen(Generator):
    def __init__(self, name: str, check_assumptions: bool = False) -> None:
        generator = GreedyPlanner(name, STAG_NAME)
        checker = GreedyPlannerStagChecker(name) if check_assumptions else None
        Generator.__init__(self, name=name, generator=generator, baseline=STAG_REWARD / N_HUNTERS, hunting_hare=False,
                           checker=checker)


# Goes for hare
class GreedyHareGen(Generator):
    def __init__(self, name: str, check_assumptions: bool = False) -> None:
        generator = Greedy(name, HARE_NAME)
        checker = GreedyHareChecker(name) if check_assumptions else None
        Generator.__init__(self, name=name, generator=generator, baseline=HARE_REWARD / N_HUNTERS, hunting_hare=True,
                           checker=checker)


# Goes for hare
class GreedyPlannerHareGen(Generator):
    def __init__(self, name: str, check_assumptions: bool = False) -> None:
        generator = GreedyPlanner(name, HARE_NAME)
        checker = GreedyPlannerHareChecker(name) if check_assumptions else None
        Generator.__init__(self, name=name, generator=generator, baseline=HARE_REWARD / N_HUNTERS, hunting_hare=True,
                           checker=checker)
