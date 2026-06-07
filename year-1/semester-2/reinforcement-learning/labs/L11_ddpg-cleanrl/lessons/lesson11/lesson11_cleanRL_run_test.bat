@echo off
echo ==============================================
echo Running CleanRL DDPG Test
echo ==============================================

REM Set the environment ID
set ENV_ID=Pendulum-v1 

REM OTHER ENVIRONMENTS: Pendulum-v1 MountainCarContinuous-v0 BipedalWalker-v3
REM IMPORTANT: Replace the path below with the actual path to your trained model
set MODEL_PATH="ddpg_Pendulum-v1_actor.pth"

echo Testing on %ENV_ID% with model %MODEL_PATH%
echo.

python test.py --env-id %ENV_ID% --model-path %MODEL_PATH%

pause
