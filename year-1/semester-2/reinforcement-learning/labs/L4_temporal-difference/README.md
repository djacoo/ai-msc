# Lab 4 — Temporal Difference Methods

Reinforcement Learning lab (MSc Artificial Intelligence). Pure NumPy implementation of the
two classic **Temporal Difference (TD) control** algorithms — **Q-Learning** and **SARSA** —
on the `DangerousGridWorld` environment.

## Topic & Theory Recap

Temporal Difference methods learn online, **step by step**, without waiting for the end of an
episode (unlike Monte Carlo). They **bootstrap**: the value estimate is updated towards a
target that itself uses a current estimate. The general TD(0) control update is:

```
Q(s,a) <- Q(s,a) + alpha * ( TD_target - Q(s,a) )
```

The two algorithms differ only in the TD target:

- **Q-Learning (off-policy)** uses the value of the *greedy* next action:
  ```
  TD_target = r + gamma * max_a' Q(s', a')
  ```
  It learns the optimal action-value function while behaving with an exploratory policy.

- **SARSA (on-policy)** uses the value of the action *actually taken next* under the
  behaviour policy (State-Action-Reward-State-Action):
  ```
  TD_target = r + gamma * Q(s', a')   with a' chosen epsilon-greedily
  ```
  It learns the value of the policy it is following, so it tends to prefer safer paths.

Both use an **epsilon-greedy** behaviour policy (`epsilon_greedy`): with probability `eps`
pick a random action, otherwise the current best. `alpha` is the learning rate, `gamma` the
discount factor.

The grid has a `[S]`tart (state 0), a `[G]`oal (state 48, reward +5), `[W]`alls, and `[X]`
death cells (reward -1); every other step costs -0.1. Transitions are stochastic (intended
action succeeds with probability 0.9). Both algorithms learn to follow the safe right-hand
column down to the goal, avoiding the death cells.

## Files

- `lessons/lesson_4_code.py` — `epsilon_greedy`, `q_learning`, `sarsa`, and `main()` driver.
- `tools/DangerousGridWorld.py` — environment (do not modify).
- `results/lesson_4_results.txt` — saved console output of a successful run.

## How to Run

From the `lessons/` directory (so `from DangerousGridWorld import GridWorld` resolves):

```bash
cd lessons
python lesson_4_code.py
```

Hyperparameters (in `main`): `episodes=500`, `alpha=0.3`, `gamma=0.9`, `epsilon=0.1`.
Requirements: `numpy<2`, `gym` (matplotlib not needed for this lab).

## Expected Results

Both algorithms recover a correct policy that routes through the safe column to the goal.
The printed reward/steps are **averages over the 500 training episodes** (which include
early exploratory episodes), so they are lower than a fully-converged policy and vary
between runs. Representative output:

```
4) Q-Learning
	Expected reward training with Q-Learning: ~1.8 - 2.3
	Average steps training with Q-Learning:   ~12 - 21

5) SARSA
	Expected reward training with SARSA: ~2.1 - 2.7
	Average steps training with SARSA:   ~11 - 21
```
