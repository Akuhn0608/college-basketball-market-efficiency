# Research Memo: College Basketball Market Efficiency

## Research Question

How accurately do closing NCAA men’s basketball moneylines reflect actual game outcomes, and do any market segments exhibit economically meaningful return patterns after sportsbook prices, risk, statistical uncertainty, and multiple testing are considered?

The current study analyzes the 2021–22 season and includes:

* market calibration and forecast-accuracy analysis
* favorite and underdog segmentation
* team-level expected-win analysis
* a Louisville basketball case study
* flat-stake backtesting
* risk and drawdown measurement
* bootstrap uncertainty estimation
* chronological and subgroup robustness testing
* game-clustered resampling
* multiple-testing adjustment

## Executive Summary

The closing moneyline market demonstrated meaningful predictive accuracy and was generally well calibrated across middle probability ranges.

The final dataset contained **5,342 valid games** and **10,684 team-game market observations**. Average sportsbook vig was **3.70%**. The market achieved a **0.1793 Brier score** and **0.5336 log loss**.

Broadly betting favorites or underdogs at listed closing prices produced negative returns:

* all favorites: **-1.84% ROI**
* all underdogs: **-13.17% ROI**
* visitor underdogs: **-16.48% ROI**

One segment—teams priced between 70% and 80% no-vig win probability—generated **4.77% flat-stake ROI** across **1,039 observations**.

The finding remained positive after:

* 5,000-sample bootstrap analysis
* chronological first-half and second-half evaluation
* home and visitor subgroup analysis
* monthly stability analysis
* resampling entire games as clusters
* Bonferroni adjustment for testing ten probability buckets

The multiple-testing-adjusted ROI interval was approximately **0.21% to 9.21%**.

This is a statistically interesting single-season anomaly, but it should not be interpreted as a persistent or tradable edge until it is validated on an independent season.

## Data

The analysis combines:

1. NCAA men’s basketball team and game-result data from the Kaggle March Machine Learning Mania dataset.
2. Historical closing moneylines and scores from the Sportsbook Review Online NCAA basketball archive.

The source odds archive originally contained approximately 5,481 games.

After:

* requiring complete moneylines
* mapping teams to NCAA identifiers
* excluding unmatched non-Division I teams
* removing invalid tied-score source records
* validating relational and probability integrity

the final market dataset contained **5,342 games**.

Each game contributed one market observation for the visitor and one for the home team, producing **10,684 team-game observations** for probability-bucket and return analysis.

Team-name normalization achieved **99.95% mapping coverage**. Three Chaminade games were excluded because the team was absent from the standard Division I team-ID dataset.

## Data Preparation

The odds archive recorded each game as two consecutive rows:

* one row for the visitor
* one row for the home team

The pipeline transformed these records into one row per game containing:

* game date
* visitor and home teams
* final scores
* visitor and home moneylines
* official NCAA team IDs
* game outcomes
* implied probabilities
* no-vig probabilities
* favorite and underdog classifications
* team-level pricing errors

Team names were standardized by:

* converting text to lowercase
* removing spaces and punctuation
* removing accent marks
* matching normalized source names to official NCAA names
* applying source-specific manual aliases where necessary

## Data-Quality Validation

The project includes automated checks for:

* duplicate game identifiers
* missing team IDs
* missing moneylines
* invalid or missing scores
* invalid outcome indicators
* probabilities outside the valid zero-to-one range
* no-vig probabilities that do not sum to one
* games without corresponding price records
* price records without corresponding games

The checks initially identified two games with tied final scores:

* SIUE at Youngstown State
* Southern Utah at Yale

Because NCAA games cannot end in ties, the records were treated as invalid source observations and removed at the cleaning stage. The full pipeline was then rebuilt.

All current automated checks pass.

## Relational Database and SQL Analysis

Cleaned data and analytical outputs are loaded into SQLite.

The relational structure includes tables for:

* teams
* games
* market prices
* Louisville case-study observations
* strategy-level backtests
* probability-bucket backtests
* bootstrap uncertainty
* chronological validation
* location validation
* monthly stability
* multiple-testing-adjusted results

SQL analysis uses:

* joins
* common table expressions
* `CASE WHEN`
* `GROUP BY`
* `UNION ALL`
* cumulative sums
* rolling-window calculations
* ranking
* team-level aggregation

This layer supports the Streamlit dashboard and separates data preparation from analytical presentation.

## Probability Conversion

American moneylines were converted into raw implied probabilities.

For positive odds:

```text
Implied probability = 100 / (odds + 100)
```

For negative odds:

```text
Implied probability = |odds| / (|odds| + 100)
```

Raw probabilities generally sum to more than 100% because sportsbooks include a margin.

## Vig Removal

For each two-team market:

```text
No-vig probability =
Team raw implied probability / Combined raw implied probability
```

The resulting visitor and home probabilities sum to 100%.

The dataset’s average sportsbook vig was **3.70%**.

## Forecast-Accuracy Metrics

### Brier Score

The Brier score measures the average squared difference between forecast probabilities and binary outcomes.

The 2021–22 Brier score was:

```text
0.1793
```

Lower values indicate more accurate probability forecasts.

### Log Loss

Log loss penalizes highly confident incorrect forecasts more severely than moderate errors.

The 2021–22 log loss was:

```text
0.5336
```

### Calibration

Calibration compares average predicted probability with actual win rate.

Selected results included:

| No-vig probability range | Observations | Average probability | Actual win rate |
| ------------------------ | -----------: | ------------------: | --------------: |
| 0%–10%                   |          528 |                7.5% |            3.6% |
| 10%–20%                  |        1,087 |               15.1% |           14.0% |
| 20%–30%                  |        1,039 |               25.3% |           19.2% |
| 30%–40%                  |        1,327 |               35.2% |           36.4% |
| 40%–50%                  |        1,425 |               44.9% |           45.2% |
| 50%–60%                  |        1,297 |               55.6% |           55.3% |
| 60%–70%                  |        1,327 |               64.8% |           63.6% |
| 70%–80%                  |        1,039 |               74.7% |           80.8% |
| 80%–90%                  |        1,087 |               84.9% |           86.0% |
| 90%–100%                 |          528 |               92.5% |           96.4% |

The middle ranges were generally close to their predicted probabilities. Larger differences appeared in some lower-probability and 70%–80% observations.

## Favorite and Underdog Segments

### Visitor Favorites

* observations: **1,566**
* average no-vig probability: **66.3%**
* actual win rate: **67.3%**
* average pricing error: **+1.0 percentage point**

### Visitor Underdogs

* observations: **3,776**
* average no-vig probability: **26.8%**
* actual win rate: **25.1%**
* average pricing error: **-1.7 percentage points**

### Home Favorites

* observations: **3,712**
* average no-vig probability: **73.6%**
* actual win rate: **75.2%**
* average pricing error: **+1.6 percentage points**

### Home Underdogs

* observations: **1,630**
* average no-vig probability: **34.4%**
* actual win rate: **33.6%**
* average pricing error: **-0.7 percentage points**

Favorites slightly outperformed their average no-vig expectations, while underdogs slightly underperformed.

These probability differences did not imply that broad favorite strategies were profitable at quoted prices.

## Backtesting Methodology

Each team-game observation was treated as a hypothetical one-unit wager at the listed closing American moneyline.

For a winning positive-moneyline wager:

```text
Profit = odds / 100
```

For a winning negative-moneyline wager:

```text
Profit = 100 / |odds|
```

A losing wager produced a net return of **-1 unit**.

The analysis measured:

* number of observations
* wins and losses
* hit rate
* total staked
* net profit
* ROI
* average return
* return volatility
* Sharpe-like return-to-volatility ratio
* maximum drawdown

## Broad Strategy Results

| Strategy          | Observations | Hit rate | Net profit |     ROI | Maximum drawdown |
| ----------------- | -----------: | -------: | ---------: | ------: | ---------------: |
| All favorites     |        5,278 |   72.85% |      -97.3 |  -1.84% |            130.7 |
| All underdogs     |        5,406 |   27.69% |     -712.0 | -13.17% |            740.6 |
| Home favorites    |        3,712 |   75.19% |      -66.1 |  -1.78% |            109.2 |
| Home underdogs    |        1,630 |   33.62% |      -89.6 |  -5.49% |            176.9 |
| Visitor favorites |        1,566 |   67.31% |      -31.2 |  -1.99% |             39.9 |
| Visitor underdogs |        3,776 |   25.13% |     -622.4 | -16.48% |            651.8 |

The sportsbook’s quoted prices and vig were sufficient to turn broad strategies negative despite reasonably accurate probabilities.

## Probability-Bucket Backtests

| Probability range | Observations |     ROI |
| ----------------- | -----------: | ------: |
| 0%–10%            |          528 | -55.85% |
| 10%–20%           |        1,087 |  -9.64% |
| 20%–30%           |        1,039 | -26.28% |
| 30%–40%           |        1,327 |  +0.50% |
| 40%–50%           |        1,425 |  -3.23% |
| 50%–60%           |        1,297 |  -4.25% |
| 60%–70%           |        1,327 |  -4.79% |
| 70%–80%           |        1,039 |  +4.77% |
| 80%–90%           |        1,087 |  -2.63% |
| 90%–100%          |          528 |  +0.09% |

The 70%–80% bucket produced the strongest positive result.

## Bootstrap Uncertainty

The project used 5,000 bootstrap samples to estimate uncertainty around ROI.

For the 70%–80% bucket:

* observed ROI: **4.77%**
* standard bootstrap lower bound: approximately **1.61%**
* standard bootstrap upper bound: approximately **7.77%**
* proportion of bootstrap samples above zero: approximately **99.9%**

Most broad strategy confidence intervals were either negative or crossed zero.

## Chronological Robustness

The 70%–80% bucket was split chronologically.

### Full Season

* observations: **1,039**
* ROI: **4.77%**
* 95% interval: approximately **1.65% to 7.68%**

### First Half

* observations: **519**
* ROI: **2.87%**
* 95% interval: approximately **-1.58% to 7.43%**
* interpretation: inconclusive

### Second Half

* observations: **520**
* ROI: **6.65%**
* 95% interval: approximately **2.27% to 10.74%**

The result did not disappear later in the season. The second-half estimate was stronger than the first-half estimate.

## Home and Visitor Robustness

### Home Observations

* observations: **748**
* ROI: **4.27%**
* 95% interval: approximately **0.52% to 7.87%**

### Visitor Observations

* observations: **291**
* ROI: **6.05%**
* 95% interval: approximately **-0.19% to 11.93%**

Home observations showed a positive interval, while the visitor interval narrowly crossed zero.

## Monthly Stability

| Month         | Observations |    ROI |
| ------------- | -----------: | -----: |
| November 2021 |          165 | -1.20% |
| December 2021 |          158 | +4.94% |
| January 2022  |          283 | +5.26% |
| February 2022 |          308 | +5.90% |
| March 2022    |          125 | +8.52% |

Four of five monthly periods were positive.

## Clustered Bootstrap

Because every game contributes two team observations, treating all observations as independent could understate uncertainty.

The project therefore aggregated returns and wager counts by game and resampled entire games rather than individual team observations.

For the 70%–80% bucket, the game-clustered 95% interval was approximately:

```text
1.59% to 7.93%
```

## Multiple-Testing Adjustment

Ten probability buckets were evaluated. Highlighting the strongest bucket without adjustment would create a data-mining risk.

A Bonferroni-adjusted familywise 95% interval was therefore calculated.

For the 70%–80% bucket:

```text
Adjusted lower bound: approximately 0.21%
Adjusted upper bound: approximately 9.21%
```

It was the only probability bucket whose adjusted interval remained entirely above zero.

This strengthens the single-season result, but it does not replace true out-of-sample validation.

## Louisville Case Study

The Louisville case study included 32 games with complete closing moneylines.

Results:

* actual wins: **13**
* actual win rate: **40.6%**
* average no-vig probability: **53.2%**
* market-expected wins: approximately **17.0**
* wins relative to expectation: approximately **-4.0**
* average pricing error: **-12.6 percentage points**

Louisville’s five-game rolling pricing error reached approximately **-36.8 percentage points**.

Potential explanations include:

* team-performance deterioration
* coaching instability
* injuries or roster availability
* delayed market adjustment
* historical reputation and public expectations
* one-season sampling variation

The result should not be interpreted as proof that Louisville was systematically overpriced.

## Interpretation

The analysis supports three main conclusions.

### 1. Closing markets contain substantial information

The market achieved strong predictive metrics and reasonable calibration across many probability ranges.

### 2. Forecast accuracy does not guarantee profitability

Broad favorite and underdog strategies lost money after quoted sportsbook prices were applied.

The distinction between no-vig calibration and realized return is central to evaluating market efficiency.

### 3. The 70%–80% bucket is an interesting but unconfirmed anomaly

The segment produced positive single-season ROI that survived several robustness checks.

However:

* the same season was used for discovery and evaluation
* only one historical season is available
* execution assumptions are simplified
* market prices may not represent a consensus across books
* true persistence cannot be established without another season

The appropriate label is:

> Promising exploratory single-season finding requiring out-of-sample validation.

## Limitations

* Only the 2021–22 season is analyzed.
* The odds source may represent one reported closing line rather than a consensus market.
* Historical listed prices may not have been available at meaningful size.
* Sportsbook limits, rejected wagers, slippage, and line movement are not modeled.
* The analysis assumes one-unit flat staking.
* Bootstrap resampling cannot replace independent test data.
* The candidate bucket was discovered and evaluated within the same season.
* Bonferroni adjustment is conservative but does not eliminate all specification-search risk.
* Injuries, suspensions, coaching changes, and roster availability are not explicitly modeled.
* Neutral-site classification and conference controls are not yet included.
* Additional seasons are needed to test persistence.

## Next Research Steps

Future work should:

1. Obtain another reliable season of historical closing moneylines.
2. test the 70%–80% result entirely out of sample
3. compare opening and closing probabilities
4. evaluate line movement and information incorporation
5. distinguish regular-season, conference-tournament, and NCAA Tournament games
6. add neutral-site and conference-level controls
7. incorporate team strength, recent form, and roster context
8. compare flat staking with fractional Kelly sizing
9. model bankroll growth and risk of ruin
10. expand unit tests and pipeline automation

## Current Conclusion

The 2021–22 NCAA men’s basketball closing moneyline market was generally well calibrated and produced strong probability forecasts.

Broadly wagering on favorites or underdogs did not generate positive returns after sportsbook prices were applied.

The 70%–80% no-vig probability bucket generated a 4.77% flat-stake ROI and remained positive after chronological, subgroup, clustered-bootstrap, and multiple-testing checks. It is the study’s most important research finding, but it remains exploratory until evaluated against an independent season.
