#!/bin/bash

# Setup Environments list
ENVS=("MountainCar-v0")

# OTHER ENVIRONMENTS: "CartPole-v1" "LunarLander-v2" "Acrobot-v1" "MountainCar-v0" "MountainCarContinuous-v0" "Pendulum-v1" "BipedalWalker-v3"

echo "Running CleanRL PPO training on multiple environments..."
for ENV in "${ENVS[@]}"; do
    echo ""
    echo "=============================================="
    echo "Training on $ENV"
    echo "=============================================="
    python lesson10_cleanRL_ppo_train_code.py --env-id $ENV --total-timesteps 50000
done

echo "All environments trained via CleanRL Solution script!"
