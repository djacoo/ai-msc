# Lab 3 — Monte Carlo RL Methods

Reinforcement Learning lab (MSc Artificial Intelligence). Pure NumPy implementation of
**on-policy Monte Carlo control** on the `DangerousGridWorld` environment.

## Topic & Theory Recap

Monte Carlo (MC) methods learn directly from **complete episodes** of experience, without a
model of the environment. They estimate the action-value function `Q(s,a)` by averaging the
**returns** observed after visiting each state-action pair:

```
G_t = r_{t+1} + gamma * r_{t+2} + gamma^2 * r_{t+3} + ...   (discounted return)
Q(s,a) = average of returns G observed from (s,a)
```

Control alternates **policy evaluation** (estimating `Q` from sampled returns) with
**policy improvement** (making the policy greedier w.r.t. `Q`). To keep exploring all
state-action pairs we use one of two strategies:

- **Exploring starts**: every episode begins from a random state and a random first action,
  so each `(s,a)` pair has a non-zero chance of being the start.
- **Epsilon-soft policies**: the policy keeps every action with probability `>= eps/|A|`,
  taking the greedy action with probability `1 - eps + eps/|A|`.

This lab uses the **every-visit** MC variant (every occurrence of `(s,a)` in an episode
contributes a return), with incremental averaging of returns into `Q`.

The grid has a `[S]`tart (state 0), a `[G]`oal (state 48, reward +5), `[W]`alls,
and `[X]` death cells (reward -1); every other step costs -0.1. Transitions are stochastic
(intended action succeeds with probability 0.9). The optimal behaviour hugs the safe
right-hand column, away from the death cells, then heads down to the goal.

## Files

- `lessons/lesson_3_code.py` — implementations of `on_policy_mc_exploring_starts` and
  `on_policy_mc_epsilon_soft`, plus `main()` driver.
- `tools/DangerousGridWorld.py` — environment (do not modify).
- `results/lesson_3_results.txt` — saved console output of a successful run.

## How to Run

From the `lessons/` directory (so `from DangerousGridWorld import GridWorld` resolves):

```bash
cd lessons
python lesson_3_code.py
```

Requirements: `numpy<2`, `gym` (matplotlib not needed for this lab).

## Expected Results

Both MC variants converge to a good policy that follows the safe column down to the goal,
with an expected reward close to the optimum (~3.3). Exact numbers vary slightly between
runs because episodes are stochastic. Representative output:

```
3) MC On-Policy (with exploring starts)
	Expected reward following this policy: ~3.27

3) MC On-Policy (for epsilon-soft policies)
	Expected reward following this policy: ~3.15
```
