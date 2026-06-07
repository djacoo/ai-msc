# Lab 8 — REINFORCE (Monte-Carlo Policy Gradient)

Deep Reinforcement Learning lab on **REINFORCE**, the naive Monte-Carlo policy-gradient
algorithm, in two variants: **without baseline** and **with a learned value baseline**.
Environment: `CartPole-v1` (Gymnasium). Both a TensorFlow/Keras and a PyTorch implementation
are provided and trained with the *same* update rule.

## Topic & theory recap

### Policy gradient theorem
Instead of learning value functions and acting greedily, policy-gradient methods directly
parameterize a stochastic policy `pi_theta(a|s)` (here a softmax over actions) and optimize the
expected return `J(theta) = E[ sum_t gamma^t r_t ]`. The policy gradient theorem gives an
estimator that does not require differentiating the environment dynamics:

```
grad_theta J(theta) = E[ sum_t grad_theta log pi_theta(a_t|s_t) * G_t ]
```

where `G_t = sum_{k>=t} gamma^{k-t} r_k` is the (reward-to-go) discounted return from step `t`.

### REINFORCE update
REINFORCE is the Monte-Carlo realization: run a full episode, compute the returns `G_t`, and take
a gradient ascent step. Implemented as a *minimization* of the negative objective:

```
loss = - sum_t log pi_theta(a_t|s_t) * G_t
```

Returns `G_t` are computed backwards in one pass: `G_t = r_t + gamma * G_{t+1}`.

### Role of the baseline (variance reduction)
The plain estimator is unbiased but has **high variance**, because the absolute magnitude of
`G_t` scales every gradient. Subtracting any state-dependent baseline `b(s_t)` leaves the gradient
unbiased while reducing its variance:

```
loss = - sum_t log pi_theta(a_t|s_t) * ( G_t - b(s_t) )
```

The natural choice is `b(s_t) = V(s_t)`, a learned value network trained by regression
(`MSE(V(s_t), G_t)`). The weighting term becomes the **advantage** `A_t = G_t - V(s_t)`: actions
that did better than expected are reinforced, worse-than-expected ones are discouraged. This
typically yields faster, more stable learning than the no-baseline version.

## Files
- `lessons/lesson_8_code.py` — full implementation: policy network (`createDNN` / `TorchModel`),
  value network (`createValueDNN` / `ValueModel`), `training_loop`, and the `REINFORCE` update rule
  (both Keras and PyTorch; both variants).
- `results/reinforce_learning_curve.png` — learning curves, REINFORCE vs REINFORCE+baseline.
- `results/lesson_8_results.txt` — console log of the successful run.
- `slides/`, `tutorials/`, `tools/` — provided course material (untouched).

## How to run
```bash
cd lessons
python lesson_8_code.py
```
The figure is written to `results/reinforce_learning_curve.png` (headless `Agg` backend, no GUI
needed). To switch to the PyTorch implementation, set `use_torch = True` in `main()`.

### Configuration notes
- Adapted to the installed stack: numpy<2, torch 2.8.0, tensorflow 2.20.0 (Keras 3),
  gymnasium 1.1.1. Gymnasium 1.x API is used (`reset() -> (obs, info)`,
  `step() -> (obs, reward, terminated, truncated, info)`, `done = terminated or truncated`),
  and the Keras 3 explicit `Input` layer.
- For runtime, `training_episodes` was reduced from 1200 to **500** and `number_seeds_to_test`
  from 3 to **2** — the curve still rises clearly and plateaus.
- The learning rate was raised from the template's `4e-5` (too small to show learning) to
  `1e-3` (policy) / `5e-3` (value network), the usual range for REINFORCE on CartPole.

## Expected results
Both variants start near the random-policy return (~10-20 steps) and rise toward the CartPole-v1
maximum of 500. Reference run (Keras, 500 episodes, 2 seeds):

| Variant | Start (mean) | End (mean) | Peak (mean) |
|---|---|---|---|
| REINFORCE (no baseline) | ~13 | ~250-300 | ~290 |
| REINFORCE + baseline    | ~20 | ~450-500 | ~490 |

Reading the curves: both clearly learn, but the **baseline variant learns faster and reaches a
higher, less noisy plateau** (closer to the 500 cap). The shaded band (standard error across
seeds) is narrower for the baseline run — the visual confirmation of the variance reduction the
value baseline provides.
