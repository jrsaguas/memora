# MEMORA experiments

Experiments are reproducible measurement programs, not production data.

## Scaling study

Run the compactness benchmark with:

```powershell
python -m experiments.benchmark --sizes 10 100 1000 5000 10000 --chats 10
```

Redirect the JSON output locally if desired:

```powershell
python -m experiments.benchmark --sizes 10 100 1000 5000 10000 --chats 10 > experiments/results/scaling.json
```

Generated result files are intentionally ignored by Git. Keep only methodology and interpretation in the repository unless a result is selected as a reproducibility artifact.

## Interpretation

The central comparison is not simply database size. Inspect:

1. concept/message ratio as message count increases;
2. edge/message ratio;
3. cross-chat recovery;
4. reconstruction size;
5. storage bytes per source byte;
6. whether the number of concept nodes stabilizes around the reusable vocabulary instead of tracking every unique token.

A favorable result for the current hypothesis would show that unique fragments continue to live primarily in message/term storage while reusable vocabulary provides a bounded or slowly growing graph of shared concepts, without losing cross-chat retrieval.

This experiment does **not** prove sublinear storage. It only measures the behavior of this implementation under a controlled workload.
