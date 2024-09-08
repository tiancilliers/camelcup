from math import ceil
import random
from utils import *
import copy

numberBots = 5
numberGames = 500

legBetScores = [5, 3, 2]
finalBetScores = [8, 5, 3, 2, 1]
startingBalance = 3

class Game:
    def __init__(self, logger=print):
        # initialise player bots
        from samplebots import SampleBot, SampleBot2
        availableBots = [SampleBot, SampleBot2]
        assert all(issubclass(bot, Bot) for bot in availableBots)
        self.bots = [random.choice(availableBots)() for i in range(numberBots)]

        # initialize board state
        self.availableLegBets = [LegBet(i+1, legBetScores[0]) for i in range(5)]
        self.board = [None for i in range(16)]
        self.botStates = [FullBotState(startingBalance, [], 0, 5, [True for j in range(5)]) for i in range(numberBots)]
        self.diceRollsDone = [0 for i in range(5)]
        self.finalWinnerBets = []
        self.finalLoserBets = []
        self.gameRunning = True

        # roll for camel starting positions
        for camelIndex in range(5):
            camelPos = random.randint(1, 3)-1
            if self.board[camelPos] == None:
                self.board[camelPos] = CamelPile([])
            self.board[camelPos].camels.append(camelIndex)
        
        # shuffle piles of camels
        for i in range(16):
            if type(self.board[i]) == CamelPile:
                random.shuffle(self.board[i].camels)

        self.botTurn = 0 # doesn't need to be randomized because bot order is randomized
        self.log = logger
        self.log("Game started")
        self.printBoard()
    
    def run(self):
        while self.gameRunning:
            self.step()

    def step(self):
        move = self.bots[self.botTurn].calculateMove(self.botTurn, self.makeBoardState(self.botTurn))
        self.log(f"Bot {self.botTurn} made move: {move}")	
        if self.validMove(move, self.botTurn):
            self.processMove(move, self.botTurn)
            for botIndex, bot in enumerate(self.bots):
                bot.onMoveMade(self.botTurn, self.sanitizeMove(move), self.makeBoardState(botIndex))
            self.botTurn = (self.botTurn + 1) % numberBots
        
    def makeBoardState(self, botIndex: int) -> BoardState:
        botStates = [HiddenBotState(botState.balance, botState.legBets, botState.nDiceRolls, botState.nFinalBetsLeft) if index != botIndex else botState for index, botState in enumerate(self.botStates)]
        boardState = BoardState(self.availableLegBets, self.board, botStates, self.diceRollsDone, len(self.finalWinnerBets), len(self.finalLoserBets))
        return copy.deepcopy(boardState)

    def validMove(self, move: Move, botIndex: int) -> bool:
        if not issubclass(type(move), Move):
            self.log("Invalid move: not a Move object")
            return False
        if type(move) is RollDice:
            if move.diceResult != 0:
                self.log("Invalid move: dice result not 0")
                return False
            if move.diceCamel != 0:
                self.log("Invalid move: camel result not 0")
                return False
            return True
        if type(move) is PlacePlusMinusOne:
            if move.tileNumber < 1 or move.tileNumber > 16:
                self.log("Invalid move: tile number out of range")
                return False
            if self.board[move.tileNumber-1] != None:
                self.log("Invalid move: tile already occupied")
                return False
            if any(type(self.board[i]) == PlusMinusOne and self.board[i].botIndex == botIndex for i in range(16)):
                self.log("Invalid move: already placed PlusMinusOne")
                return False
            if (move.tileNumber > 1 and type(self.board[move.tileNumber-2]) == PlusMinusOne) or (move.tileNumber < 16 and type(self.board[move.tileNumber]) == PlusMinusOne):
                self.log("Invalid move: PlusMinusOne cannot be placed next to another PlusMinusOne")
                return False
            return True
        if type(move) is PlaceLegBet:
            if move.camelNumber < 1 or move.camelNumber > 5:
                self.log("Invalid move: camel number out of range")
                return False
            if self.availableLegBets[move.camelNumber - 1] == None:
                self.log("Invalid move: all bets for this camel already placed")
                return False
            return True
        if type(move) is PlaceFinalBet:
            if move.camelNumber < 1 or move.camelNumber > 5:
                self.log("Invalid move: camel number out of range")
                return False
            if not self.botStates[botIndex].finalBetsLeft[move.camelNumber-1]:
                self.log("Invalid move: already placed final bet for this camel")
                return False
            return True

    def processMove(self, move: Move, botIndex: int) -> None:
        if type(move) is RollDice:
            move.diceResult = random.randint(1, 3)
            move.diceCamel = random.choice([i for i in range(5) if self.diceRollsDone[i] == 0])
            self.diceRollsDone[move.diceCamel] = move.diceResult
            self.botStates[botIndex].nDiceRolls += 1
            self.log(f"Bot {botIndex} rolled dice: {move.diceResult} for camel {move.diceCamel+1}")
            self.moveCamels(move.diceCamel, move.diceResult)
            self.printBoard()
            if self.gameRunning and not any(rollDone == 0 for rollDone in self.diceRollsDone):
                self.processLeg()
            return
        if type(move) is PlacePlusMinusOne:
            self.board[move.tileNumber-1] = PlusMinusOne(move.isPlusOne, botIndex)
            self.log(f"Bot {botIndex} placed {'+1' if move.isPlusOne else '-1'} on tile {move.tileNumber}")
            self.printBoard()
            return
        if type(move) is PlaceLegBet:
            bet = copy.deepcopy(self.availableLegBets[move.camelNumber - 1])
            self.botStates[botIndex].legBets.append(bet)
            nextBets = [val for idx,val in enumerate(legBetScores) if idx>0 and legBetScores[idx-1] == bet.winCoins]
            self.availableLegBets[move.camelNumber - 1] = None if len(nextBets) == 0 else LegBet(move.camelNumber, nextBets[0])
            self.log(f"Bot {botIndex} has leg bets: " + ", ".join([f"{legBet.camelNumber} ({legBet.winCoins})" for legBet in self.botStates[botIndex].legBets]))
            return
        if type(move) is PlaceFinalBet:
            self.botStates[botIndex].nFinalBetsLeft -= 1
            self.botStates[botIndex].finalBetsLeft[move.camelNumber - 1] = False
            if move.isBetToWin:
                self.finalWinnerBets.append(FinalBet(move.camelNumber, botIndex))
            else:
                self.finalLoserBets.append(FinalBet(move.camelNumber, botIndex))
            self.log(f"Bot {botIndex} placed final bet on camel {move.camelNumber} to {'win' if move.isBetToWin else 'lose'}")

    def processWin(self, camelsWinning: list[int]) -> None:
        camelPositions = self.processLeg(pastBots=camelsWinning)
        correctIdx = 0
        self.log(f"Winning camel: {camelsWinning[0]+1}, winning bets: {', '.join([str(bet.botIndex)+':'+str(bet.camelNumber) for bet in self.finalWinnerBets])}")
        for bet in self.finalWinnerBets:
            if bet.camelNumber-1 == camelsWinning[0]:
                self.log(f"Bot {bet.botIndex} wins {finalBetScores[correctIdx]} coins")
                self.botStates[bet.botIndex].balance += finalBetScores[-1] if correctIdx >= len(finalBetScores) else finalBetScores[correctIdx]
                correctIdx += 1
            else:
                self.log(f"Bot {bet.botIndex} loses 1 coin")
                self.botStates[bet.botIndex].balance -= 1
        correctIdx = 0
        self.log(f"Losing camel: {camelPositions[-1]+1}, losing bets: {', '.join([str(bet.botIndex)+':'+str(bet.camelNumber) for bet in self.finalLoserBets])}")
        for bet in self.finalLoserBets:
            if bet.camelNumber-1 == camelPositions[-1]:
                self.log(f"Bot {bet.botIndex} wins {finalBetScores[correctIdx]} coins")
                self.botStates[bet.botIndex].balance += finalBetScores[-1] if correctIdx >= len(finalBetScores) else finalBetScores[correctIdx]
                correctIdx += 1
            else:
                self.log(f"Bot {bet.botIndex} loses 1 coin")
                self.botStates[bet.botIndex].balance -= 1
        self.gameRunning = False
        self.log("Final scores: " + ", ".join([f"{i}: {bot.balance}" for i, bot in enumerate(self.botStates)]))

    def processLeg(self, pastBots=[]) -> None:
        camelPositions = pastBots + [idx for i in range(16-1, -1, -1) if type(self.board[i]) == CamelPile for idx in self.board[i].camels if idx not in pastBots]
        self.availableLegBets = [LegBet(i+1, legBetScores[0]) for i in range(5)]
        self.log(f"Leg finished, camel positions: {[c+1 for c in camelPositions]}")
        for idx,bot in enumerate(self.botStates):
            self.log(f"Bot {idx} has {bot.balance} coins, ", end="")
            bot.balance += bot.nDiceRolls
            self.log(f"+ {bot.nDiceRolls} from dice rolls, ", end="")
            bot.nDiceRolls = 0
            for legBet in bot.legBets:
                if legBet.camelNumber-1 == camelPositions[0]:
                    bot.balance += legBet.winCoins
                    self.log(f"+ {legBet.winCoins} from leg bet on {legBet.camelNumber}, ", end="")
                elif legBet.camelNumber-1 == camelPositions[1]:
                    bot.balance += 1
                    self.log(f"+ 1 from leg bet on {legBet.camelNumber}, ", end="")
                else:
                    bot.balance -= 1
                    self.log(f"- 1 from leg bet on {legBet.camelNumber}, ", end="")
            self.log(f"total: {bot.balance}")
            bot.legBets = []
        self.diceRollsDone = [0 for i in range(5)]
        for i in range(16):
            if type(self.board[i]) == PlusMinusOne:
                self.board[i] = None
        return camelPositions
    
    def printBoard(self):
        if not self.gameRunning:
            return
        for i in range(5):
            line = " ".join([str(self.board[j].camels[-5+i]+1) if type(self.board[j]) == CamelPile and len(self.board[j].camels) > 4-i else ("-+"[int(self.board[j].isPlusOne)] if type(self.board[j]) == PlusMinusOne and i==4 else " ") for j in range(16)])
            self.log(line)

    def sanitizeMove(self, move: Move) -> Move:
        move2 = copy.deepcopy(move)
        if type(move) is PlaceFinalBet:
            move2.camelNumber = 0
        return move2

    def moveCamels(self, camelIndex: int, nTiles: int) -> None:
        camelsToMove = []
        camelsMoveIdx = -1
        for i in range(16):
            if type(self.board[i]) == CamelPile and camelIndex in self.board[i].camels:
                camelIdxInPile = self.board[i].camels.index(camelIndex)
                camelsToMove = self.board[i].camels[:camelIdxInPile+1]
                if camelIdxInPile == len(self.board[i].camels) - 1:
                    self.board[i] = None
                else:
                    self.board[i].camels = self.board[i].camels[camelIdxInPile+1:]
                camelsMoveIdx = i + nTiles
                break
        assert camelsMoveIdx != -1
        addTop = True
        if camelsMoveIdx >= 16:
            self.processWin(camelsToMove)
            return
        if type(self.board[camelsMoveIdx]) == PlusMinusOne:
            self.botStates[self.board[camelsMoveIdx].botIndex].balance += 1
            addTop = addTop if self.board[camelsMoveIdx].isPlusOne == None else False
            self.log(f"Bot {self.board[camelsMoveIdx].botIndex} wins 1 coin from +1/-1")
            camelsMoveIdx += 1 if self.board[camelsMoveIdx].isPlusOne else -1
        if camelsMoveIdx >= 16:
            self.processWin(camelsToMove)
            return
        if self.board[camelsMoveIdx] == None:
            self.board[camelsMoveIdx] = CamelPile(camelsToMove)
        else:
            if addTop:
                self.board[camelsMoveIdx].camels = camelsToMove + self.board[camelsMoveIdx].camels
            else:
                self.board[camelsMoveIdx].camels += camelsToMove

    def __repr__(self):
        return f"Game(\n  bots={self.bots},\n  availableLegBets={self.availableLegBets},\n  board={self.board},\n  botStates={self.botStates},\n  diceRollsDone={self.diceRollsDone},\n  finalWinnerBets={self.finalWinnerBets},\n  finalLoserBets={self.finalLoserBets}\n)"

def runOneGame():
    game = Game()
    game.run()

from rich.progress import track

def scoreBots():
    scores = {}
    for i in track(range(numberGames)):
        game = Game(logger=lambda s,*args,**kwargs: None)
        game.run()
        for j,bot in enumerate(game.bots):
            if bot.__class__ not in scores:
                scores[bot.__class__] = 0
            scores[bot.__class__] += game.botStates[j].balance
    print(scores)

if __name__ == "__main__":
    scoreBots()
    # runOneGame()