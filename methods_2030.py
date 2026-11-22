"""Seat changes from the 2020 apportionment under each method, for the central 2030
projection (2020-25 average growth carried forward to 1 April 2030)."""
import numpy as np, pandas as pd
from apportion import METHODS, load_2020, load_estimates
a20 = load_2020(); e = load_estimates().loc[a20.index]
overseas = a20["pop"] - e["ESTIMATESBASE2020"]
g = np.mean([np.log(e[f"POPESTIMATE{y}"] / e[f"POPESTIMATE{y-1}"]) for y in range(2021, 2026)], axis=0)
pop = np.exp(np.log(e["POPESTIMATE2025"].astype(float)) + 4.75 * g) + overseas
pop = dict(zip(a20.index, pop))
t = pd.DataFrame({m: f(pop) for m, f in METHODS.items()}).sub(a20["seats"], axis=0)
t = t[(t != 0).any(axis=1)].sort_values(["Huntington-Hill", "Webster"])
t.to_csv("out_2030_all_methods.csv"); print(t.to_string())
