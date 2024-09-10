from utils import *
import random

class SampleBot(Bot):
    def onMoveMade(self, botIndex: int, move: Move, boardAfter: BoardState):
        pass

    def calculateMove(self, yourIndex: int, boardCurrent: BoardState):
        return RollDice()

class SampleBot2(Bot):
    def onMoveMade(self, botIndex: int, move: Move, boardAfter: BoardState):
        pass

    def calculateMove(self, yourIndex: int, boardCurrent: BoardState):
        move = random.randint(0, 3)
        if move == 0:
            return RollDice()
        elif move == 1:
            return PlacePlusMinusOne(random.randint(0,15), random.randint(0,1)==1)
        elif move == 2:
            return PlaceLegBet(random.randint(0, 4))
        elif move == 3:
            return PlaceFinalBet(random.randint(0, 4), random.randint(0,1)==1)