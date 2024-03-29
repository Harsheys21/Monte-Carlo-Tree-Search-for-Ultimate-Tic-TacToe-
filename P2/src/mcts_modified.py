
from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
import random
from math import sqrt, log

num_nodes = 750
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverses the tree until the end criterion are met.
    e.g. find the best expandable node (node with untried action) if it exist,
    or else a terminal node

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 1 or 2

    Returns:
        node: A node from which the next stage of the search can proceed.
        state: The state associated with that node

    """
    while len(node.child_nodes) > 0 and len(node.untried_actions) == 0 and board.is_ended(state) == False:
        # finds out if last action was committed by opponent
        is_opponent = True
        if board.current_player(state) == bot_identity:
            is_opponent = False
        
        child_nodes_values = node.child_nodes.values()
        best_node = None
        best_ucb_value = float('-inf')  # Initialize to negative infinity

        for child_node in child_nodes_values:
            current_ucb_value = ucb(child_node, is_opponent)
            if current_ucb_value >= best_ucb_value:
                best_node = child_node
                best_ucb_value = current_ucb_value

        node = best_node

        state = board.next_state(state, node.parent_action)
    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node (if it is non-terminal).

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:
        node: The added child node
        state: The state associated with that node

    """
    if len(node.untried_actions) > 0:
        action = node.untried_actions.pop(0)
        state = board.next_state(state, action) 
        n = MCTSNode(parent=node,parent_action=action, action_list=board.legal_actions(state))
        node.child_nodes[action] = n
    
    return node, state

# rollout (board, state)
# simulate the remainder of the game by making random moves until the game is over
def testaction(board, state, action, depth, bot_identity):
    test_state = board.next_state(state, action)

    if board.is_ended(test_state) or depth > 19:
        if board.is_ended(test_state) and is_win(board,test_state,bot_identity):
            return depth * -1
        else:
            return depth

    selected_action = choice(board.legal_actions(test_state))

    return testaction(board, test_state, selected_action, depth + 1, bot_identity)

def rollout(board: Board, state, bot_identity: int):
    """ Modified rollout function using improved_rollout with additional parameters.

    Args:
        board:  The game setup.
        state:  The state of the game.

    Returns:
        state: The terminal game state.

    """

    exploration_factor = 0.8

    while board.is_ended(state) == False:  
        # pull all legal actions
        actions = board.legal_actions(state)

        if len(actions) == 0:
            break
        
        for action in actions:
            next_state = board.next_state(state,action)
            if board.is_ended(next_state):
                return next_state  

        if random.random() < exploration_factor:
            selected_action = choice(actions)
            state = board.next_state(state, selected_action)
        else:
            selected_action = min(actions, key=lambda n: testaction(board, state, n, 0, bot_identity))
            state = board.next_state(state, selected_action)
        
        # continue the loop until the game is ended
        randomAction = choice(board.legal_actions(state))   # randomly select a move from legal moves
        state = board.next_state(state, randomAction)       # update the state accordingly

    # Return the terminal game state after the loop
    return state


# backpropagate(node, won)
# uses recursion to traverse from the leaf node to the root
# it updates the statistics of each node on the way
def backpropagate(node: MCTSNode|None, won: bool):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    if won == True:
        node.wins += 1                  # if the base case is false, update the wins
    node.visits += 1                    # and visits of the current node based on the outcome of the game

    if(node.parent is None):            # check if the current node has no parent
        return                          # if leaf node is reached, terminate the recursion

    backpropagate(node.parent, won)     # recursively call backpropagate() with the parent of the current node and the same won value

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calcualtes the UCB value for the given node from the perspective of the bot

    Args:
        node:   A node.
        is_opponent: A boolean indicating whether or not the last action was performed by the MCTS bot
    Returns:
        The value of the UCB function for the given node
    """
    # ucb formula is (child node wins / child node total visits) + (exploration factor)*(sqrt(ln(current node total visits)/child node total visits))
    if node.visits == 0:
        return float("inf")
    
    first_half = node.wins / node.visits
    v = log(node.parent.visits)
    second_half = explore_faction * sqrt(v / node.visits) 
    ucb_value = first_half + second_half

    if is_opponent == True:
        return 1 - ucb_value
    else:
        return ucb_value

def get_best_action(root_node: MCTSNode):
    """ Selects the best action from the root node in the MCTS tree

    Args:
        root_node:   The root node
    Returns:
        action: The best action from the root node
    
    """
    best_action = None
    best_win_rate = -1
    for key, child_node in root_node.child_nodes.items():
        if child_node.visits > 0:
            win_rate = child_node.wins/ child_node.visits
            if win_rate > best_win_rate:
                best_action = key
                best_win_rate = win_rate
    return best_action

def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        current_state:  The current state of the game.

    Returns:    The action to be taken from the current state

    """
    bot_identity = board.current_player(current_state) # 1 or 2
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Do MCTS - This is all you!
        # ...
        # traverse node to find best option
        leaf_node, state = traverse_nodes(node, board, state, bot_identity)

        # add node to tree
        expand_node, state = expand_leaf(leaf_node, board, state)
        
        # do simulation with the added node
        state = rollout(board, state, bot_identity)
        
        # find out if player/bot won or not
        w = is_win(board, state, bot_identity)

        # add information from simulation back into board
        backpropagate(expand_node, w)
    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action = get_best_action(root_node)
    print(f"Action chosen: {best_action}")
    return best_action
