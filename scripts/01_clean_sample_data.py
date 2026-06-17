import sys
from pathlib import Path

# Add the main project folder to Python's import path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.features import clean_sample_odds_data


input_path = "data/raw/sample_cbb_odds.csv"
output_path = "data/processed/sample_cbb_odds_clean.csv"

clean_df = clean_sample_odds_data(input_path, output_path)

print("Cleaned data saved to:", output_path)
print(clean_df.head())