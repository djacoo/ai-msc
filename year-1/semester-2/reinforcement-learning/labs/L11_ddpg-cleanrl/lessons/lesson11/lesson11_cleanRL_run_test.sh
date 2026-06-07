#!/bin/bash

echo "=============================================="
echo "Running CleanRL DDPG Test"
echo "=============================================="

# Set the environment ID
ENV_ID="Pendulum-v1"

# IMPORTANT: Replace the path below with the actual path to your trained model
MODEL_PATH="ddpg_Pendulum-v1_actor.pth"

echo "Testing on $ENV_ID with model $MODEL_PATH"
echo ""

python test.py --env-id $ENV_ID --model-path "$MODEL_PATH"
