import dataclasses
import datetime
import json
import logging
import typing
from typing import Literal

import dacite

from gb import pws

logger = logging.getLogger(__name__)

Seat = Literal["east", "south", "west", "north", None]


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
        assert seats == set(("east", "south", "west", "north")) or seats == set(None)
        assert len(players) == 4
        assert point_sum == 0


@dataclasses.dataclass
class SetScore:
    date: typing.Optional[datetime.date]
    scores: list[GameScore]

    def validate(self):
        for score in self.scores:
            score.validate()


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
