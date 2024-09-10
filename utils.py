from dataclasses import dataclass

class Move:
    pass

@dataclass
class RollDice(Move):
    diceResult: int = 0 # do not initialize, stores result when returning move
    diceCamel: int = 0  # do not initialize, stores camel that moved when returning move

@dataclass
class PlacePlusMinusOne(Move):
    tileNumber: int     # tile number from 0-15
    isPlusOne: bool     # true if +1, false if -1

@dataclass
class PlaceLegBet(Move):
    camelNumber: int    # camel number from 0-4

@dataclass
class PlaceFinalBet(Move):
    camelNumber: int    # camel number from 0-4, None when representing someone else's move (unknown)
    isBetToWin: bool    # true if betting to win, false if betting to lose

class BoardItem:
    pass

@dataclass
class CamelPile(BoardItem):
    camels: list[int]  # list of camel indices in the pile, first is at the top

@dataclass
class PlusMinusOne(BoardItem):
    isPlusOne: bool     # true if +1, false if -1
    botIndex: int       # index of bot that placed this

@dataclass
class LegBet:
    camelNumber: int    # camel number from 0-4
    winCoins: int       # coins won if this camel wins

@dataclass
class HiddenBotState:
    balance: int           # balance of bot
    legBets: list[LegBet]  # list of leg bets placed by bot
    nDiceRolls: int        # number of dice rolls bot has completed
    nFinalBetsLeft: int    # number of final bet cards bot has left

@dataclass
class FullBotState(HiddenBotState):
    finalBetsLeft: list[bool]  # list of final bets left

@dataclass
class BoardState():
    availableLegBets: list[LegBet]  # list of leg bets available to be placed
    board: list[BoardItem]          # list of board items, None if empty
    botStates: list[HiddenBotState] # list of bot states
    diceRollsDone: list[int]        # list of camel dice rolls done, None if not done
    nFinalWinnerBets: int           # number of final winner bets placed
    nFinalLoserBets: int            # number of final loser bets placed

@dataclass
class FinalBet:
    camelNumber: int
    botIndex: int

class Bot:
    # is called at the start
    def __init__(self):
        pass

    # is called for every bot after every move
    def onMoveMade(self, botIndex: int, move: Move, boardAfter: BoardState):
        pass

    # is called before your bot needs to make a move
    def calculateMove(self, yourIndex: int, boardCurrent: BoardState):
        pass