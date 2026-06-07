import argparse
import os
import gymnasium as gym
import torch
import torch.nn as nn
import numpy as np
from torch.distributions.categorical import Categorical
from torch.distributions.normal import Normal

def layer_init(layer, std=np.sqrt(2), bias_const=0.0):
    torch.nn.init.orthogonal_(layer.weight, std)
    torch.nn.init.constant_(layer.bias, bias_const)
    return layer

class Agent(nn.Module):
    def __init__(self, envs):
        super().__init__()
        self.is_continuous = isinstance(envs.single_action_space, gym.spaces.Box)
        
        self.critic = nn.Sequential(
            layer_init(nn.Linear(np.array(envs.single_observation_space.shape).prod(), 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 1), std=1.0),
        )
        self.actor_mean = nn.Sequential(
            layer_init(nn.Linear(np.array(envs.single_observation_space.shape).prod(), 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, 64)),
            nn.Tanh(),
            layer_init(nn.Linear(64, envs.single_action_space.shape[0] if self.is_continuous else envs.single_action_space.n), std=0.01),
        )
        if self.is_continuous:
            self.actor_logstd = nn.Parameter(torch.zeros(1, np.prod(envs.single_action_space.shape)))

    def get_value(self, x):
        return self.critic(x)

    def get_action_and_value(self, x, action=None):
        action_mean = self.actor_mean(x)
        if self.is_continuous:
            action_logstd = self.actor_logstd.expand_as(action_mean)
            action_std = torch.exp(action_logstd)
            probs = Normal(action_mean, action_std)
        else:
            probs = Categorical(logits=action_mean)
            
        if action is None:
            action = probs.sample()
            
        if self.is_continuous:
            return action, probs.log_prob(action).sum(1), probs.entropy().sum(1), self.critic(x)
        else:
            return action, probs.log_prob(action), probs.entropy(), self.critic(x)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-id", type=str, default="CartPole-v1", help="the id of the environment")
    parser.add_argument("--model-path", type=str, required=True, help="path to the trained model (.cleanrl_model file)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    env = gym.make(args.env_id, render_mode="human")
    
    # Mocking single_action_space and single_observation_space required by the exact CleanRL Agent
    env.single_action_space = env.action_space
    env.single_observation_space = env.observation_space
    
    agent = Agent(env)
    
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
            action, _, _, _ = agent.get_action_and_value(obs_tensor)
            
        action = action.cpu().numpy()[0]
        
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        total_reward += reward

    print(f"Episode finished. Total Reward: {total_reward}")
    env.close()
