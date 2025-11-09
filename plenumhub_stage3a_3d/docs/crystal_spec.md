# Texture & Time Crystal Economy (Stage 3d)

## Overview
Texture Crystals (TC) and Time Crystals (TiC) are internal "microcurrency" units used by PlenumHub
to budget entropy, prioritize mediation, and stabilize fork convergence. This specification gives
minting/burning rules, staking, and example parameters.

## Tokens
- **TC (Texture Crystal):** rewarded for structural work: completing modalities, reducing entropy via merges, contributing high-quality rule chains.
- **TiC (Time Crystal):** a decaying staking token representing temporal commitment; used for quorum weight and time-limited privileges.

## Earning TC
- Closing a missing modality (successful Media-Quine synthesis): +0.1 TC
- Resolving a merge that reduces entropy by ΔE > 0: +1 * floor(10 * ΔE) TC
- Executing a valid pop step that is later accepted: +0.05 TC per step
- Reviewing and validating a mediation candidate: +0.02 TC

## TiC Emission & Decay
- TiC emits proportionally to measured coherence over window Δt:
  r = base_rate * coherence(Δt)
- Decay model: TiC(t) = TiC0 * exp(-λ t) when not restaked or attached to active tasks.
- Example: λ = 0.01 per day.

## Merge Quorum & Crystal Stake
- To propose a merge with high-impact (entropy change > threshold), proposer must stake a minimum TC and TiC amount.
- Quorum weight is computed as:
  weight(node) = f(TC_balance, TiC_attached, reputation_score)
- Higher stake increases probability that mediation search budgets are allocated in favor of the staker's candidate, but does NOT guarantee acceptance; entropy constraints are mandatory.

## Entropy Pricing
- Every rule r carries an explicit entropy budget ε_r and a **price** p_r in TC:
  p_r = α * ε_r
  where α is a global market parameter (e.g., α = 10 TC per entropy unit).
- Network enforces rate limits: each identity can expend at most B TC per epoch on entropy spending; this prevents entropy flooding attacks.

## Mint & Burn
- Minting:
  - TC minted as rewards, subject to global supply caps or algorithmic sinks.
  - TiC minted by time-locked staking of TC or other reputation-backed assets.
- Burning:
  - TC used to pay for mediation search and merge fees are burned to create deflationary pressure.
  - TiC decays naturally when unstaked.

## Anti-Sybil & Reputation
- Crystal issuance is tied to contribution graphs: new identities have reduced initial minting rates.
- Reputation score is derived from provenance quality, historical entropy reductions, and peer validations.

## Example Parameters (suggested)
- α = 10 TC / entropy-unit
- Merge threshold for staking: ΔE_threshold = 0.5
- Minimum stake for high-impact merge: 10 TC + 1 TiC
- Base TiC emission rate: 0.1 TiC/day * coherence(Δt)
- Decay λ = 0.01 / day

## Pseudocode snippets

```
function price_for_rule(eps):
    return alpha * eps

function propose_merge(proposer, sigma_a, sigma_b, candidate):
    deltaE = sigma_before.entropy - candidate.entropy
    required_stake = if deltaE > big_threshold then large_stake else small_stake
    if proposer.TC < required_stake.TC or proposer.TiC < required_stake.TiC:
        raise "insufficient stake"
    lock_stake(proposer, required_stake)
    enqueue_mediation(candidate, proposer)
```

## Security notes
- Entropy budgets are cryptographically signed in proofs to prevent forgery.
- Synthesis transducers used by Q must be allowed/permitted and recorded in the consensus registry.
- All stake and reward operations emit proofs that are included in sphere provenance.
