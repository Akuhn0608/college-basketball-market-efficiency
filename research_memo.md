# Research Memo: College Basketball Market Efficiency

## Research Question

How accurately do closing NCAA men’s basketball moneylines reflect actual game outcomes, and are there identifiable differences in pricing across probability ranges, favorites, underdogs, and selected teams?

The current analysis focuses on the 2021–22 season and includes a Louisville basketball case study.

## Data

The analysis combines two primary datasets:

1. NCAA men’s basketball team and game-result data from the Kaggle March Machine Learning Mania dataset.
2. Historical closing moneylines and scores from the Sportsbook Review Online NCAA basketball odds archive.

The odds source contained 5,481 games. After requiring complete moneylines and mapping team names to official NCAA team identifiers, 5,344 games remained in the final analysis.

Team-name normalization achieved 99.95% mapping coverage. Three games involving Chaminade were excluded because the team was not represented in the standard Division I team-ID dataset.

## Data Preparation

The odds archive recorded each game as two consecutive rows:

* one row for the visiting team
* one row for the home team

The data was transformed into one row per game containing:

* game date
* visitor and home teams
* final scores
* visitor and home moneylines
* official NCAA team IDs
* game outcome indicators

Team names were standardized by:

* converting text to lowercase
* removing spaces and punctuation
* removing accent marks
* matching normalized names against official names and known alternative spellings
* applying a small manual alias dictionary for source-specific abbreviations

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

Because sportsbooks include a margin, the two raw implied probabilities generally sum to more than 100%.

## Vig Removal

For each game, the raw visitor and home implied probabilities were divided by their combined total.

```text
No-vig probability =
Team implied probability / Combined implied probability
```

This produced two adjusted probabilities that sum to 100%.

The average sportsbook vig in the dataset was 3.70%.

## Evaluation Metrics

### Brier Score

The Brier score measures the average squared difference between predicted probabilities and actual binary outcomes.

Lower values indicate more accurate probability estimates.

The 2021–22 market Brier score was:

```text
0.1793
```

### Log Loss

Log loss evaluates probability accuracy while penalizing highly confident incorrect predictions more severely.

The 2021–22 market log loss was:

```text
0.5336
```

### Calibration

Calibration compares average predicted probabilities with actual win rates.

A market is well calibrated when teams priced near a given probability win approximately that percentage of games.

For example, teams in the 40–50% visitor probability bucket had:

```text
Average market probability: 44.8%
Actual win rate: 45.5%
Calibration error: +0.7 percentage points
```

This indicates strong calibration within that range.

## Main Findings

### Overall Market Accuracy

The closing moneyline market demonstrated meaningful predictive accuracy.

The strongest calibration appeared in the middle probability ranges, where sample sizes were relatively large. Larger deviations appeared in some extreme probability buckets, though these groups contained fewer games and should therefore be interpreted cautiously.

### Probability-Bucket Findings

Notable results included:

* Teams priced between 20% and 30% won 19.4% of games.
* Teams priced between 30% and 40% won 35.8% of games.
* Teams priced between 40% and 50% won 45.5% of games.
* Teams priced between 70% and 80% won 81.4% of games.
* Teams priced above 90% won 83.3% of games, though this bucket contained only 30 observations.

The extreme favorite result should not be treated as strong evidence of systematic mispricing because of the limited sample size.

### Favorite and Underdog Segments

Visitor favorites:

* Games: 1,566
* Average market probability: 66.3%
* Actual win rate: 67.3%
* Average pricing error: +1.0 percentage point

Visitor underdogs:

* Games: 3,778
* Average market probability: 26.9%
* Actual win rate: 25.1%
* Average pricing error: -1.7 percentage points

Home favorites:

* Games: 3,714
* Average market probability: 73.5%
* Actual win rate: 75.1%
* Average pricing error: +1.6 percentage points

Home underdogs:

* Games: 1,630
* Average market probability: 34.4%
* Actual win rate: 33.6%
* Average pricing error: -0.7 percentage points

These results suggest that favorites slightly outperformed their average market probabilities during the season, while underdogs slightly underperformed them.

This does not automatically imply a profitable strategy because transaction costs, line selection, timing, and sportsbook limits are not included in the analysis.

## Louisville Case Study

The Louisville case study included 32 games with complete closing moneylines.

Results:

```text
Actual wins: 13
Actual win rate: 40.6%
Average no-vig market probability: 53.2%
Market-expected wins: approximately 17.0
Average pricing error: -12.6 percentage points
```

Louisville therefore finished approximately four wins below the cumulative expectation implied by its closing moneylines.

The cumulative expected-versus-actual chart shows the gap widening as the season progressed.

This result should not be interpreted as proof that Louisville was systematically overpriced. It may reflect:

* team performance deterioration
* coaching instability
* injuries or roster availability
* delayed market adjustment
* Louisville’s historical reputation
* one-season sampling variation

A stronger follow-up study would examine whether the pricing gap was concentrated early in the season and whether markets adjusted later.

## Interpretation

The analysis supports the general view that betting markets contain substantial information and are reasonably efficient, particularly across high-volume middle probability ranges.

However, market efficiency does not require every subgroup or season to be perfectly calibrated. Temporary deviations may occur when teams experience abrupt changes in performance, coaching, personnel, or public expectations.

The Louisville result provides a useful example of how team-specific performance can diverge materially from market expectations over a season.

## Limitations

* The analysis currently covers only one season.
* The odds archive may represent one sportsbook or reported closing line rather than a true market consensus.
* The project does not yet examine opening-to-closing line movement.
* It does not account for injuries, suspensions, coaching changes, or roster availability.
* Team-level results may be highly sensitive to sample size.
* Extreme probability buckets contain fewer observations.
* The current analysis evaluates predictive accuracy rather than betting profitability.
* Transaction costs and bet sizing are not modeled.

## Next Research Steps

The next version should:

1. Add the 2022–23 season.
2. Compare Louisville’s market expectations before and during the Kenny Payne era.
3. Measure rolling pricing error throughout each season.
4. Compare opening and closing probabilities when both are available.
5. Separate regular-season and NCAA Tournament games.
6. Analyze home, away, and neutral-site performance.
7. Add conference and team-strength controls.
8. Test whether deviations persist across multiple seasons.
9. Evaluate simulated betting strategies only after accounting for vig and realistic execution assumptions.

## Current Conclusion

The 2021–22 NCAA men’s basketball closing moneyline market was generally well calibrated and produced strong probability forecasts.

The market performed especially well in the middle probability ranges. Favorites modestly outperformed their implied probabilities, while underdogs modestly underperformed.

Louisville represented a notable team-level divergence, finishing roughly four wins below its cumulative market expectation. Additional seasons are needed to determine whether this reflected a short-term transition, delayed market adjustment, or ordinary variation.
