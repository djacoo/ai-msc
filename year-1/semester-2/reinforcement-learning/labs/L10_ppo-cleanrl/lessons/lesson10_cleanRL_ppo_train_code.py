import argparse
import os
import random
import time
from collections import deque
from distutils.util import strtobool

import gymnasium as gym
import matplotlib
matplotlib.use("Agg")  # study note: headless backend so savefig works without a display
import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions.categorical import Categorical
from torch.distributions.normal import Normal
from torch.utils.tensorboard import SummaryWriter

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--exp-name", type=str, default=os.path.basename(__file__).rstrip(".py"),
        help="the name of this experiment")
    parser.add_argument("--env-id", type=str, default="CartPole-v1",
        help="the id of the environment")
    parser.add_argument("--learning-rate", type=float, default=2.5e-4,
        help="the learning rate of the optimizer")
    parser.add_argument("--seed", type=int, default=1,
        help="seed of the experiment")
    parser.add_argument("--total-timesteps", type=int, default=100000,
        help="total timesteps of the experiments")
    parser.add_argument("--torch-deterministic", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
        help="if toggled, `torch.backends.cudnn.deterministic=False`")
    parser.add_argument("--cuda", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
        help="if toggled, cuda will be enabled by default")
    
    # Algorithm specific arguments
    parser.add_argument("--num-envs", type=int, default=4,
        help="the number of parallel game environments")
    parser.add_argument("--num-steps", type=int, default=128,
        help="the number of steps to run in each environment per policy rollout")
    parser.add_argument("--anneal-lr", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
        help="Toggle learning rate annealing for policy and value networks")
    parser.add_argument("--gamma", type=float, default=0.99,
        help="the discount factor gamma")
    parser.add_argument("--gae-lambda", type=float, default=0.95,
        help="the lambda for the general advantage estimation")
    parser.add_argument("--num-minibatches", type=int, default=4,
        help="the number of mini-batches")
    parser.add_argument("--update-epochs", type=int, default=4,
        help="the K epochs to update the policy")
    parser.add_argument("--norm-adv", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
        help="Toggles advantages normalization")
    parser.add_argument("--clip-coef", type=float, default=0.2,
        help="the surrogate clipping coefficient")
    parser.add_argument("--clip-vloss", type=lambda x: bool(strtobool(x)), default=True, nargs="?", const=True,
        help="Toggles whether or not to use a clipped loss for the value function, as per the paper.")
    parser.add_argument("--ent-coef", type=float, default=0.01,
        help="coefficient of the entropy")
    parser.add_argument("--vf-coef", type=float, default=0.5,
        help="coefficient of the value function")
    parser.add_argument("--max-grad-norm", type=float, default=0.5,
        help="the maximum norm for the gradient clipping")
    args = parser.parse_args()
    args.batch_size = int(args.num_envs * args.num_steps)
    args.minibatch_size = int(args.batch_size // args.num_minibatches)
    return args

def make_env(env_id, seed, idx, capture_video, run_name):
    def thunk():
        env = gym.make(env_id)
        env = gym.wrappers.RecordEpisodeStatistics(env)
        if capture_video:
            if idx == 0:
                env = gym.wrappers.RecordVideo(env, f"videos/{run_name}")
        env.action_space.seed(seed)
        env.observation_space.seed(seed)
        return env
    return thunk

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

if __name__ == "__main__":
    args = parse_args()
    run_name = f"{args.env_id}__{args.exp_name}__{args.seed}__{int(time.time())}"
    writer = SummaryWriter(f"runs/{run_name}")

    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    torch.backends.cudnn.deterministic = args.torch_deterministic

    device = torch.device("cuda" if torch.cuda.is_available() and args.cuda else "cpu")

    envs = gym.vector.SyncVectorEnv(
        [make_env(args.env_id, args.seed + i, i, False, run_name) for i in range(args.num_envs)]
    )

    agent = Agent(envs).to(device)
    optimizer = optim.Adam(agent.parameters(), lr=args.learning_rate, eps=1e-5)

    # Storage setup
    obs = torch.zeros((args.num_steps, args.num_envs) + envs.single_observation_space.shape).to(device)
    actions = torch.zeros((args.num_steps, args.num_envs) + envs.single_action_space.shape).to(device)
    logprobs = torch.zeros((args.num_steps, args.num_envs)).to(device)
    rewards = torch.zeros((args.num_steps, args.num_envs)).to(device)
    dones = torch.zeros((args.num_steps, args.num_envs)).to(device)
    values = torch.zeros((args.num_steps, args.num_envs)).to(device)

    global_step = 0
    start_time = time.time()
    
    episode_returns = deque(maxlen=100)
    episode_lengths = deque(maxlen=100)
    history_returns = []
    history_steps = []
    
    next_obs, _ = envs.reset(seed=args.seed)
    next_obs = torch.Tensor(next_obs).to(device)
    next_done = torch.zeros(args.num_envs).to(device)
    num_updates = args.total_timesteps // args.batch_size

    for update in range(1, num_updates + 1):
        if args.anneal_lr:
            frac = 1.0 - (update - 1.0) / num_updates
            lrnow = frac * args.learning_rate
            optimizer.param_groups[0]["lr"] = lrnow

        for step in range(0, args.num_steps):
            global_step += 1 * args.num_envs
            obs[step] = next_obs
            dones[step] = next_done

            with torch.no_grad():
                action, logprob, _, value = agent.get_action_and_value(next_obs)
                values[step] = value.flatten()
            actions[step] = action
            logprobs[step] = logprob

            next_obs, reward, terminations, truncations, info = envs.step(action.cpu().numpy())
            next_done = np.logical_or(terminations, truncations)
            rewards[step] = torch.tensor(reward).to(device).view(-1)
            next_obs, next_done = torch.Tensor(next_obs).to(device), torch.Tensor(next_done).to(device)

            if "final_info" in info:
                for item in info["final_info"]:
                    if item and "episode" in item.keys():
                        ep_ret = item['episode']['r'].item() if isinstance(item['episode']['r'], np.ndarray) else item['episode']['r']
                        ep_len = item['episode']['l'].item() if isinstance(item['episode']['l'], np.ndarray) else item['episode']['l']
                        
                        episode_returns.append(ep_ret)
                        episode_lengths.append(ep_len)
                        history_returns.append(ep_ret)
                        history_steps.append(global_step)
                        
                        writer.add_scalar("charts/episodic_return", ep_ret, global_step)
                        writer.add_scalar("charts/episodic_length", ep_len, global_step)
            elif "episode" in info and "_episode" in info:
                for i, done_flag in enumerate(info["_episode"]):
                    if done_flag:
                        ep_ret = info["episode"]["r"][i].item() if hasattr(info["episode"]["r"][i], 'item') else info["episode"]["r"][i]
                        ep_len = info["episode"]["l"][i].item() if hasattr(info["episode"]["l"][i], 'item') else info["episode"]["l"][i]
                        
                        episode_returns.append(ep_ret)
                        episode_lengths.append(ep_len)
                        history_returns.append(ep_ret)
                        history_steps.append(global_step)
                        
                        writer.add_scalar("charts/episodic_return", ep_ret, global_step)
                        writer.add_scalar("charts/episodic_length", ep_len, global_step)

        with torch.no_grad():
            next_value = agent.get_value(next_obs).flatten()
            advantages = torch.zeros_like(rewards).to(device)
            lastgaelam = 0
            for t in reversed(range(args.num_steps)):
                if t == args.num_steps - 1:
                    nextnonterminal = 1.0 - next_done
                    nextvalues = next_value
                else:
                    nextnonterminal = 1.0 - dones[t + 1]
                    nextvalues = values[t + 1]
                delta = rewards[t] + args.gamma * nextvalues * nextnonterminal - values[t]
                advantages[t] = lastgaelam = delta + args.gamma * args.gae_lambda * nextnonterminal * lastgaelam
            returns = advantages + values

        b_obs = obs.reshape((-1,) + envs.single_observation_space.shape)
        b_logprobs = logprobs.reshape(-1)
        b_actions = actions.reshape((-1,) + envs.single_action_space.shape)
        b_advantages = advantages.reshape(-1)
        b_returns = returns.reshape(-1)
        b_values = values.reshape(-1)

        b_inds = np.arange(args.batch_size)
        for epoch in range(args.update_epochs):
            np.random.shuffle(b_inds)
            for start in range(0, args.batch_size, args.minibatch_size):
                end = start + args.minibatch_size
                mb_inds = b_inds[start:end]

                _, newlogprob, entropy, newvalue = agent.get_action_and_value(b_obs[mb_inds], b_actions[mb_inds])
                logratio = newlogprob - b_logprobs[mb_inds]
                ratio = logratio.exp()

                mb_advantages = b_advantages[mb_inds]
                if args.norm_adv:
                    mb_advantages = (mb_advantages - mb_advantages.mean()) / (mb_advantages.std() + 1e-8)

                # PPO clipped surrogate objective.
                # We MAXIMISE the surrogate, so we minimise its negative.
                # pg_loss1: unclipped policy-gradient term (ratio * advantage).
                # pg_loss2: ratio clipped to [1-eps, 1+eps] * advantage (pessimistic bound).
                # Taking the element-wise max of the two negatives implements the
                # min over the unclipped/clipped objective from the PPO paper.
                pg_loss1 = -mb_advantages * ratio
                pg_loss2 = -mb_advantages * torch.clamp(ratio, 1 - args.clip_coef, 1 + args.clip_coef)
                pg_loss = torch.max(pg_loss1, pg_loss2).mean()

                # Value loss
                newvalue = newvalue.view(-1)
                # Optionally clip the value function update the same way the policy
                # is clipped (limits how far V can move per update); otherwise plain MSE.
                if args.clip_vloss:
                    v_loss_unclipped = (newvalue - b_returns[mb_inds]) ** 2
                    v_clipped = b_values[mb_inds] + torch.clamp(
                        newvalue - b_values[mb_inds], -args.clip_coef, args.clip_coef
                    )
                    v_loss_clipped = (v_clipped - b_returns[mb_inds]) ** 2
                    v_loss_max = torch.max(v_loss_unclipped, v_loss_clipped)
                    v_loss = 0.5 * v_loss_max.mean()
                else:
                    v_loss = 0.5 * ((newvalue - b_returns[mb_inds]) ** 2).mean()

                entropy_loss = entropy.mean()
                loss = pg_loss - args.ent_coef * entropy_loss + v_loss * args.vf_coef

                optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(agent.parameters(), args.max_grad_norm)
                optimizer.step()
        
        # PRINT METRICS 
        sps = int(global_step / (time.time() - start_time))
        print("---------------------------------------")
        print(f"| rollout/                |           |")
        print(f"|    ep_len_mean          | {np.mean(episode_lengths) if episode_lengths else 0:.2f}")
        print(f"|    ep_rew_mean          | {np.mean(episode_returns) if episode_returns else 0:.2f}")
        print(f"| time/                   |           |")
        print(f"|    fps                  | {sps}")
        print(f"|    iterations           | {update}/{num_updates}")
        print(f"|    time_elapsed         | {int(time.time() - start_time)}")
        print(f"|    total_timesteps      | {global_step}")
        print(f"| train/                  |           |")
        print(f"|    entropy_loss         | {entropy_loss.item():.4f}")
        print(f"|    learning_rate        | {optimizer.param_groups[0]['lr']:.6f}")
        print(f"|    policy_loss          | {pg_loss.item():.4f}")
        print(f"|    value_loss           | {v_loss.item():.4f}")
        print("---------------------------------------")

    # Save model
    model_path = f"runs/{run_name}/{args.exp_name}.cleanrl_model"
    torch.save(agent.state_dict(), model_path)
    print(f"Model saved to {model_path}")

    envs.close()
    writer.close()

    # Plotting learning curve
    if len(history_returns) > 0:
        plt.figure(figsize=(10, 5))
        plt.plot(history_steps, history_returns, alpha=0.3, color='blue', label='Raw Return')
        if len(history_returns) > 10:
            sma = np.convolve(history_returns, np.ones(10)/10, mode='valid')
            plt.plot(history_steps[9:], sma, color='red', label='SMA 10')
        plt.xlabel("Global Step")
        plt.ylabel("Episodic Return")
        plt.title(f"{args.env_id} - PPO Training Curve")
        plt.legend()
        plt.grid(True)
        plot_path = f"runs/{run_name}/{args.exp_name}_learning_curve.png"
        plt.savefig(plot_path)
        print(f"Learning curve saved to {plot_path}")

        # study note: also drop a copy into the lab's results/ folder for the report
        results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
        os.makedirs(results_dir, exist_ok=True)
        results_plot_path = os.path.join(results_dir, "ppo_learning_curve.png")
        plt.savefig(results_plot_path)
        print(f"Learning curve also saved to {results_plot_path}")
        # plt.show()  # disabled: Agg backend is headless



