# House Apportionment under Alternative Methods

Noah Parsons, as of 21 November 2026

## Question

How much does the choice of apportionment method change the House, both for the 2020 Census and for the 2030 apportionment now in prospect? And how certain are the 2030 changes?

## Data

- **2020:** apportionment populations and seats, U.S. Census Bureau, 2020 Census Apportionment Results, Table 1 (`data/apportionment-2020-table01.xlsx`).
- **2030 projection:** U.S. Census Bureau Vintage 2025 state population estimates (`data/NST-EST2025-ALLDATA.csv`).

## Methods (`apportion.py`)

Six methods, each giving every state at least one seat and allocating 435 seats:
- Huntington–Hill (equal proportions), current law since 1941;
- Webster (Sainte-Laguë);
- Jefferson (D'Hondt);
- Adams;
- Dean;
- Hamilton (largest remainders).

The divisor methods are written in their priority-value form.

**Check:** Huntington–Hill applied to the 2020 apportionment populations reproduces the official 2020 apportionment exactly, for all 50 states.

**2030 projection:** apportionment populations are projected to 1 April 2030 from the Vintage 2025 estimates. Each of 20,000 simulations draws every future year's growth from one of the observed years 2021 to 2025. The same year is drawn for all states, so each year's national pattern, such as the 2022 to 2024 rise in international migration, stays together. Overseas federal personnel are carried at their 2020 counts. Two deterministic trends (2020 to 2025, and 2023 to 2025) are given alongside.

## Results

### 2020: 21 states would hold a different number of seats under at least one other method (`out_2020_all_methods.csv`)

- **Webster and Hamilton each move two seats:** New York and Ohio gain one each, and Montana and Rhode Island lose one each.
- **Jefferson favours large states:** it moves 9 seats. California, New York and Texas each gain 2, and Florida, Ohio and Pennsylvania 1 each, at the expense of nine smaller states.
- **Adams favours small states:** it moves 5 seats. California loses 2 and Florida, Illinois and Texas 1 each, while Delaware, Idaho, South Dakota, Utah and West Virginia each gain one.
- **Dean differs from Huntington–Hill only in Idaho (+1) and Minnesota (−1).**

### 2030 under current law (`out_2030_projection.csv`, `fig_2030_seat_change.png`)

| Change | States (probability across 20,000 runs) |
|---|---|
| Gain | Texas +4, Florida +3 (in every run); Arizona, Idaho, North Carolina, Utah +1 (every run); Georgia +1 (98%) |
| Lose | California −4, New York −2; Illinois, Minnesota, Oregon, Pennsylvania, Rhode Island, Wisconsin −1 (every run) |
| Uncertain | Michigan loses a seat in 48% of runs; Tennessee gains one in 26% |

The two deterministic trends agree, except that New York loses one seat, not two, on the 2023 to 2025 trend and Florida gains two, not three.

### 2030 under the other methods (`out_2030_all_methods.csv`)

Under Jefferson, Texas would gain 6 and Florida 5. Under Adams, Texas would gain 3, Florida 2, and Georgia and North Carolina nothing.

## Limits

- **The projection simply carries recent growth forward.** It cannot foresee a change in migration, or the Census Bureau's own revisions to the estimates.
- **Overseas federal personnel are held at their 2020 counts.**
- **None of this is new mathematics.** These methods and their biases are well studied (Balinski and Young, *Fair Representation*). What this provides is open, checked code, a side-by-side table for 2020 and 2030, and a probability for each 2030 change, not just a single projection.

## Files

| File | Contents |
|---|---|
| `apportion.py` | The six methods, the 2020 check and the 2030 projection |
| `methods_2030.py` | All six methods applied to the central 2030 projection |
| `out_2020_all_methods.csv`, `out_2030_projection.csv`, `out_2030_all_methods.csv` | Results |
| `fig_2030_seat_change.png` | Figure |
| `data/` | Census Bureau source files |
