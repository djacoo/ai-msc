# Lab 6 — TensorFlow & PyTorch: Neural Network Basics

## Topic & Theory Recap
A deep-learning primer covering the building blocks needed for Deep RL,
implemented **side by side in TensorFlow/Keras and PyTorch**:

1. **Gradient-based optimization.** Minimize `2x² + 2xy + 2y² − 6x` by gradient
   descent. TF uses `GradientTape` to record operations and `tape.gradient`;
   PyTorch uses `loss.backward()` + autograd. Both converge to the analytic
   minimum `(x, y) = (2, −1)`, value `−6`.
2. **Building a DNN.** A fully-connected network
   `input → ReLU(nNodes) → nLayer·ReLU(nNodes) → linear(nOutputs)`,
   built with `Sequential`/`Dense` in Keras and an `nn.Module` in PyTorch.
   The two are made bit-for-bit identical by copying Keras weights into the
   PyTorch layers (`set_same_weights`), so a forward pass returns the same value.
3. **A standard Deep-RL data loop.** Roll out random episodes in
   DangerousGridWorld, store transitions `[state, action, next_state, reward]`,
   then train the DNN to **regress the reward of a state** using MSE loss
   (Adam optimizer) in both frameworks.

## Files
- `lessons/lesson_6_code.py` — all 8 TODOs implemented (optimization, model
  construction, data collection, Keras & PyTorch training loops) and `main()`.
- `tools/DangerousGridWorld.py` — environment (do not modify).
- `results/lesson_6_results.txt` — saved console output of a successful run.

## How to Run
Run **from the `lessons/` directory** so the environment import resolves:

```bash
cd lessons
python lesson_6_code.py
```

Runs on CPU. Targets Keras 3 (TF 2.20) and PyTorch 2.8.

## Expected Results
- **Optimization:** both frameworks report `<x:2.0, y:-1.0>` with value `-6.0`.
- **Networks:** identical structure (Keras 4 Dense layers, 169 params; PyTorch
  `fc1, fc2, fc3, output`). After `set_same_weights`, the Keras and PyTorch
  forward passes of `-1.4` return the **same** number.
- **Reward prediction:** the random policy rarely reaches the goal/death cells,
  so the network learns the dominant step reward; after training both Keras and
  PyTorch predict ≈ **−0.08** for the queried states, in close agreement.
