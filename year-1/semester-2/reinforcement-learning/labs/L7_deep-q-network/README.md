# Lab 7 — Deep Q-Network (DQN)

Deep Reinforcement Learning lab: train a **Deep Q-Network** to solve the classic
`CartPole-v1` control task, implemented twice (PyTorch and TensorFlow/Keras) so the
two frameworks can be compared on the same problem.

## Topic & Theory Recap

Tabular Q-learning learns the optimal action-value function `Q*(s, a)` by storing one
value per state–action pair. That breaks down when the state space is large or
continuous (CartPole states are 4 real numbers). **DQN** keeps the Q-learning update
but replaces the table with a **neural network function approximator**
`Q(s, a; θ)` that maps a state to one Q-value per action.

The three ideas that make this work:

1. **Q-learning + function approximation.** The network outputs a vector of Q-values,
   one per action. Acting greedily means picking `argmax_a Q(s, a; θ)`; exploration is
   added with an **ε-greedy** policy (random action with probability ε, otherwise
   greedy). ε decays over time so the agent explores early and exploits later.

2. **Experience replay.** Each transition `(s, a, r, s', done)` is pushed into a replay
   buffer. Training samples *random* mini-batches from this buffer. Random sampling
   breaks the temporal correlation between consecutive transitions, which stabilizes
   the gradient updates.

3. **Bootstrapped TD target.** For each sampled transition the regression target is

   ```
   y = r                               if s' is terminal (done)
   y = r + γ · max_a' Q(s', a'; θ)     otherwise
   ```

   The network is then trained with a gradient-descent step that minimizes the
   **MSE** between its prediction `Q(s, a; θ)` and the target `y`. Only the entry for
   the action actually taken is corrected; the predictions for the other actions are
   left unchanged (their error is zero in the loss).

> Note: this lab uses the *online* network to compute the target (no separate target
> network). This is the minimal DQN formulation; it learns CartPole well but is more
> sensitive to the random seed than the full DQN with a frozen target network.

## Files

| File | Description |
|------|-------------|
| `lessons/lesson_7_code.py` | Full DQN implementation (PyTorch + Keras), training loop, ε-greedy policy, replay buffer, DQN update, plotting. |
| `results/lesson_7_results.txt` | Console log of the successful training run. |
| `results/dqn_learning_curve.png` | Learning curve: mean reward vs. episode for both frameworks. |
| `slides/`, `tutorials/`, `tools/` | Course material (not modified). |

What was implemented in `lesson_7_code.py`:

- `createDNN_keras` — Keras 3 MLP: `Input(shape=(4,))` → `nLayer` ReLU hidden layers → linear output (one Q-value per action).
- `TorchModel` — the equivalent PyTorch MLP (`__init__` builds the hidden layers, `forward` applies ReLU + linear output head).
- `training_loop` — Adam optimizer, environment interaction with the ε-greedy policy, replay buffer, per-episode ε decay, gymnasium 1.x API handling.
- `DQNupdate` — vectorized mini-batch sampling, Bellman TD target, and a single MSE gradient-descent step for both frameworks.

## How to Run

From the `lessons/` directory, using the provided virtual environment:

```bash
cd lessons
python lesson_7_code.py
```

Plotting is headless (`matplotlib.use("Agg")`), so no display is required; the figure
is written directly to `results/dqn_learning_curve.png`.

### Environment

Runs against newer libraries than the original course targets (the code was adapted
accordingly): `numpy<2`, `torch 2.8`, `tensorflow 2.20` (Keras 3), `gymnasium 1.1`,
plus `pandas`, `seaborn`, `matplotlib`.

### Adaptations vs. the original template

- **gymnasium 1.x API**: `env.reset()` returns `(obs, info)` and `env.step(a)` returns
  `(obs, reward, terminated, truncated, info)`; `done = terminated or truncated`.
- **Keras 3**: explicit `Input` layer, `model(x)` for fast single/batch inference
  (instead of the slow `model.predict`), and `tf.GradientTape` + `apply_gradients`.
- **DQN update is vectorized** over the mini-batch (a few tensor ops instead of a
  per-sample Python loop) — same math, far faster.
- **Reduced workload for runtime**: `training_steps = 150` episodes and `runs = 3`
  per framework (original template: 50 episodes × 10 runs). The replay buffer was
  enlarged (`maxlen = 10000`) and the learning rate set to `5e-4`, which gives a
  clearly rising, more stable learning curve. Total wall-clock is a few minutes
  (PyTorch is roughly an order of magnitude faster than Keras here).

## Expected Results

The reward reported each episode is the **running mean of all episode returns so far**
(this is what gets plotted), so it lags the instantaneous performance and smooths out
single-episode dips.

Typical curve (see `results/dqn_learning_curve.png`):

1. **Episodes 0–60 — exploration phase.** ε is high, the agent acts mostly at random,
   and the running mean sits low (~13–20). It may even dip slightly: this is expected.
2. **Episodes ~70–150 — exploitation phase.** As ε decays toward its floor, the learned
   greedy policy takes over and the curve rises sharply and accelerates.

In the recorded run:

- **Per-episode return** reaches the CartPole maximum of **500** in the best PyTorch
  and Keras runs, with the final 10 episodes averaging ~150–185 (PyTorch) and up to
  ~500 (best Keras run).
- **Running-mean** final values: PyTorch ≈ 48–71, best Keras run ≈ 157 — all still
  climbing at episode 150.

Because there is no target network, the outcome varies between seeds/runs (this is
genuine DQN behaviour), but the **averaged curve across runs clearly improves**, which
is the point of the exercise: a neural-network Q-function, trained from replayed
experience with a bootstrapped TD target, learns to balance the pole.
