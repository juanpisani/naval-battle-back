import logging
import threading
import uuid
from collections import OrderedDict
from typing import Any, Mapping, Optional
import numpy

import attr
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

log = logging.getLogger(__name__)


@attr.s
class Cell:
    x: int = attr.ib(validator=attr.validators.instance_of(int))
    y: int = attr.ib(validator=attr.validators.instance_of(int))
    is_hit: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)
    has_boat_part: bool = attr.ib(validator=attr.validators.instance_of(bool), default=False)

    def shot(self):
        self.is_hit = True

    def set_boat_part(self):
        self.has_boat_part = True

    def to_json(self) -> Mapping[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "is_hit": self.is_hit,
            "has_boat_part": self.has_boat_part,
        }


@attr.s
class Player:
    user_id = attr.ib()
    boats_parts_left: int = attr.ib(default=20)

    def get_shot(self):
        self.boats_parts_left = self.boats_parts_left - 1

    @staticmethod
    def from_dict(state_dict):
        return Player(
            user_id=state_dict["userId"],
            boats_parts_left=state_dict["boats_parts_left"],
        )

    def to_json(self) -> Mapping[str, Any]:
        return {
            "user_id": self.user_id,
            "boats_parts_left": self.boats_parts_left,
        }


# todo el board donde guesseamos el del oponente, que no tiene los boards
@attr.s
class Board:
    owner: Player = attr.ib(validator=attr.validators.instance_of(Player))
    # mhmhm y ahora de que nos disfrazamos?
    dimensions: Cell[[]] = attr.ib(default=numpy.empty((10, 10), dtype=Cell))

    # blocks: Set[Cell] = attr.ib(default=attr.Factory(set))

    @staticmethod
    def from_dict(state_dict):
        return Board(
            dimensions=Cell(**state_dict["board"]),
            owner=state_dict["owner"]
        )

    def to_json(self) -> Mapping[str, Any]:
        return {
            "owner": self.owner.to_json(),
            "dimensions": self.dimensions.to_json()
        }


@attr.s
class State:
    boards: Mapping[str, Board] = attr.ib(
        default=attr.Factory(dict), validator=attr.validators.instance_of(Board)
    )
    players: Mapping[str, Player] = attr.ib(default=attr.Factory(dict))

    @staticmethod
    def from_dict(state_dict) -> "State":
        return State(
            boards=[Board.from_dict(board) for board in state_dict["boards"]],
            players=[Player.from_dict(player) for player in state_dict["players"]],
        )

    def to_json(self) -> Mapping[str, Any]:
        return {
            "boards": [board.to_json() for board in self.boards],
            "players": [player.to_json() for player in self.players],
        }


class GameEngine(threading.Thread):
    # dimensions = [10, 10]
    player_turn = 0

    def __init__(self, group_name, **kwargs):
        log.info("Init GameEngine...")
        super(GameEngine, self).__init__(daemon=True, name="GameEngine", **kwargs)
        self.name = uuid.uuid4()
        self.group_name = group_name
        self.channel_layer = get_channel_layer()
        # self.state = State(board=Board(dimensions=Cell(*self.dimensions)))
        # mhmh again
        self.state = State()
        self.player_queue = OrderedDict()
        self.player_lock = threading.Lock()

    def run(self):
        log.info("Starting engine loop")
        while True:
            self.broadcast_state(self.state)

    #         mmhmh if winner exit loop?

    def broadcast_state(self, state: State):
        state_json = state.to_json()
        async_to_sync(self.channel_layer.group_send)(
            self.group_name, {"type": "game_update", "state": state_json}
        )

    def next_turn(self) -> State:
        # check if players son solo 1, entonces ganaste perro
        self.player_turn += 1
        log.info("Turn %d for game %s", self.player_turn, self.name)
        state = self.state
        # mhmh hace falta? si en el init pones que reciba solo 2 players no hace falta meter gente a mitad del game
        # mhm pero si se le cae el juego al breo?
        state = self.process_new_players(state)
        # de donde saco el player y la cell? (ponele que el player lo pueda sacar del turn)
        state = self.check_winner(state)
        return state

    def join_queue(self, player: str, at_front=False) -> None:
        log.info("Player %s joining queue (Front? %r)", player, at_front)
        if player in self.state.players:
            log.info("Player %s is already in a game", player)
            return

        if len(self.player_queue) > 2:
            log.warning("Game capacity full")
            return

        # mhmhm this
        with self.player_lock:
            self.player_queue[player] = True
            if at_front:
                self.player_queue.move_to_end(player, last=False)

    # mhmmhmh doubt (x)
    def get_queued_player(self) -> Optional[str]:
        log.info("Getting next player in queue")
        with self.player_lock:
            try:
                player, _ = self.player_queue.popitem(last=False)
                return player
            except KeyError:
                # no player queued
                return None

    def check_winner(self, state: State) -> State:
        log.info("Checking winner")
        dead = [user_id for user_id, player in state.players.items() if player.boats_parts_left == 0]
        for user_id in dead:
            log.info("Player %s lost", user_id)
            state.players.pop(user_id)
        #     mmhmh tengo un player y ahora que?
        return state

    # todo llevar a utils
    @staticmethod
    def without_keys(map, keys):
        return {k: v for k, v in map.items() if k not in keys}

    @staticmethod
    def get_cell(board: Board, x: int, y: int) -> Cell:
        for cells in board.dimensions:
            for cell in cells:
                if cell.x == x and cell.y == y:
                    return cell if not cell.is_hit else None

    def shoot(self, player, shoot) -> None:
        log.info("Player shooting: %s", player)
        (opponent_id, opponent_player) = self.without_keys(self.state.players, player)
        opponent_board = [board for board in self.state.boards.values() if board.owner.user_id == opponent_id][0]
        cell = self.get_cell(opponent_board, shoot.x, shoot.y)
        if cell:
            cell.shot()
            if cell.has_boat_part:
                opponent_player.get_shot()
                if opponent_player.boats_parts_left == 0:
                    #                 todo gano el que shoteo y ahora que prro?
                    pass

    #     if not cell? no pudo shotear el breo

    def set_pieces(self, player, cells_with_boats_parts) -> None:
        log.info("Player setting pieces: %s", player)
        own_board = [board for board in self.state.boards.values() if board.owner.user_id == player][0]
        for cell in cells_with_boats_parts:
            self.get_cell(own_board, cell[0], cell[1]).set_boat_part()

    def process_new_players(self, state: State) -> State:
        log.info("Processing new players for game: %s", self.name)
        user_id = self.get_queued_player()
        if not user_id:
            return state

        # check if player has already lost
        player = state.players.pop(user_id, None)
        if player:
            log.info("Player %s is rejoining.", player)

        log.info("Player joining %s", user_id)

        # generate random position and add to state
        dims = self.dimensions
        # setupear piezas segun como vienen
        # c = Coords(x=random.randint(0, dims[0] - 1), y=random.randint(0, dims[1] - 1))

        p = Player(user_id=user_id)
        state.players[user_id] = p
        log.info("New player %s added", user_id)
        return state
