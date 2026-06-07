# Lab 2 — MDPs and Gym Environments

## Topic & theory recap
A **Markov Decision Process (MDP)** formalises sequential decision making with states,
actions, a transition model `P(s' | s, a)`, and a reward function `R`. This lab has two
hands-on parts that build intuition for environments and the Markov property *before*
introducing any learning algorithm:

1. **Random policy on the Dangerous Grid World.** A 7×7 grid with a start cell `[S]`,
   a goal `[G]`, walls `[W]` (impassable) and death cells `[X]` (terminal, negative
   reward). Transitions are **stochastic**: the chosen move succeeds with probability
   `0.9`, otherwise it slips to another neighbour. We roll out a **uniform random policy**
   and collect the visited trajectory, stopping if a terminal cell is reached.

2. **Recycling Robot** (Sutton & Barto, Example 3.3). A custom MDP with two energy
   states `{HIGH, LOW}` and three actions `{SEARCH, WAIT, RECHARGE}`:
   - `SEARCH` — high expected reward (`r_search = 0.5`) but drains the battery: from
     `HIGH` stays `HIGH` w.p. `α = 0.7` else drops to `LOW`; from `LOW` stays `LOW`
     w.p. `β = 0.7`, otherwise the battery depletes, the robot is rescued
     (reward `-3`) and reset to `HIGH`.
   - `WAIT` — lower reward (`r_wait = 0.2`), energy level unchanged.
   - `RECHARGE` — no cans collected (reward `0`), battery returns to `HIGH`.

## Files
- `lessons/lesson_2_code.py` — implementation: `random_dangerous_grid_world`
  (random rollout on the grid) and the `RecyclingRobot` environment
  (`__init__`, `reset`, `step`, `render`).
- `tools/DangerousGridWorld.py` — provided grid-world environment (do not edit).
- `results/lesson_2_results.txt` — console output of a successful run.
- `slides/slides_lesson_2.pdf` — lecture slides.

## How to run
From the `lessons/` directory (so the relative `../tools` import resolves):

```bash
cd lessons
python lesson_2_code.py
```

Requirements: `numpy<2`, `gym`. (A deprecation warning from `gym` about NumPy 2.0 is
harmless and does not affect the run.)

## Expected results
- **Part A** prints the rendered grid and a random trajectory as a list of
  `(state, action)` pairs starting from state `0`. Because moves are stochastic and the
  policy is random, the path wanders and may revisit cells; it terminates early only if
  it stumbles onto a death or goal cell. Each run differs (no fixed seed).
- **Part B** runs 10 random steps of the Recycling Robot and prints the action taken and
  the cumulative reward. Observe the dynamics: `SEARCH` yields `+0.5` (or `-3` on a rare
  `LOW` depletion), `WAIT` yields `+0.2`, `RECHARGE` yields `0` and forces the state back
  to `HIGH`. This confirms the transition/reward table of Example 3.3.
