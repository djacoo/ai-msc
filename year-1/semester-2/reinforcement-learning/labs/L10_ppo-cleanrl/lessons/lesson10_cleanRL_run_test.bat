@echo off
echo ==============================================
echo Running CleanRL PPO Test
echo ==============================================

REM Set the environment ID
set ENV_ID=CartPole-v1

REM IMPORTANT: Replace the path below with the actual path to your trained model
REM Example: runs\CartPole-v1__ppo_cleanRL_solution__1__1684594234\ppo_cleanRL_solution.cleanrl_model
set MODEL_PATH="runs/CartPole-v1__ppo_cleanRL_solution__1__1779540671/ppo_cleanRL_solution.cleanrl_model"

echo Testing on %ENV_ID% with model %MODEL_PATH%
echo.

python test.py --env-id %ENV_ID% --model-path %MODEL_PATH%

pause
