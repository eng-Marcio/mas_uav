# search.py
# ---------
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


"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()


def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"

    "Pra rodar isso:"
    "python pacman.py -l tinyMaze -p SearchAgent"
    "python pacman.py -l mediumMaze -p SearchAgent" 
    "python pacman.py -l bigMaze -z .5 -p SearchAgent"

    # print("Start:", problem.getStartState())
    # "Start: (5, 5)"
    # print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    # "Is the start a goal? False"
    # print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    # "Start's successors: [((5, 4), 'South', 1), ((4, 5), 'West', 1)]"
    # print("Start's successor 0 position:", problem.getSuccessors(problem.getStartState())[0][0])
    # "Start's successor 0 position: (5, 4)"

    ## Estados: Posição do Pacman 
    ## Transições: Movimentos permitidos
    ## Euristica: aqui? nenhuma

    current_state = Node(problem, problem.getStartState(), [])
    unvisited_states = [current_state]
    visited_states = []
    while not problem.isGoalState(current_state.state):
        # print("investigando estado ", current_state.state)
        for new_state in problem.getSuccessors(current_state.state):
            state, action, action_cost = new_state
            if state not in visited_states: # poda de estados já visitados
                new_node = Node(problem, state, current_state.action_list + [action])
                unvisited_states.append(new_node)
        unvisited_states.remove(current_state)
        if unvisited_states is []:
            print("Objetivo não alcançado")
            return False
        visited_states.append(current_state.state)
        current_state = unvisited_states[-1] # Right-most depth first (FILO)
    # print("A sequencia de movimentos encontrada foi: ", current_state.action_list)
    return current_state.action_list

    #util.raiseNotDefined()

def breadthFirstSearch(problem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"

    "Pra rodar isso:"

    "python pacman.py -l mediumMaze -p SearchAgent -a fn=bfs"
    "python pacman.py -l bigMaze -p SearchAgent -a fn=bfs -z .5"
    
    current_state = Node(problem, problem.getStartState(), [])
    unvisited_states = [current_state]
    visited_states = []
    while not problem.isGoalState(current_state.state):
        # print("investigando estado ", current_state.state)
        for new_state in problem.getSuccessors(current_state.state):
            state, action, action_cost = new_state
            if state not in visited_states: # poda de estados já visitados (pro Astar não é pertinente)
                new_node = Node(problem, state, current_state.action_list + [action])
                unvisited_states.append(new_node) # (critico pro Astar)
        unvisited_states.remove(current_state)
        if unvisited_states is []:
            print("Objetivo não alcançado")
            return False
        visited_states.append(current_state.state)
        current_state = unvisited_states[0] # FIFO
    # print("A sequencia de movimentos encontrada foi: ", current_state.action_list)
    return current_state.action_list
    
class Node:
    "Inspirado no AstarNode, só que sem a parte da heuristica"
    def __init__(self, problem, state, action_list, path_cost=0, expected_cost=0):
        self.state = state
        self.action_list= action_list
        self.path_cost = path_cost
        self.expected_cost = expected_cost

def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"

    "Pra rodar isso:"

    "python pacman.py -l mediumMaze -p SearchAgent -a fn=ucs"
    "python pacman.py -l mediumDottedMaze -p StayEastSearchAgent"
    "python pacman.py -l mediumScaryMaze -p StayWestSearchAgent"

    current_state = Node(problem, problem.getStartState(), [])
    unvisited_states = [current_state]
    visited_states = []
    while not problem.isGoalState(current_state.state):
        # print("investigando estado ", current_state.state)
        for new_state in problem.getSuccessors(current_state.state):
            state, action, action_cost = new_state
            if state not in visited_states: # poda de estados já visitados (pro Astar não é pertinente)
                new_node = Node(problem, state, current_state.action_list + [action], current_state.path_cost + action_cost)
                unvisited_states.append(new_node) # (critico pro Astar)
        unvisited_states.remove(current_state)
        if unvisited_states is []:
            print("Objetivo não alcançado")
            return False
        visited_states.append(current_state.state)
        current_state = sorted(unvisited_states, key=lambda unvisited_state: unvisited_state.path_cost)[0] # porran, até eu to impressionado com a elegancia que eu encontrei
        # ordena a lista 'unvisited_states' com base na propriedade 'path_cost'
        # extremamente elegante, extremamente ineficiente
    # print("A sequencia de movimentos encontrada foi: ", current_state.action_list)
    return current_state.action_list


def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0
class AstarNode:
    """
    Esta classe serve meramente para armazenar as informações relevantes para a 
    execução das funções aStarSearch e _heuristicInsert e não deve ser usada fora
    destas funções.
    """
    def __init__(self, problem, state, action_list, acc_cost, step_cost, heuristic):
        self.state = state
        self.action_list = action_list
        self.acc_cost = acc_cost + step_cost + heuristic(state)

def _heuristicInsert(array, to_insert):
    """
    Esta funcão encapsula a inserção de um estado na lista de estados não visitados
    ordenando-o de acordo com o custo acumulado (+ a heurística, que está encapsulada
    na classe AstarNode) e não deve ser usada fora da função aStarSearch. Após a in-
    serção do novo estado, caso este estado já estivesse na lista com um custo maior,
    as instâncias com custo maior são removidas
    """
    if array == []:
        array.append(to_insert)
        return
    insertion_index = -1
    for unseen_state in array:
        if insertion_index <= -1 and unseen_state.acc_cost > to_insert.acc_cost:
            insertion_index = array.index(unseen_state)
        if unseen_state.state == to_insert.state:
            if unseen_state.acc_cost > to_insert.acc_cost:
                array.remove(unseen_state)
            else:
                return
    if insertion_index == -1:
        array.append(to_insert)
    else:
        array.insert(insertion_index, to_insert)
     
def aStarSearch(problem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"

    "Roda com:"
    
    "python pacman.py -l openMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic"
    "python pacman.py -l openMaze -z .5 -p SearchAgent -a fn=astar,heuristic=euclideanHeuristic"
    "python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic"
    "python pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=euclideanHeuristic"

    current_state = Node(problem, problem.getStartState(), [])
    unvisited_states = [current_state]
<<<<<<< HEAD
    while not problem.isGoalState(current_state.state):
        for triplet in problem.getSuccessors(current_state.state):
            state, action, action_cost = triplet
            new_state = AstarNode(problem, state, \
                current_state.action_list + [action],\
                    current_state.acc_cost, action_cost, heuristic)
            _heuristicInsert(unvisited_states, new_state)
        unvisited_states.remove(current_state)
        current_state = unvisited_states[0]
        if unvisited_states == []:
            print("fuck")
            return []
=======
    visited_states = []
    while not problem.isGoalState(current_state.state):
        # print("investigando estado ", current_state.state)
        for new_state in problem.getSuccessors(current_state.state):
            state, action, action_cost = new_state
            if state not in visited_states: # poda de estados já visitados (pro Astar não é pertinente)
                new_node = Node(problem, state, current_state.action_list + [action], current_state.path_cost + action_cost, heuristic(state, problem) )
                unvisited_states.append(new_node) # (critico pro Astar)
        unvisited_states.remove(current_state)
        if unvisited_states is []:
            print("Objetivo não alcançado")
            return False
        visited_states.append(current_state.state)
        current_state = sorted(unvisited_states, key=lambda unvisited_state: (unvisited_state.expected_cost))[0] 
        # ordena a lista 'unvisited_states' com base na propriedade 'path_cost'
<<<<<<< HEAD
        # extremamente elegante, extremamente ineficiente por causa de 'sort'
    #print("A sequencia de movimentos encontrada foi: ", current_state.action_list)
=======
        # extremamente elegante, extremamente ineficiente
    print("A sequencia de movimentos encontrada foi: ", current_state.action_list)
>>>>>>> f6dba8ed1ede954c923365cb09cb566e6825bb6a
>>>>>>> 67161847271e72a0a9ff89bffdef6296942a2376
    return current_state.action_list
    util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
