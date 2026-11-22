"""House apportionment under five methods: 2020 Census check, then 2030 projections.

Methods (each state gets at least one seat, as the Constitution requires):
  Huntington-Hill (equal proportions; current law since 1941), Webster (Sainte-Lague),
  Jefferson (D'Hondt), Adams, Hamilton (largest remainders, with the one-seat floor).
"""
import math
import numpy as np
import pandas as pd

H = 435


def divisor_method(pop, rounding_point, seats=H):
    """Priority-value form of a divisor method. rounding_point(n) is where a state holding n
    seats crosses to n+1: geometric mean (HH), n + 0.5 (Webster), n + 1 (Jefferson), n (Adams)."""
    n = {s: 1 for s in pop}
    for _ in range(seats - len(pop)):
        best = max(pop, key=lambda s: (pop[s] / rounding_point(n[s]) if rounding_point(n[s]) > 0
                                       else math.inf, s))
        n[best] += 1
    return n


def huntington_hill(pop, seats=H):
    return divisor_method(pop, lambda k: math.sqrt(k * (k + 1)), seats)


def webster(pop, seats=H):
    return divisor_method(pop, lambda k: k + 0.5, seats)


def jefferson(pop, seats=H):
    return divisor_method(pop, lambda k: k + 1.0, seats)


def adams(pop, seats=H):
    # Adams gives a state its first seat at any population; the one-seat floor is built in,
    # so the next seat is decided at the divisor equal to the seats already held.
    return divisor_method(pop, lambda k: float(k), seats)


def dean(pop, seats=H):
    return divisor_method(pop, lambda k: k * (k + 1) / (k + 0.5), seats)


def hamilton(pop, seats=H):
    total = sum(pop.values())
    quota = {s: seats * p / total for s, p in pop.items()}
    n = {s: max(1, math.floor(q)) for s, q in quota.items()}
    rest = seats - sum(n.values())
    order = sorted(pop, key=lambda s: (quota[s] - n[s], s), reverse=True)  # remainder over seats held
    for s in order[:rest]:
        n[s] += 1
    return n


METHODS = {"Huntington-Hill": huntington_hill, "Webster": webster, "Jefferson": jefferson,
           "Adams": adams, "Dean": dean, "Hamilton": hamilton}


def load_2020():
    d = pd.read_excel("data/apportionment-2020-table01.xlsx", header=None, skiprows=4, nrows=50)
    d = d.iloc[:, :3]
    d.columns = ["state", "pop", "seats"]
    return d.set_index("state")


def load_estimates():
    e = pd.read_csv("data/NST-EST2025-ALLDATA.csv", encoding="latin-1")
    e = e[(e.SUMLEV == 40) & (e.NAME != "District of Columbia") & (e.NAME != "Puerto Rico")]
    return e.set_index("NAME")


if __name__ == "__main__":
    a20 = load_2020()
    pop20 = a20["pop"].to_dict()
    hh = huntington_hill(pop20)
    mism = {s: (hh[s], a20.seats[s]) for s in pop20 if hh[s] != a20.seats[s]}
    print("Huntington-Hill reproduces the official 2020 apportionment:", not mism, mism or "")
    table = pd.DataFrame({m: f(pop20) for m, f in METHODS.items()})
    diff = table.sub(table["Huntington-Hill"], axis=0)
    changed = diff[(diff != 0).any(axis=1)]
    print("\n2020 counts: seats that differ from Huntington-Hill under each method")
    print(changed.to_string())
    table.to_csv("out_2020_all_methods.csv")


def project_2030(n_sims=20000, seed=1):
    """Project apportionment populations to 1 April 2030 from the Census Bureau's Vintage 2025
    estimates. Each simulation draws the growth of every future year (mid-2025 to April 2030)
    from one of the observed years 2021-2025, the same year for all states, so the national
    pattern of each year (e.g. the 2022-2024 rise in international migration) is kept together.
    Overseas federal personnel are carried at their 2020 counts."""
    a20 = load_2020()
    e = load_estimates().loc[a20.index]
    overseas = a20["pop"] - e["ESTIMATESBASE2020"]
    years = [2021, 2022, 2023, 2024, 2025]
    growth = np.log(np.array([e[f"POPESTIMATE{y}"] / e[f"POPESTIMATE{y - 1}"] for y in years]))  # (5, 50)
    base = np.log(e["POPESTIMATE2025"].to_numpy(float))
    horizon = 4.75                                     # 1 July 2025 -> 1 April 2030
    rng = np.random.default_rng(seed)
    states = list(a20.index)
    seats20 = a20["seats"].to_numpy()
    counts = np.zeros((n_sims, 50), int)
    for k in range(n_sims):
        idx = rng.integers(0, len(years), size=5)
        g = growth[idx]                                # (5, 50): years 2026..2030
        total = g[:4].sum(axis=0) + 0.75 * g[4]
        pop = np.exp(base + total) + overseas.to_numpy()
        hh = huntington_hill(dict(zip(states, pop)))
        counts[k] = [hh[s] for s in states]
    change = counts - seats20
    trend = {}
    for name, yrs in {"2020-25 trend": years, "2023-25 trend": [2024, 2025]}.items():
        g = growth[[years.index(y) for y in yrs]].mean(axis=0)
        pop = np.exp(base + horizon * g) + overseas.to_numpy()
        hh = huntington_hill(dict(zip(states, pop)))
        trend[name] = np.array([hh[s] for s in states]) - seats20
    res = pd.DataFrame({"seats_2020": seats20,
                        "P(gain)": (change > 0).mean(0), "P(lose)": (change < 0).mean(0),
                        "median_change": np.median(change, 0).astype(int),
                        **{f"{k} change": v for k, v in trend.items()}}, index=states)
    return res, counts


if __name__ == "__main__":
    res, counts = project_2030()
    res.to_csv("out_2030_projection.csv")
    show = res[(res["P(gain)"] > 0.05) | (res["P(lose)"] > 0.05)].sort_values("median_change")
    print("\n2030 projection under current law (Huntington-Hill), 20,000 simulations")
    print(show.round(3).to_string())
