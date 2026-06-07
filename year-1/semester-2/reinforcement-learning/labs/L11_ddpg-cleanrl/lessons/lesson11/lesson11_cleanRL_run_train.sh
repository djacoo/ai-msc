#!/bin/bash

# Setup Environments list
ENVS=("Pendulum-v1")

# OTHER ENVIRONMENTS: "Pendulum-v1" "MountainCarContinuous-v0" "BipedalWalker-v3"

echo "Running CleanRL DDPG training on multiple environments..."
for ENV in "${ENVS[@]}"; do
    echo ""
    echo "=============================================="
    echo "Training on $ENV"
    echo "=============================================="
    python lesson11_cleanRL_ddpg_train_solution.py --env-id $ENV --total-timesteps 50000
done

echo "All environments trained via CleanRL Solution script!"
