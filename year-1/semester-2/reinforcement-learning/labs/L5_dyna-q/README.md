# Lab 5 — Dyna-Q and Dyna-Q+

## Topic & Theory Recap
**Dyna-Q** is an integrated planning–acting–learning architecture. Each real
interaction with the environment is used twice:

1. **Direct RL** — a standard tabular Q-learning update from the *real*
   transition `(s, a, r, s')`:
   `Q(s,a) += α · [ r + γ·maxₐ' Q(s',a') − Q(s,a) ]`.
2. **Model learning** — the observed transition is stored in a deterministic
   model `M(s,a) → (r, s')`.
3. **Planning** — `n` simulated updates per real step, each sampling a
   previously visited `(s,a)` pair from the model and applying the same
   Q-learning update on the *imagined* transition. Larger `n` propagates reward
   information faster, so fewer real steps are needed to find a good policy.

Behaviour is **ε-greedy** to keep exploring.

**Dyna-Q+** adds an *exploration bonus* to planning targets:
`r + κ·√τ(s,a)`, where `τ(s,a)` is the number of steps since `(s,a)` was last
tried. This rewards revisiting long-unused transitions, making the agent robust
to non-stationary environments. Untried actions of visited states are seeded as
zero-reward self-loops so planning can also "discover" them.

Environment: **DangerousGridWorld**, a 7×7 grid (49 states, actions L/R/U/D)
with walls, deadly cells (`R=-1`), a step cost (`R=-0.1`) and a goal (`R=+5`).

## Files
- `lessons/lesson_5_code.py` — Dyna-Q / Dyna-Q+ implementation and `main()`.
- `tools/DangerousGridWorld.py` — environment (do not modify).
- `results/lesson_5_results.txt` — saved console output of a successful run.
- `results/dyna_q_cumulative_rewards.png` — learning curves (Dyna-Q vs Dyna-Q+).

## How to Run
Run **from the `lessons/` directory** so the environment import resolves:

```bash
cd lessons
python lesson_5_code.py
```

## Expected Results
Both algorithms learn a policy that routes from the start `[S]` down and along
the safe corridor to the goal `[G]`, avoiding the `[X]` death cells. With enough
training episodes the greedy policies reach the goal and the evaluated reward is
positive (≈ **3.6–3.8**) for the planning variants. The plot shows reward
improving as training progresses.
