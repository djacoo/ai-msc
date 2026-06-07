import argparse
import os
import random
import time

import gymnasium as gym
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import matplotlib
matplotlib.use("Agg")  # study note: headless backend so savefig works without a display
import matplotlib.pyplot as plt

# =====================================================================
# ENVIRONMENT AND NETWORK STRUCTURE
# =====================================================================

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env-id", type=str, default="Pendulum-v1")
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--total-timesteps", type=int, default=50000)
    parser.add_argument("--buffer-size", type=int, default=int(1e6))
    parser.add_argument("--gamma", type=float, default=0.99)
    parser.add_argument("--tau", type=float, default=0.005) 
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--exploration-noise", type=float, default=0.1)
    parser.add_argument("--learning-starts", type=int, default=25000)
    return parser.parse_args()

def make_env(env_id, seed):
    def thunk():
        env = gym.make(env_id)
        env.action_space.seed(seed)
        return env
    return thunk

class ReplayBuffer:
    def __init__(self, capacity, obs_space, action_space, device):
        self.capacity = capacity
        self.device = device
        self.obs = np.zeros((capacity, *obs_space.shape), dtype=np.float32)
        self.next_obs = np.zeros((capacity, *obs_space.shape), dtype=np.float32)
        self.actions = np.zeros((capacity, *action_space.shape), dtype=np.float32)
        self.rewards = np.zeros((capacity,), dtype=np.float32)
        self.dones = np.zeros((capacity,), dtype=np.float32)
        self.pos = 0
        self.size = 0

    def add(self, obs, next_obs, action, reward, done):
        self.obs[self.pos] = obs
        self.next_obs[self.pos] = next_obs
        self.actions[self.pos] = action
        self.rewards[self.pos] = reward
        self.dones[self.pos] = done
        self.pos = (self.pos + 1) % self.capacity
        self.size = min(self.size + 1, self.capacity)

    def sample(self, batch_size):
        idxs = np.random.randint(0, self.size, size=batch_size)
        return (
            torch.as_tensor(self.obs[idxs]).to(self.device),
            torch.as_tensor(self.actions[idxs]).to(self.device),
            torch.as_tensor(self.rewards[idxs]).to(self.device),
            torch.as_tensor(self.next_obs[idxs]).to(self.device),
            torch.as_tensor(self.dones[idxs]).to(self.device)
        )

class QNetwork(nn.Module):
    def __init__(self, envs):
        super().__init__()
        self.fc1 = nn.Linear(np.array(envs.single_observation_space.shape).prod() + np.prod(envs.single_action_space.shape), 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc3 = nn.Linear(256, 1)

    def forward(self, x, a):
        x = torch.cat([x, a], 1)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class Actor(nn.Module):
    def __init__(self, envs):
        super().__init__()
        self.fc1 = nn.Linear(np.array(envs.single_observation_space.shape).prod(), 256)
        self.fc2 = nn.Linear(256, 256)
        self.fc_mu = nn.Linear(256, np.prod(envs.single_action_space.shape))
        self.register_buffer("action_scale", torch.tensor((envs.single_action_space.high - envs.single_action_space.low) / 2.0, dtype=torch.float32))
        self.register_buffer("action_bias", torch.tensor((envs.single_action_space.high + envs.single_action_space.low) / 2.0, dtype=torch.float32))

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = torch.tanh(self.fc_mu(x))
        return x * self.action_scale + self.action_bias


if __name__ == "__main__":
    args = parse_args()
    
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    envs = gym.vector.SyncVectorEnv([make_env(args.env_id, args.seed)])
    
    actor = Actor(envs).to(device)
    qf1 = QNetwork(envs).to(device)
    target_actor = Actor(envs).to(device)
    qf1_target = QNetwork(envs).to(device)
    target_actor.load_state_dict(actor.state_dict())
    qf1_target.load_state_dict(qf1.state_dict())
    
    q_optimizer = optim.Adam(list(qf1.parameters()), lr=args.learning_rate)
    pi_optimizer = optim.Adam(list(actor.parameters()), lr=args.learning_rate)

    rb = ReplayBuffer(args.buffer_size, envs.single_observation_space, envs.single_action_space, device)
    
    # Manual Foolproof Episode Tracking
    episode_returns = []
    episode_lengths = []
    current_ep_return = 0.0
    current_ep_length = 0

    start_time = time.time()
    obs, _ = envs.reset(seed=args.seed)
    
    print(f"--- Starting DDPG Training on {args.env_id} ---")
    
    for global_step in range(args.total_timesteps):
        
        if global_step < args.learning_starts:
            actions = np.array([envs.single_action_space.sample() for _ in range(envs.num_envs)])
        else:
            with torch.no_grad():
                actions = actor(torch.Tensor(obs).to(device))
                actions += torch.normal(0, actor.action_scale * args.exploration_noise)
                actions = actions.cpu().numpy().clip(envs.single_action_space.low, envs.single_action_space.high)

        next_obs, rewards, terminations, truncations, infos = envs.step(actions)

        # Track returns manually
        current_ep_return += float(rewards[0])
        current_ep_length += 1

        # Check for episode end
        if terminations[0] or truncations[0]:
            episode_returns.append(current_ep_return)
            episode_lengths.append(current_ep_length)
            
            avg_return = np.mean(episode_returns[-50:])
            print(f"Step: {global_step:7d} | Ep Return: {current_ep_return:7.2f} | Avg Return (last 50): {avg_return:7.2f} | Ep Length: {current_ep_length:4.0f}")
            
            current_ep_return = 0.0
            current_ep_length = 0

        # Handle real next observation for truncations
        real_next_obs = next_obs.copy()
        for idx, (term, trunc) in enumerate(zip(terminations, truncations)):
            if (term or trunc) and "final_observation" in infos:
                real_next_obs[idx] = infos["final_observation"][idx]
                
        rb.add(obs[0], real_next_obs[0], actions[0], rewards[0], terminations[0])
        obs = next_obs

        if global_step > args.learning_starts:
            b_obs, b_actions, b_rewards, b_next_obs, b_dones = rb.sample(args.batch_size)

            # =====================================================================
            # 1. UPDATE Q-NETWORK (CRITIC)
            # =====================================================================
            # Bellman target: y = r + gamma * (1 - done) * Q_target(s', mu_target(s')).
            # The target networks are used to stabilise the regression target.
            with torch.no_grad():
                next_actions = target_actor(b_next_obs)
                qf1_next_target = qf1_target(b_next_obs, next_actions).view(-1)
                next_q_value = b_rewards.flatten() + (1 - b_dones.flatten()) * args.gamma * qf1_next_target

            qf1_a_values = qf1(b_obs, b_actions).view(-1)
            qf1_loss = F.mse_loss(qf1_a_values, next_q_value)

            q_optimizer.zero_grad()
            qf1_loss.backward()
            q_optimizer.step()

            # =====================================================================
            # 2. UPDATE POLICY (ACTOR) - Deterministic Policy Gradient
            # =====================================================================
            # Maximise Q(s, mu(s)) w.r.t. the actor params -> minimise its negative.
            actor_loss = -qf1(b_obs, actor(b_obs)).mean()

            pi_optimizer.zero_grad()
            actor_loss.backward()
            pi_optimizer.step()

            # =====================================================================
            # 3. UPDATE TARGET NETWORKS (POLYAK / soft averaging)
            # =====================================================================
            # theta_target <- tau * theta + (1 - tau) * theta_target
            with torch.no_grad():
                for param, target_param in zip(actor.parameters(), target_actor.parameters()):
                    target_param.data.copy_(args.tau * param.data + (1.0 - args.tau) * target_param.data)
                for param, target_param in zip(qf1.parameters(), qf1_target.parameters()):
                    target_param.data.copy_(args.tau * param.data + (1.0 - args.tau) * target_param.data)

            if global_step % 5000 == 0:
                sps = int(global_step / (time.time() - start_time))
                print(f"[Metrics] Step: {global_step}/{args.total_timesteps} | Q-Loss: {qf1_loss.item():.4f} | Pi-Loss: {actor_loss.item():.4f} | SPS: {sps}")

    envs.close()
    
    # --- MODEL SAVING ---
    print("\n--- Saving Model ---")
    os.makedirs("models", exist_ok=True)
    model_path = f"models/ddpg_{args.env_id}_actor.pth"
    torch.save(actor.state_dict(), model_path)
    print(f"Success: Actor model saved to {model_path}")
    
    # --- PLOTTING ---
    print("\n--- Generating Plot ---")
    if len(episode_returns) > 0:
        plt.figure(figsize=(10, 5))
        plt.plot(episode_returns, label='Episodic Return', alpha=0.5, color='blue')
        
        window_size = min(50, len(episode_returns))
        moving_avg = np.convolve(episode_returns, np.ones(window_size)/window_size, mode='valid')
        plt.plot(range(window_size - 1, len(episode_returns)), moving_avg, label=f'{window_size}-Episode Moving Average', color='red', linewidth=2)
        
        plt.title(f"DDPG Learning Curve on {args.env_id}")
        plt.xlabel("Episode")
        plt.ylabel("Return")
        plt.legend()
        plt.grid(True)
        
        plot_filename = f"ddpg_learning_curve_{args.env_id}.png"
        plt.savefig(plot_filename)
        print(f"Success: Plot saved to {plot_filename}")

        # study note: also drop a copy into the lab's results/ folder for the report
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "results")
        os.makedirs(results_dir, exist_ok=True)
        results_plot_path = os.path.join(results_dir, "ddpg_learning_curve.png")
        plt.savefig(results_plot_path)
        print(f"Success: Plot also saved to {results_plot_path}")
        # plt.show()  # disabled: Agg backend is headless
    else:
        print("Error: No episodes completed during training.")
