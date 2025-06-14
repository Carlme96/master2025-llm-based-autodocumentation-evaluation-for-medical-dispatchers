# Qwen1.5-4B Fine-Tuning with Unsloth

This repository fine-tunes the [Qwen3-4B](https://huggingface.co/unsloth/Qwen3-4B-unsloth-bnb-4bit) model using [Unsloth](https://github.com/unslothai/unsloth), leveraging **BitsAndBytes (4-bit quantization)** and **LoRA** adapters at **rank 8** and **rank 16** for efficient training.

## Overview

This setup is optimized for lightweight, memory-efficient fine-tuning on consumer GPUs using LoRA. It supports:

- 4-bit quantized training with BitsAndBytes
- LoRA adapters (rank 8 and 16)
- Unsloth backend for speed and stability

## Model

| Model              | Quantization | LoRA Rank |
|-------------------|--------------|-----------|
| Qwen1.5-4B         | 4-bit        | 8 & 16    |


