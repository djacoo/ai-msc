@echo off
setlocal enabledelayedexpansion

REM Setup Environments list
set ENVS=CartPole-v1 

REM OTHER ENVIRONMENTS: CartPole-v1 LunarLander-v2 Acrobot-v1 MountainCar-v0 MountainCarContinuous-v0 Pendulum-v1 BipedalWalker-v3

echo Running CleanRL PPO training on multiple environments...
for %%E in (%ENVS%) do (
    echo.
    echo ==============================================
    echo Training on %%E
    echo ==============================================
    python ppo_cleanRL_solution.py --env-id %%E --total-timesteps 50000
)

echo All environments trained via CleanRL Solution script!
pause
