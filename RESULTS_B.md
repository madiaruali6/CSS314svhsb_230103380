# RESULTS_B — Variant B (Scalability Diagnostics)

> **Measurement environment:** sandbox with **1 CPU** (`os.cpu_count() == 1`), Python 3.12.3.
> With a single core, real parallel speedup is impossible, so every e(p) ≈ 1 (≈ no speedup).
> **Re-run the three scripts on a multi-core machine and replace the "[your machine]" row before submitting.**

e(p) = ((p·Tp/T1) − 1) / (p − 1)

## Measured (sandbox, 1 CPU)

| Configuration | T1 (s) | T2 (s) | T4 (s) | T8 (s) | S8 | e(2) | e(8) | Verdict |
|---|---|---|---|---|---|---|---|---|
| A: Micro (k=1), N=200k | 6.932 | 6.528 | 5.884 | 6.284 | 1.10 | 0.883 | 0.893 | Dispatch/pickle overhead dominates (~5x slower than coarse at P=1) |
| A: Coarse (k=10000), N=200k | 1.345 | 1.362 | 1.372 | 1.398 | 0.96 | 1.025 | 1.046 | No speedup — only 1 core available |
| B: Queue Choke, N=400k | 2.797 | 2.665 | 2.626 | 2.743 | 1.02 | 0.905 | 0.978 | Per-item put/get cost ~7 µs, bound by consumer; no scaling |
| C: Buffered Batch, N=10M | 0.597 | 0.608 | 0.596 | 0.623 | 0.96 | 1.036 | 1.050 | IPC cost removed; 10M items in 0.6 s |

## Measured on [your machine] — fill in

| Configuration | T1 | T2 | T4 | T8 | S8 | e(2) | e(8) |
|---|---|---|---|---|---|---|---|
| A: Micro (k=1) | | | | | | | |
| A: Coarse (k=10000) | | | | | | | |
| B: Queue Choke | | | | | | | |
| C: Buffered Batch | | | | | | | |

## Observations

- **Exp A:** with chunksize=1 every number is pickled and sent as its own task; at P=1 the fine run was ~5x slower than the coarse run for identical work (6.9 s vs 1.3 s), which is pure dispatch overhead. On a multi-core machine the master becomes the serial bottleneck, so e(p) stays high for fine chunks and near 0 for coarse ones.
- **Exp B:** every item crosses the pipe, so the single consumer (`q.get()`) and the pipe lock cap throughput (~145k items/s here) regardless of P. Extra producers only add contention. The handout's expected T8 > T1 is not guaranteed on every OS/CPU; the reliable finding is that e(p) stays high and speedup stays ≈ 1 or below.
- **Exp C:** one `put` per 10,000 items cuts queue operations by 10,000x. 25x more data (10M vs 400k) ran ~4.7x faster in absolute time. Per-item throughput rose from ~0.14M/s to ~16.7M/s (~117x). Near-linear speedup (S8 > 5, e(8) < 0.05) needs ≥ 8 physical cores.
- **Note:** each worker restarts `i` at 0, so the checksum differs slightly for different P (e.g. 29999994 at P=1 vs 29999990 at P=2); this is expected, not a bug.
