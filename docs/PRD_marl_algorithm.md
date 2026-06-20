# PRD - MARL Algorithms

## 1. Purpose

Define the theoretical model, baseline learners, scoped CTDE approach, evaluation protocol, and honest limitations for partially observable competitive pursuit-evasion.

## 2. Formal models

### Required Dec-POMDP tuple

The course tuple is:

\[
\langle N, S, A, T, R, \Omega, O, \gamma \rangle
\]

- `N={cop, thief}` is the agent set.
- `S` is the global state: exact positions, barriers, move count, and terminal metadata.
- `A=A_cop x A_thief` is the joint action space; cop also has parameterized barrier placement.
- `T(s' | s, a)` is the deterministic transition under v1 rules (a degenerate probability distribution).
- `R(s,a)` is a shared scalar only for a cooperative approximation/training experiment; it is not the most faithful game payoff.
- `Omega=Omega_cop x Omega_thief` contains local observation spaces.
- `O(o | s',a)` deterministically maps state to radius-limited observations.
- `gamma in [0,1]` discounts future training reward.

An execution history is `h_i,t=(o_i,0,a_i,0,...,o_i,t)`, and a decentralized policy is `pi_i(a_i | h_i)`.

### POSG distinction

The binding game is better represented as:

\[
G=\langle I,S,{A_i},{O_i},P,\Omega,{R_i},\gamma\rangle
\]

because cop and thief have separate, conflicting reward functions `R_cop` and `R_thief`. A cop capture benefits the cop while survival benefits the thief. Therefore, cooperative VDN/QMIX guarantees do not transfer automatically. The project will label any shared-objective/value-factorization variant as a **simplified CTDE experiment**, not as a general POSG solution or Nash-equilibrium method.

## 3. Why MARL is harder than single-agent RL

Each learner changes its policy while the other learns, so from either agent's perspective transition/reward targets drift: the environment is non-stationary. Partial observations create perceptual aliasing, joint actions grow combinatorially, exploration depends on the opponent, credit assignment is ambiguous, and evaluation must separate genuine strategy from exploitation of one opponent/seed.

For IQL agent `i`, a target such as `y_i = r_i + gamma max_a' Q_i(o_i',a')` assumes a stable transition distribution. Opponent policy updates violate that assumption, causing replay staleness, oscillation, and possible failure to converge.

## 4. Information boundary and CTDE

Centralized Training, Decentralized Execution separates two phases:

- **Training:** the trainer may consume global state, joint actions, both rewards, availability masks, and local histories from centralized replay.
- **Execution:** each exported policy receives only its own local observation/history and action mask. It has no global state, opponent observation, centralized mixer, or inter-policy gradient channel.

Types, package dependencies, and negative tests enforce this boundary. GUI access to read-only global snapshots is presentation telemetry and must never feed a policy.

## 5. Baselines

### Non-learning controls

- Uniform legal random policy, seeded.
- Heuristic cop that minimizes visible/last-known distance without privileged state.
- Heuristic thief that maximizes visible/last-known distance and avoids traps/barriers without privileged state.

### Independent Q-Learning (IQL)

Each agent has its own Q-network/target network, optimizer, exploration schedule, and local transition view. Replay may be separated or centrally collected but samples expose only permitted per-agent fields to each learner. IQL is required as the non-stationary baseline, not assumed to converge.

## 6. Scoped CTDE approach

### VDN first

For a cooperative/shared-training objective, VDN assumes:

\[
Q_{tot}(h,a)=Q_{cop}(h_{cop},a_{cop})+Q_{thief}(h_{thief},a_{thief})
\]

This additive factorization satisfies the Individual-Global-Max (IGM) consistency condition: greedy local choices compose into a greedy joint action for `Q_tot`. It is simple enough to test the CTDE plumbing.

For this competitive POSG, the implementation gate must choose and document one exact experiment, for example separate role-conditioned team objectives or a zero-sum centralized critic with decentralized role policies. It must not claim VDN solves the general-sum game. Results must be compared empirically with IQL.

### Optional QMIX

QMIX replaces addition with a global-state-conditioned mixing network constrained by `dQ_tot/dQ_i >= 0`. It is more expressive than VDN while preserving IGM, but monotonicity cannot represent every useful joint value function. It can suffer **lossy decomposition**, especially where optimal joint action ranking depends on non-monotonic interactions. QPLEX, Weighted QMIX, QTRAN, or MAPPO are future alternatives, not version-1 requirements.

## 7. Optional recurrent memory

LSTM or GRU can summarize local history to reduce observation aliasing. This is optional. If added, recurrent state must reset at episode boundaries, truncated sequences need burn-in/masks, hidden state must remain agent-local at execution, and an ablation against feed-forward policies must justify complexity. GRU is the smaller initial candidate; LSTM may model longer dependencies.

OLoRA is documented as an advanced option only. It is neither necessary for small Q-networks nor claimed implemented.

## 8. Data and training contract

A joint replay record may contain `(state, local_histories, joint_action, rewards, next_state, next_local_histories, terminated, action_masks, episode_id, timestep)`. Global fields are read only by training components. Dataset sources may include seeded self-play and heuristic rollouts; train/evaluation seeds must be disjoint.

All hyperparameters live in `config/training.yaml`, including algorithm, episodes, batch size, replay capacity, learning rate, gamma, target update, epsilon schedule, hidden size, sequence length, evaluation interval, seeds, and checkpoint policy. Training is local. Checkpoints include schema/config/code version metadata and load in inference/eval mode.

Reward shaping may aid learning but must preserve and separately report authoritative match scores. Shaped terms, scale, and potential policy must be explicit; no post-hoc changes during evaluation.

## 9. Metrics and experimental protocol

Required per role and aggregate metrics:

- win/capture/survival rate;
- mean and distribution of moves to capture;
- undiscounted episodic training return and authoritative score;
- Q/TD loss and gradient norm;
- exploration rate and invalid-action rate;
- wall-clock training/inference time and sample count;
- performance against random and heuristic opponents;
- generalization across held-out seeds and at least the staged grid sizes `2x2`, `3x3`, `4x4`, `5x5` where valid.

Report mean plus standard deviation or a confidence interval over multiple seeds. Use the same evaluation episodes for every policy checkpoint, disable exploration, and never select the final model on the test seeds. Learning curves must include axis labels, algorithm, grid/config, seed aggregation, and smoothing details.

## 10. Acceptance criteria

- **MARL-AC-1:** A formal mapping for every Dec-POMDP tuple member and POSG reward distinction appears in docs and code-level schemas.
- **MARL-AC-2:** Automated tests prove policies cannot receive global state at execution.
- **MARL-AC-3:** Seeded random and heuristic baselines are reproducible and reported before learned results.
- **MARL-AC-4:** IQL target/update tests pass and at least one tiny environment demonstrates a measurable learning signal.
- **MARL-AC-5:** Centralized replay and VDN use global/joint information only in training; exported policy inference needs local data only.
- **MARL-AC-6:** VDN additive/IGM behavior is tested; if QMIX exists, mixer monotonic gradients and IGM are tested.
- **MARL-AC-7:** IQL and CTDE are evaluated on identical held-out seeds and metrics with uncertainty; no fabricated or single-run conclusion.
- **MARL-AC-8:** Recurrent memory, QMIX, and OLoRA remain labeled optional until tests, ablations, and artifacts exist.

## 11. Known risks and limitations

- Cooperative value decomposition is theoretically mismatched with opposing rewards; exact formulation requires review.
- Independent self-play may cycle or overfit one opponent population.
- Small grids can create deceptive high win rates and weak generalization.
- Replay data becomes stale as opponent policies change.
- Score asymmetry is an assignment rule, not necessarily a dense learning reward.
- Compute/time may make multi-seed deep experiments infeasible; a tabular/small-network baseline is preferable to unsupported sophistication.

## 12. Alternatives considered

Pure IQL is simple but retains non-stationarity. QMIX is more expressive but more complex and still monotonic/cooperative. MAPPO or centralized actor-critic better supports mixed cooperative-competitive settings, but expands scope. The version-1 plan therefore uses IQL plus a clearly labeled VDN CTDE comparison, with stronger methods reserved for final-project extension.
