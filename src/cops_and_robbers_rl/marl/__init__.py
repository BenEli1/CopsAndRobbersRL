"""Submission-safe tabular MARL training components."""

from cops_and_robbers_rl.marl.iql import IQLAgent, encode_observation
from cops_and_robbers_rl.marl.trainer import IQLTrainer, TrainingConfig

__all__ = ["IQLAgent", "IQLTrainer", "TrainingConfig", "encode_observation"]
