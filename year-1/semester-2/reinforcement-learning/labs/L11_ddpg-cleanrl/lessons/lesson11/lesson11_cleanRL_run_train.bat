@echo off
setlocal enabledelayedexpansion

REM Setup Environments list
set ENVS=Pendulum-v1 


REM OTHER ENVIRONMENTS: Pendulum-v1 MountainCarContinuous-v0 BipedalWalker-v3

echo Running CleanRL DDPG training on multiple environments...
for %%E in (%ENVS%) do (
    echo.
    echo ==============================================
    echo Training on %%E
    echo ==============================================
    python lesson11_cleanRL_ddpg_cleanRL_train_code.py --env-id %%E --total-timesteps 50000
)

echo All environments trained via CleanRL Solution script!
pause
