# Lab 1 — Multi-Armed Bandit (10-armed Testbed)

## Topic & theory recap
The **multi-armed bandit** is the simplest reinforcement-learning setting: a single
state, `k` actions ("levers"), and a stochastic reward for each. Each lever `a` has an
unknown true value `q*(a)` (here drawn once from `N(0, 1)`); pulling it returns a reward
`~ N(q*(a), 1)`. The agent does not know `q*` and must learn it by trial and error.

This lab reproduces Sutton & Barto's **10-armed testbed** and studies the
**exploration vs. exploitation** trade-off via an **ε-greedy** policy:

- with probability `ε` pick a **random** lever (explore);
- otherwise pick `argmax(Q)` (exploit the current best estimate).

Value estimates are updated with the **incremental sample-average** rule:

```
N(a) <- N(a) + 1
Q(a) <- Q(a) + (1 / N(a)) * (reward - Q(a))
```

which maintains the running mean of the rewards seen for each action without storing them.

## Files
- `lessons/lesson_1_code.py` — implementation: `MultiArmedBandit` environment
  (`__init__`, `action`) and the `banditAlgorithm` (ε-greedy + incremental update).
- `results/lesson_1_results.txt` — console output of a successful run.
- `results/average_reward_vs_steps.png` — average-reward-vs-steps learning curve
  (averaged over 500 independent runs for `ε = 0, 0.01, 0.1`).
- `slides/slides_lesson_1.pdf` — lecture slides.

## How to run
From the `lessons/` directory (so the relative `../tools` path resolves):

```bash
cd lessons
python lesson_1_code.py
```

Requirements: `numpy<2`, `matplotlib`. Plotting is headless (`Agg` backend); the figure
is written to `results/average_reward_vs_steps.png`.

## Expected results
- **ε = 0 (pure greedy)** gets stuck on whatever action it tried first that looked good;
  it often never finds the optimal lever, so its average reward plateaus low (~0.7–1.0).
- **ε = 0.01** explores rarely but eventually identifies the best lever; it is slow to
  rise but reaches a high asymptote.
- **ε = 0.1** explores more, learns the best action fastest, and gives the highest
  average reward over 1000 steps (~1.4), at the cost of occasionally pulling a sub-optimal
  lever forever (the 10% exploration tax).

A representative single-run summary (seed `6`):

```
Last episodes reward (eps=0   ): ~0.74
Last episodes reward (eps=0.01): ~0.97
Last episodes reward (eps=0.1 ): ~1.39
Real optimal action: 8   |   found: 1 (eps=0), 8 (eps=0.01), 8 (eps=0.1)
```

Note that greedy (`eps=0`) fails to recover the true optimal action `8`, while both
exploring agents do — the headline lesson of the chapter.
