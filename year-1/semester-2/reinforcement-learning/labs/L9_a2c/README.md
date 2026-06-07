# Lab 9 — Advantage Actor-Critic (A2C)

Deep Reinforcement Learning lab on the **Advantage Actor-Critic** algorithm, trained on
`CartPole-v1` (Gymnasium). The same agent is implemented twice — once in **PyTorch** and once
in **TensorFlow/Keras** — and their learning curves are compared.

## Topic & theory recap

A2C combines a **policy network (actor)** and a **value network (critic)** trained jointly.

- **REINFORCE vs. actor-critic.** Plain REINFORCE scales each action's log-probability by the
  Monte-Carlo return `G_t`, an unbiased but high-variance signal. Subtracting a *baseline*
  `b(s)` reduces variance without adding bias. Actor-critic goes one step further: it learns the
  state value `V(s)` as that baseline and **bootstraps** it (uses its own estimate of the next
  state's value), trading a little bias for a large variance reduction and faster, online updates.

- **TD error as advantage.** The advantage measures how much better an action did than the
  critic expected:

  ```
  A(s, a) = r + gamma * V(s') - V(s)        (with V(s') = 0 if s' is terminal)
  ```

  This is exactly the one-step **TD error**. It is positive when the action beat the baseline and
  negative otherwise, giving the actor a low-variance learning signal.

- **The two losses.**
  - *Actor (policy):* maximize `log pi(a|s) * A`, i.e. minimize `-log pi(a|s) * A`. The advantage
    is **detached** (treated as a constant weight) so gradients flow only through the policy.
    A small **entropy bonus** is added to keep the policy stochastic and avoid premature collapse.
  - *Critic (value):* minimize `MSE(V(s), r + gamma * V(s'))`, which is the same as minimizing the
    squared advantage. The bootstrapped target is detached (it is a regression label).

  Both networks are updated with Adam; gradient norms are clipped and advantages are normalized
  per batch to stabilize training.

In CartPole the reward is a constant `+1` per step, so the *only* directional signal comes from
terminal transitions (where `V(s') = 0`). This makes the policy gradient weak and noisy, which is
why advantage normalization, gradient clipping, an entropy bonus, and a few actor steps per batch
matter for reliable learning.

## Files

| File | Description |
| --- | --- |
| `lessons/lesson_9_code.py` | Full A2C implementation: actor/critic networks (Keras + PyTorch), training loop, and the `A2C` update rule. |
| `results/a2c_learning_curve.png` | Mean-reward learning curve (PyTorch vs. Keras, mean ± std-error over 3 seeds). |
| `results/lesson_9_results.txt` | Console log of the successful training run. |

## How to run

From the `lessons/` directory:

```bash
python lesson_9_code.py
```

The script trains 3 PyTorch agents and 3 Keras agents, prints per-episode returns, and saves the
comparison plot to `results/a2c_learning_curve.png`. Plotting is headless (Matplotlib `Agg`
backend), so no display is required.

Tested with: numpy < 2, torch 2.8.0, tensorflow 2.20.0 (Keras 3), gymnasium 1.1.1.

## Expected results

`training_episodes` is reduced from the original 5000 to **700** to keep the run to a few minutes
of wall-clock while still showing clear learning.

- Both backends start near the random baseline (~15 average reward) and climb steadily.
- The 100-episode rolling average rises into the **hundreds**; individual episodes frequently reach
  the CartPole-v1 cap of **500**. In the reference run the peak averaged return was ~**350**
  (PyTorch around ~235 averaged, Keras around ~130 averaged at the end).
- Some run-to-run dips are expected — A2C on CartPole is known for occasional catastrophic
  forgetting — but the overall trend is clearly upward.
