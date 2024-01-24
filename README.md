# Navmesh-Pathfinding

Teammates: Harsh and Cromwell De Guzman

Modifications done to the MCTS_modified:

The modified Monte Carlo Tree Search (MCTS) algorithm introduces key changes to the original implementation. 
The primary modification is the incorporation of a new rollout strategy named testaction. In the updated rollout function, this strategy involves recursively selecting actions until the game concludes or a predefined depth of 19 is reached, with the depth used to evaluate the outcome. 
Additionally, an exploration factor of 0.8 is introduced, determining whether to choose a random action or utilize the testaction strategy during the rollout phase. The modified algorithm aims to enhance the exploration-exploitation trade-off during simulations. Moreover, a redundant random action selection line within the rollout function has been identified. Overall, these changes in the rollout strategy and exploration factor contribute to an adjusted decision-making process, potentially impacting the performance of the MCTS algorithm in game scenarios.