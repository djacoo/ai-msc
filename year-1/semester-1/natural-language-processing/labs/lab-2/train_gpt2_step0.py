# File train_gpt2_step0.py: initial setup and imports for GPT model
# Main references in the literature:
# - GPT2 paper (Radford et al., Language Models are Unsupervised Multitask Learners, 2019): https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
# - GPT3 paper (Brown et al., Language Models are Few-Shot Learners, 2020): https://arxiv.org/pdf/2005.14165.pdf
# # -----------------------------------------------------------------------------
# # simple launch:
# # python train_gpt2_StepXX.py


from dataclasses import dataclass
import torch
import torch.nn as nn
from torch.nn import functional as F
import numpy as np
import math


# -----------------------------------------------------------------------------

# Legend
# T=block_size: max sequence length (length of each sequence) (block_size=1024 in GPT-2 124M)
# C=n_embd: embedding dimension (number of channels in the model) (n_embd=768 for GPT-2 124M)
# n_layer: number of transformer blocks (12 for GPT-2 124M)
# n_head: number of attention heads (12 in GPT-2 124M)
# vocab_size: size of the vocabulary (number of unique tokens) (50257 for GPT-2)
############################################################################################################


@dataclass
class GPTConfig:
    block_size: int = 256 # max sequence length (T) - 1024 in GPT-2 124M
    vocab_size: int = 65 # number of tokens in the dataset - 50257 for GPT-2
    n_layer: int = 6 # number of layers - 12 in GPT-2 124M
    n_head: int = 6 # number of heads - 12 in GPT-2 124M
    n_embd: int = 384 # embedding dimension - 768 in GPT-2 124M

class GPT(nn.Module):

    def __init__(self, config):
        super().__init__()
        self.config = config