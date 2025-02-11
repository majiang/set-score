import dataclasses
import datetime
import enum
import json
import logging
import typing

import dacite

from gb import pws

logger = logging.getLogger(__name__)

Seat = typing.Literal["east", "south", "west", "north", None]


@dataclasses.dataclass
class PlayerScore:
    player: str
    point: int
    seat: Seat = None

class ErrorType(enum.Enum):
    NOT_4_PLAYER = "not 4-player"
    SEATS_MISMATCH = "seats mismatch"
    NON_ZERO_SUM = "non-zero-sum points"
    UNKNOWN = "__UNKNOWN__"

class ErrorHandler(enum.Enum):
    DROP = "drop"
    RESUME = "resume"
    RAISE = "raise"

class ScoreError:
    message: str = ""
    handler: typing.Optional[typing.Callable] = None

@dataclasses.dataclass
class InputGameScore:
    result: list[PlayerScore]
    known_errors: typing.Optional[dict[ErrorType, ErrorHandler]]

    def validate(self):
        seats: set[Seat] = set()
        players = set()
        point_sum = 0
        for player_score in self.result:
            seats.add(player_score.seat)
            players.add(player_score.player)
            point_sum += player_score.point

        found_errors: list[ErrorType] = []
        if seats != set(("east", "south", "west", "north")) and seats != set([None]):
            found_errors.append(ErrorType.SEATS_MISMATCH)
        if len(players) != 4:
            found_errors.append(ErrorType.NOT_4_PLAYER)
        if point_sum != 0:
            found_errors.append(ErrorType.NON_ZERO_SUM)

        for found_error in found_errors:
            if not (self.known_errors and found_error in self.known_errors):
                raise ValueError(f"Error found: {found_error}")
        if self.known_errors:
            for known_error in self.known_errors:
                if known_error not in found_errors:
                    raise ValueError(f"Expected error not found: {known_error}")
                handler = self.known_errors[known_error]
                if handler == ErrorHandler.RAISE:
                    raise ValueError(f"Error found: {known_error}")
                logger.warning(f"Error found: {known_error}")
        return ValidatedGameScore(self.result, self.known_errors)

@dataclasses.dataclass
class ValidatedGameScore():
    result: list[PlayerScore]
    errors: typing.Optional[dict[ErrorType, typing.Literal[ErrorHandler.DROP, ErrorHandler.RESUME]]]

@dataclasses.dataclass
class Variant:
    flower: typing.Optional[bool]
    reseat: typing.Optional[typing.Literal[1, 3]]

@dataclasses.dataclass
class InputSetScore:
    date: typing.Optional[datetime.date]
    variant: typing.Optional[Variant]
    scores: list[InputGameScore]

    def validate(self):
        vss: list[ValidatedGameScore] = []
        for i, score in enumerate(self.scores):
            try:
                vs = score.validate()
            except ValueError as e:
                logger.error(f"{self.date}[{i}]: {e}")
                raise
            if vs.errors:
                logger.warning(f"{self.date}[{i}]: {vs.errors}")
            vss.append(vs)
        return ValidatedSetScore(self.date, self.variant, vss)

@dataclasses.dataclass
class ValidatedSetScore:
    date: typing.Optional[datetime.date]
    variant: typing.Optional[Variant]
    scores: list[ValidatedGameScore]


def read_json_validate(filename: str) -> ValidatedSetScore:
    data = json.load(open(filename))
    score: InputSetScore = dacite.from_dict(
        InputSetScore,
        data,
        config=dacite.Config(type_hooks={
            datetime.date: datetime.date.fromisoformat,
            ErrorType: ErrorType,
            ErrorHandler: ErrorHandler,
        }),
    )
    return score.validate()

@dataclasses.dataclass(order=True)
class PersonalDayResult:
    player: str
    n_games: int
    total_tp12: int
    total_mp: int

    def __str__(self):
        return f"{self.player}:\t{self.total_tp12/12}\t{self.total_mp}\t/{self.n_games}"

@dataclasses.dataclass
class DayResult:
    scores: list[PersonalDayResult]

    @classmethod
    def from_set_score(cls, set_score: ValidatedSetScore):
        ret: dict[str, PersonalDayResult] = {}
        for game_score in set_score.scores:
            tp12s = get_tp12([player_score.point for player_score in game_score.result])
            for (player_score, tp12) in zip(game_score.result, tp12s):
                if player_score.player not in ret:
                    ret[player_score.player] = PersonalDayResult(player_score.player, 0, 0, 0)
                ret[player_score.player].n_games += 1
                ret[player_score.player].total_tp12 += tp12
                ret[player_score.player].total_mp += player_score.point
        return DayResult(sorted(ret.values()))

    def __str__(self):
        return "\n".join(str(score) for score in self.scores)

def get_tp12(points: list[int]):
    ret = [0] * 4
    for i in range(4):
        for j in range(4):
            if i == j:
                continue
            ret[i] += (points[j] < points[i]) + (points[j] <= points[i])
    top_score = max(ret)
    top_bonus = 12 / (7 - top_score)
    top_score *= 6
    for i in range(4):
        ret[i] *= 6
        if ret[i] == top_score:
            ret[i] += top_bonus
    return ret
