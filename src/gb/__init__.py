import dataclasses
import datetime
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
    seat: Seat
    point: int


@dataclasses.dataclass
class GameScore:
    result: list[PlayerScore]

    def validate(self):
        seats: set[Seat] = set()
        players = set()
        point_sum = 0
        for player_score in self.result:
            seats.add(player_score.seat)
            players.add(player_score.player)
            point_sum += player_score.point
        errors: list[str] = []
        if seats != set(("east", "south", "west", "north")) and seats != set(None):
            errors.append("seats mismatch")
        if len(players) != 4:
            errors.append("not 4-player")
        if point_sum != 0:
            errors.append(f"non-zero-sum points: {[player_score.point for player_score in self.result]}")
        return errors


@dataclasses.dataclass
class Variant:
    flower: typing.Optional[bool]
    reseat: typing.Optional[typing.Literal[1, 3]]

@dataclasses.dataclass
class SetScore:
    date: typing.Optional[datetime.date]
    variant: typing.Optional[Variant]
    scores: list[GameScore]

    def validate(self):
        for i, score in enumerate(self.scores):
            errors = score.validate()
            for error in errors:
                logger.warning(f"{self.date}[{i}]: {error}")



def read_json_validate(filename: str):
    data = json.load(open(filename))
    score = dacite.from_dict(
        SetScore,
        data,
        config=dacite.Config(type_hooks={datetime.date: datetime.date.fromisoformat}),
    )
    score.validate()
    logger.info(score)
    return score

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
    def from_set_score(cls, set_score: SetScore):
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
