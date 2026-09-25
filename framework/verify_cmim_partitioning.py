"""
Checks on the number-partitioning data released with
Al-Kayed et al., "Programmable 200 GOPS Hopfield-inspired photonic Ising machine", Nature 648 (2025).

  git clone https://github.com/Shastri-Lab/tfln-ising-nature-paper-2025.git cmim
  pip install h5py numpy
  python3 verify_cmim_partitioning.py cmim/Figure_Data/Figure_05

Public domain.
"""
import sys, time
import h5py
import numpy as np

root = sys.argv[1] if len(sys.argv) > 1 else "."
rng = np.random.default_rng(0)

def ground_state_configs(s):
    """Exact number of spin configurations with residue 0 (subset-sum DP)."""
    T = int(sum(s))
    if T % 2:
        return 0
    dp = [0] * (T + 1); dp[0] = 1
    for x in s:
        for t in range(T, x - 1, -1):
            dp[t] += dp[t - x]
    return dp[T // 2]

for N in (64, 128, 256):
    h = h5py.File(f"{root}/{N}spins.mat", "r")
    s = np.array(h["nset1"]).ravel().astype(np.int64)
    sv = np.array(h["spin_vector"])
    if sv.shape[0] != N:
        sv = sv.T
    g = ground_state_configs(list(s))
    res = np.abs(s @ np.sign(sv))
    first = int(np.argmax(res == 0)) if (res == 0).any() else None
    print(f"N={N}: integers {s.min()}..{s.max()}, sum {s.sum()}, "
          f"ground-state configurations {g:.3e} = {g / 2**N:.2%} of all 2^N; "
          f"first residue-0 iteration {first}; final residue {res[-1]}")

# random guessing baseline on the 256-spin instance
s = np.array(h5py.File(f"{root}/256spins.mat", "r")["nset1"]).ravel().astype(np.int64)
B = rng.choice(np.array([-1, 1], dtype=np.int64), (200_000, len(s)))
print(f"uniform random guess success rate: {np.mean(B @ s == 0):.2%}")
times = []
for _ in range(100):
    t = time.perf_counter()
    while not np.any(rng.choice(np.array([-1, 1], dtype=np.int64), (1024, len(s))) @ s == 0):
        pass
    times.append(time.perf_counter() - t)
print(f"random guessing, median wall time to a ground state: {np.median(times)*1e3:.2f} ms (unoptimized NumPy)")

# how often do random instances with the stated range (0..16) have a unique perfect partition?
for N in (8, 16, 32):
    u = sum(ground_state_configs(list(rng.integers(0, 17, N))) == 2 for _ in range(5000))
    print(f"N={N}, integers 0..16: unique-solution instances {u}/5000")

# the Fig. 5b fit, TTS = A exp(bN) + C
A, b, C = 0.300057, 0.018509, -0.469471
print(f"fit crosses zero at N = {np.log(-C / A) / b:.1f}; predicted TTS at N=16: {A*np.exp(b*16)+C:.3f} s")
