#!/bin/bash

echo "=============================================="
echo "Running CleanRL PPO Test"
echo "=============================================="

# Set the environment ID
ENV_ID="CartPole-v1"

# IMPORTANT: Replace the path below with the actual path to your trained model
# Example: runs/CartPole-v1__ppo_cleanRL_solution__1__1684594234/ppo_cleanRL_solution.cleanrl_model
MODEL_PATH=""

echo "Testing on $ENV_ID with model $MODEL_PATH"
echo ""

python lesson10_cleanRL_test.py --env-id $ENV_ID --model-path "$MODEL_PATH"
