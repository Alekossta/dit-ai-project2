# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newGhostPositions = successorGameState.getGhostPositions()
        newPacmanPosition = successorGameState.getPacmanPosition()

        # find minimum distance from pacman to a ghost.
        distancesFromPlayerToGhosts = []
        for ghostPosition in newGhostPositions:
            newDistance = manhattanDistance(newPacmanPosition, ghostPosition)
            distancesFromPlayerToGhosts.append(newDistance)

        minDistanceFromPlayerToGhosts = min(distancesFromPlayerToGhosts, default=0)

        # find minimum distance from pacman to a food.
        distancesFromPlayerToFoods = []
        foodPositions = successorGameState.getFood().asList()
        for foodPosition in foodPositions:
            newDistance = manhattanDistance(newPacmanPosition, foodPosition)
            distancesFromPlayerToFoods.append(newDistance)

        minDistanceFromPlayerToFoods = min(distancesFromPlayerToFoods, default=0)

        # find minimum distance from pacman to all capsules
        distancesFromPlayerToCapsules = []
        capsulePositions = successorGameState.getCapsules()
        for capsulePosition in capsulePositions:
            newDistance = manhattanDistance(newPacmanPosition, capsulePosition)
            distancesFromPlayerToCapsules.append(newDistance)

        minDistanceFromPlayerToCapsules = min(distancesFromPlayerToCapsules, default=0)


        # find difference in scores
        oldScore = currentGameState.getScore()
        newScore = successorGameState.getScore()
        scoreDifference = newScore - oldScore

        # find smallest scare time and determine if we have any scared ghosts. in this case
        # the closer the ghost the better.
        newGhostStates = successorGameState.getGhostStates()
        scaredTimers = []
        for ghostState in newGhostStates:
            scaredTimers.append(ghostState.scaredTimer)
        smallestScareTime = min(scaredTimers, default=0) # set 1 because we dont want to divide by 0        
        if(smallestScareTime != 0):
            minDistanceFromPlayerToGhosts = -minDistanceFromPlayerToGhosts


        newNumberOfFoods = successorGameState.getNumFood()

        stopPenalty = 0
        if(action=="Stop"):
            stopPenalty = -10
        
        # some weights for each factor
        distanceFromFoodWeight = 0.3
        distanceFromGhostWeight = 0.02
        numberOfFoodsWeights = 0.2
        scoreDifferenceWeight = 0.3
        capsuleWeight = 10

        distanceFromFoodsFactor = (1/(minDistanceFromPlayerToFoods+1)) * distanceFromFoodWeight
        distanceFromGhostsFactor = minDistanceFromPlayerToGhosts * distanceFromGhostWeight
        distanceFromCapsulesFactor = (1/ (minDistanceFromPlayerToCapsules+1)) * capsuleWeight
        numberOfFoodsFactor = newNumberOfFoods * numberOfFoodsWeights
        scoreFactor = scoreDifference * scoreDifferenceWeight


        return (
        distanceFromFoodsFactor
        + distanceFromGhostsFactor
        + distanceFromCapsulesFactor
        + numberOfFoodsFactor
        + scoreFactor
        + stopPenalty
        )

      

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        def minMax(gameState:GameState, agentIndex, depth=0):
            # check if we have a terminal state
            if(gameState.isWin() or gameState.isLose() or depth == self.depth):
                return self.evaluationFunction(gameState), None
            
            # handle the indexes

            # in case we reach the final agent, reset the index and add depth
            # else just move to the next agent
            newAgentIndex = agentIndex
            newDepth = depth
            if(agentIndex == (gameState.getNumAgents() - 1)):
                newAgentIndex = 0
                newDepth = depth + 1
            else:
                newAgentIndex = agentIndex + 1
            
            
            # if agent is player
            if agentIndex == 0:
                maxValue = -float('inf')
                maxBestAction = None
                legalActions = gameState.getLegalActions(agentIndex)
                for legalAction in legalActions:
                    succesorGameState = gameState.generateSuccessor(agentIndex,legalAction)
                    successorMaxValue, succesorMinAction = minMax(succesorGameState, newAgentIndex, newDepth)
                    if(successorMaxValue > maxValue):
                        maxValue = successorMaxValue
                        maxBestAction = legalAction
                
                return maxValue, maxBestAction
            else: # agent is a ghost
                minValue = float('inf')
                minBestAction = None
                legalActions = gameState.getLegalActions(agentIndex)
                for legalAction in legalActions:
                    succesorGameState = gameState.generateSuccessor(agentIndex,legalAction)
                    succesorMinValue, succesorMinAction = minMax(succesorGameState, newAgentIndex, newDepth)
                    if(succesorMinValue < minValue):
                        minValue = succesorMinValue
                        minBestAction = legalAction

                return minValue, minBestAction
            
        value, action = minMax(gameState, 0, 0)
        return action    

class AlphaBetaAgent(MultiAgentSearchAgent):
    def getAction(self, gameState):
        def alphaBetaPruning(gameState:GameState, agentIndex, alpha, beta, depth=0):
            # check if we have a terminal state
            if(gameState.isWin() or gameState.isLose() or depth == self.depth):
                return self.evaluationFunction(gameState), None
            
            # handle the indexes

            # in case we reach the final agent, reset the index and add depth
            # else just move to the next agent
            newAgentIndex = agentIndex
            newDepth = depth
            if(agentIndex == (gameState.getNumAgents() - 1)):
                newAgentIndex = 0
                newDepth = depth + 1
            else:
                newAgentIndex = agentIndex + 1
            
            
            # if agent is player
            if agentIndex == 0:
                maxValue = -float('inf')
                maxBestAction = None
                legalActions = gameState.getLegalActions(agentIndex)
                for legalAction in legalActions:
                    succesorGameState = gameState.generateSuccessor(agentIndex,legalAction)
                    successorMaxValue, succesorMinAction = alphaBetaPruning(succesorGameState, newAgentIndex, alpha, beta, newDepth)
                    if(successorMaxValue > maxValue):
                        maxValue = successorMaxValue
                        maxBestAction = legalAction

                    if(successorMaxValue > beta):
                        break
                    alpha = max(alpha, successorMaxValue)

                return maxValue, maxBestAction
            else: # agent is a ghost
                minValue = float('inf')
                minBestAction = None
                legalActions = gameState.getLegalActions(agentIndex)
                for legalAction in legalActions:
                    succesorGameState = gameState.generateSuccessor(agentIndex,legalAction)
                    succesorMinValue, succesorMinAction = alphaBetaPruning(succesorGameState, newAgentIndex, alpha, beta, newDepth)
                    if(succesorMinValue < minValue):
                        minValue = succesorMinValue
                        minBestAction = legalAction

                    if minValue < alpha:
                        break
                    beta = min(beta, succesorMinValue)

                return minValue, minBestAction
            
        value, action = alphaBetaPruning(gameState, 0, -float("inf"), float("inf"), 0)
        return action   

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
