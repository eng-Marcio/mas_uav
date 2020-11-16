# -*- coding: utf-8 -*-
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
#global action
L = 'L'
R = 'R'
N = 'N'
S = 'S'
class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).
    """
    def __init__(self, map):
        from Mapping_System import Mapping_System
        self.map_System = map

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        return self.map_System.cur_pos

    def EqualState(self, state1, state2):
        return (state1[0] == state2[0]) and (state1[1] == state2[1])

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        return self.EqualState(state, self.map_System.goal)

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        successors = []
        x, y = state  #split state coordinates
        #check Left
        if(self.space9free(x-1, y)):
            successors.append([[x-1, y], L, 1])
        #check Right
        if(self.space9free(x+1, y)):
            successors.append([[x+1, y], R, 1])
        #check North
        if(self.space9free(x, y+1)):
            successors.append([[x, y+1], N, 1])
        #check South
        if(self.space9free(x, y-1)):
            successors.append([[x, y-1], S, 1])
        return successors

    def space9free(self, x, y): #return true if and only if all 9 grid spaces centered in x,y are free
        res = True
        res = res and self.map_System.map[x-1][y-1] == 0
        res = res and self.map_System.map[x][y-1] == 0
        res = res and self.map_System.map[x+1][y-1] == 0
        res = res and self.map_System.map[x-1][y] == 0
        res = res and self.map_System.map[x][y] == 0
        res = res and self.map_System.map[x+1][y] == 0
        res = res and self.map_System.map[x-1][y+1] == 0
        res = res and self.map_System.map[x][y+1] == 0
        res = res and self.map_System.map[x+1][y+1] == 0
        return res
        


    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        return len(actions) ##cost is simply the number of steps


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
    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    print("Start's successor 0 position:", problem.getSuccessors(problem.getStartState())[0][0])
    

    ## Estados: Posição do Pacman 
    ## Transições: Movimentos permitidos
    ## Euristica: aqui? nenhuma

    # Busca em profundidade, exploro um estado por vez e esgoto a possibilidade dele ser a solução,
    # ou seja, existe uma lista de estados "abertos", que podem ser solução, investigo se ele é, 
    # se não é, crio, com base no "investigado", novos estado e adiciono os "sucessores" a lista de "abertos"
    # OBS: Não permito abrir o mesmo estado duas vezes ## if abertos
    abertos = problem.getSuccessors(problem.getStartState())
    for investigado in abertos:
        print("agora aberto: ", investigado)
        if problem.isGoalState(investigado[0]):
            print("chegou a solucao! ")
            return 
        sucessores = problem.getSuccessors(investigado[0])
        print("sucessores no for: ", sucessores)
        #abertos.extend(sucessores) condicional:
        for sucessor in sucessores: # coloca os "sucessores" na lista de "abertos" se eles já não estão
            if (sucessor in abertos):
                print("houve poda")
            else: 
                abertos.append(sucessor)
        # fim do .extend(sucessores)

                


    util.raiseNotDefined()

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
    print("A sequencia de movimentos encontrada foi: ", current_state.action_list)
    return current_state.action_list
    
class Node:
    "Inspirado no AstarNode, só que sem a parte da heuristica"
    def __init__(self, problem, state, action_list, path_cost=0):
        self.state = state
        self.action_list= action_list
        self.path_cost = path_cost


def uniformCostSearch(problem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

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
        self.acc_cost = acc_cost + step_cost
        self.heuristic_cost = self.acc_cost + heuristic(state, problem)

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
        if insertion_index <= -1 and unseen_state.heuristic_cost >= to_insert.heuristic_cost:
            insertion_index = array.index(unseen_state)
        if unseen_state.state == to_insert.state:
            if insertion_index > -1:
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
    
    "python3 pacman.py -l openMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic"
    "python3 pacman.py -l openMaze -z .5 -p SearchAgent -a fn=astar,heuristic=euclideanHeuristic"
    "python3 pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=manhattanHeuristic"
    "python3 pacman.py -l bigMaze -z .5 -p SearchAgent -a fn=astar,heuristic=euclideanHeuristic"

    current_state = AstarNode(problem, problem.getStartState(), [], 0, 0, heuristic)
    unvisited_states = [current_state]
    visited_states = []
    while not problem.isGoalState(current_state.state):
        unvisited_states.remove(current_state)
        visited_states.append(current_state.state)
        next_states = problem.getSuccessors(current_state.state)
        for triplet in next_states:
            state, action, action_cost = triplet
            if state in visited_states:
                continue
            new_state = AstarNode(problem, state, \
                current_state.action_list + [action],\
                    current_state.acc_cost, action_cost, heuristic)
            _heuristicInsert(unvisited_states, new_state)
        if unvisited_states == []:
            return []
        current_state = unvisited_states[0]
    return current_state.action_list
        
    util.raiseNotDefined()


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch

