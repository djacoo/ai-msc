import argparse
import os
import gymnasium as gym
import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np

class Actor(nn.Module):
    def __init__(self, envs):
        super().__init__()
        self.fc1 = nn.Linear(np.array(envs.single_observation_space.shape).prod(), 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc_mu = nn.Linear(256, np.prod(envs.single_action_space.shape))
        
        self.register_buffer(
            "action_scale", torch.tensor((envs.single_action_space.high - envs.single_action_space.low) / 2.0, dtype=torch.float32)
        )
        self.register_buffer(
            "action_bias", torch.tensor((envs.single_action_space.high + envs.single_action_space.low) / 2.0, dtype=torch.float32)
        )

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = torch.tanh(self.fc_mu(x))
        return x * self.action_scale + self.action_bias

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-id", type=str, default="Pendulum-v1", help="the id of the environment")
    parser.add_argument("--model-path", type=str, required=True, help="path to the trained model (.cleanrl_model file)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    env = gym.make(args.env_id, render_mode="human")
    
    # Mocking single_action_space and single_observation_space required by the exact CleanRL Agent
    env.single_action_space = env.action_space
    env.single_observation_space = env.observation_space
    
    agent = Actor(env)
    
    # Load the trained model weights
    if not os.path.exists(args.model_path):
        print(f"Error: The model path '{args.model_path}' does not exist.")
        exit(1)
        
    agent.load_state_dict(torch.load(args.model_path, map_location=torch.device('cpu')))
    agent.eval()

    # Run a single episode
    obs, info = env.reset()
    done = False
    total_reward = 0

    print(f"Starting test episode for environment: {args.env_id}")
    while not done:
        obs_tensor = torch.Tensor(obs).unsqueeze(0)
        
        with torch.no_grad():
            action = agent(obs_tensor)
            
        action = action.cpu().numpy()[0]
        
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward

    print(f"Episode finished. Total Reward: {total_reward}")
    env.close()
