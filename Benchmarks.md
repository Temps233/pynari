# Pynarist Benchmarks

You can find the benchmark source code in `benchmark.py`.

By running the bench, you may get results like this:

| Tool | Serialize Time | Deserialize Time | Size |
|------|-----------|-------------|------|
| Pynarist | **285.28 ms** | **443.49 ms** | **18** |
| Pickle | 281.46 ms | 246.86 ms | 137 |
| Binpi | 854.79 ms | 1035.09 ms | 17 |

Overall, Pynarist has a very small size and have a good performance, while pickle and binpi have problems about result sizes and performances.