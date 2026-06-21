# QMIX / VDN Extension Stub

## Status

Not implemented. The current learner is tabular Independent Q-Learning. The centralized training trace is deliberate CTDE scaffolding, not a mixer and not evidence that CTDE improved performance.

## Why it is deferred

Standard VDN and QMIX factor a shared cooperative team value and rely on the Individual-Global-Max (IGM) relationship. This project is a competitive cop-versus-thief POSG with opposing terminal rewards. Applying a cooperative mixer without first defining and defending the competitive objective would create an impressive-looking but theoretically misleading result.

## Proposed interface

A future `marl/vdn.py` or `marl/qmix.py` trainer may consume only `CentralizedTransition` records during training. It may use global state and joint actions in a centralized critic/mixer, but exported role policies must retain the current `BaseAgent.act(LocalObservation)` contract. No global coordinates may enter an execution checkpoint.

## Acceptance gates

1. Freeze the zero-sum/general-sum objective and explain how it relates to IGM.
2. Unit-test additive VDN or monotonic QMIX mixing and controlled argmax consistency.
3. Add an execution leakage test proving loaded policies accept local observations only.
4. Compare against IQL on identical disjoint seeds, grids, opponents, and budgets.
5. Report instability and negative results; do not claim convergence from smoothed training curves.
