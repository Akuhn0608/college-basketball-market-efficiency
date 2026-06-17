# College Basketball Market Efficiency Research Platform

A Python-based research platform that evaluates the accuracy and efficiency of NCAA men’s basketball betting markets using historical moneyline prices, no-vig probabilities, calibration analysis, and team-level case studies.

The current version analyzes the 2021–22 season and includes a focused Louisville basketball pricing case study.

## Project Overview

Sportsbook moneylines can be interpreted as market prices for game outcomes. However, raw implied probabilities include the sportsbook’s margin, or **vig**, and therefore do not sum to 100%.

This project:

* converts American moneylines into implied probabilities
* removes the sportsbook vig
* evaluates probability accuracy using Brier score and log loss
* measures calibration across probability ranges
* compares favorites and underdogs
* studies Louisville’s actual results against market-expected wins
* presents findings through an interactive Streamlit dashboard

## Current Results

The 2021–22 dataset contains:

* **5,344 games** with complete moneyline data and mapped NCAA teams
* **99.95% team-name mapping coverage**
* **3.70% average sportsbook vig**
* **0.1793 Brier score**
* **0.5336 log loss**

The market was generally well calibrated in the middle probability ranges, while some deviations appeared among larger favorites and longer underdogs.

### Louisville Case Study

Across 32 Louisville games:

* Actual win rate: **40.6%**
* Average no-vig market probability: **53.2%**
* Actual wins: **13**
* Market-expected wins: approximately **17**
* Average pricing error: **-12.6 percentage points**

This indicates that Louisville underperformed its closing market expectations during the season. Because the sample covers only one season, the result should not be interpreted as evidence of a persistent pricing bias.

## Dashboard

The Streamlit dashboard includes:

* overall market statistics
* Brier score and log loss
* probability calibration analysis
* favorite and underdog segmentation
* Louisville actual versus expected wins
* game-level market data

Run the dashboard locally with:

```bash
streamlit run dashboard/app.py
```

## Project Structure

```text
cbb-market-efficiency/
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── reports/
│   └── charts/
├── scripts/
├── src/
├── tests/
├── README.md
├── research_memo.md
├── requirements.txt
└── pytest.ini
```

## Core Methodology

### 1. Convert American Odds to Implied Probability

For positive American odds:

```text
100 / (odds + 100)
```

For negative American odds:

```text
|odds| / (|odds| + 100)
```

### 2. Remove the Vig

For a two-team market, each team’s implied probability is divided by the sum of both raw implied probabilities.

```text
No-vig probability =
Raw implied probability / Total implied probability
```

This forces the two probabilities to sum to 100%.

### 3. Measure Forecast Accuracy

The project evaluates market probabilities using:

* **Brier score**, which measures squared probability error
* **Log loss**, which penalizes confident incorrect predictions more heavily
* **Calibration error**, which compares average predicted probability with actual win rate

Lower Brier score and log loss values indicate stronger probability forecasts.

## Data Sources

The project currently uses:

* NCAA men’s basketball team and game-result data from the Kaggle March Machine Learning Mania dataset
* historical moneyline and game data from the Sportsbook Review Online NCAA basketball odds archive

Team names are normalized and matched to official NCAA team identifiers before analysis.

## Technology

* Python
* pandas
* NumPy
* scikit-learn
* matplotlib
* Streamlit
* pytest

## Testing

Run the unit tests with:

```bash
pytest
```

The current tests cover:

* American odds conversion
* invalid odds handling
* reverse probability-to-odds conversion
* two-way vig removal

## Limitations

* The current market analysis covers only the 2021–22 season.
* Historical sportsbook data may reflect one reported closing line rather than a consensus across all books.
* A small number of non-Division I teams are excluded because they do not appear in the NCAA team-ID dataset.
* Team-level pricing results may reflect performance, injuries, coaching changes, and other information already incorporated unevenly throughout the season.
* Calibration buckets at extreme probabilities contain fewer observations and should be interpreted cautiously.

## Planned Expansion

Future versions will:

* add additional seasons
* analyze how quickly markets adjusted during Louisville’s 2022–23 decline
* compare regular-season and NCAA Tournament pricing
* add rolling calibration and cumulative pricing-error analysis
* examine market behavior by home/away status, conference, and probability range
* expand the interactive dashboard
