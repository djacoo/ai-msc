# Reinforcement Learning — Laboratory

Solved and runnable lab exercises for the *Reinforcement Learning* course
(MSc Artificial Intelligence, University of Verona). Each lab is **self-contained**:
its own `lessons/` (solution code), `results/` (logs + plots), `slides/`, `tools/`
(shared environments) and `tutorials/`.

All `# YOUR CODE HERE!` exercises and incomplete function bodies have been
implemented, commented for study, executed, and their outputs saved.

## Index

| # | Lab | Topic | Stack | Key result |
|---|-----|-------|-------|------------|
| L1 | `L1_multi-armed-bandits` | ε-greedy simple-bandit algorithm, 10-armed testbed | NumPy | ε=0.1 best average reward; greedy gets stuck |
| L2 | `L2_mdp-gym-environments` | MDPs, Gym-style envs (grid-world rollout, Recycling Robot) | NumPy | custom env matches Sutton & Barto dynamics |
| L3 | `L3_monte-carlo` | Monte-Carlo control (ε-soft & exploring starts) | NumPy | learned policy ≈ near-optimal (eval ≈ 3.1–3.3) |
| L4 | `L4_temporal-difference` | TD control: Q-Learning (off-policy) & SARSA (on-policy) | NumPy | both route safely to the goal |
| L5 | `L5_dyna-q` | Dyna-Q & Dyna-Q+ (model-based planning) | NumPy | eval reward ≈ 3.6–3.8 |
| L6 | `L6_tensorflow-pytorch-dnn` | DNN primer in TensorFlow/Keras **and** PyTorch | TF + Torch | both frameworks agree (min at (2,−1) = −6) |
| L7 | `L7_deep-q-network` | Deep Q-Network (Q-learning + function approx + replay) | TF + Torch + Gym | CartPole, peak return 500 |
| L8 | `L8_reinforce` | REINFORCE (MC policy gradient), with/without baseline | Keras + Gym | baseline ≈ 488 vs no-baseline ≈ 410 (lower variance) |
| L9 | `L9_a2c` | Advantage Actor-Critic (bootstrapping critic) | TF + Torch + Gym | CartPole, peak mean return ≈ 350 |
| L10 | `L10_ppo-cleanrl` | PPO (clipped surrogate, GAE) — CleanRL | Torch + Gym | CartPole, SMA-10 ≈ 200, peaks 500 |
| L11 | `L11_ddpg-cleanrl` | DDPG (deterministic PG, replay, target nets) — CleanRL | Torch + Gym | Pendulum, return −1500 → ≈ −150 |

The progression mirrors the course: tabular RL (L1–L5) → deep-learning tooling
(L6) → value-based deep RL (L7) → policy-gradient & actor-critic (L8–L9) →
state-of-the-art deep RL (L10–L11).

## Setup

The deep-RL labs need a Python environment. Tested with Python 3.9 and:

```
numpy<2  matplotlib  scipy  tqdm  pandas  seaborn
torch  gymnasium[classic-control]  gym  tensorflow  tensorboard
```

Create it once and reuse it for every lab:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "numpy<2" matplotlib scipy tqdm pandas seaborn \
            torch "gymnasium[classic-control]" gym tensorflow tensorboard
```

> L1–L5 only require `numpy` + `matplotlib`. L6–L11 additionally need
> `torch` / `tensorflow` / `gymnasium`.

The original conda spec shipped with the course is kept in each lab under
`tools/rl-lab-environment.yml`.

## Running a lab

Each lab's `README.md` has the exact command. The classic-RL lessons must be run
from their `lessons/` directory so the shared `tools/` modules import correctly:

```bash
cd L4_temporal-difference/lessons
python lesson_4_code.py
```

Plots are written headlessly (matplotlib `Agg`) into the lab's `results/` folder,
and console output is saved as `results/lesson_X_results.txt`.

## Notes

- Code was adapted to current library versions (gymnasium 1.x 5-tuple `step`
  API, Keras 3) while preserving each algorithm exactly.
- Deep-RL training is stochastic; the saved numbers/plots are representative
  single runs. Where training length was reduced for runtime, it is noted in the
  lab's own README.
