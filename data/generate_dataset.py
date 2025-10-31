"""
Dataset Generator for Voting Rules in Python
============================================

This script generates the example dataset from the PDF.
"""

import csv
from typing import List, Tuple
from pathlib import Path


def create_example_dataset() -> List[Tuple[List[str], int]]:
    """
    Create the example dataset from the PDF:
    n = 27 voters, m = 4 candidates {a, b, c, d}
    
    Returns:
        List of tuples (preference_order, number_of_voters)
    """
    preferences = [
        (['a', 'b', 'c', 'd'], 5),
        (['a', 'c', 'b', 'd'], 4),
        (['d', 'b', 'a', 'c'], 2),
        (['d', 'b', 'c', 'a'], 6),
        (['c', 'b', 'a', 'd'], 8),
        (['d', 'c', 'b', 'a'], 2),
    ]
    
    return preferences


def save_preferences_csv(preferences: List[Tuple[List[str], int]], 
                        filename: str) -> None:
    """
    Save preferences to a CSV file.
    One row per voter with their preference order.
    
    Args:
        preferences: List of tuples (preference_order, number_of_voters)
        filename: Output CSV filename
    """
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Find maximum number of candidates
        max_candidates = max(len(pref_order) for pref_order, _ in preferences)
        
        # Write header
        header = ['Voter'] + [f'Rank{i+1}' for i in range(max_candidates)]
        writer.writerow(header)
        
        # Write voter preferences
        voter_id = 1
        for pref_order, count in preferences:
            for _ in range(count):
                row = [f'voter_{voter_id}'] + pref_order
                writer.writerow(row)
                voter_id += 1


def main():
    """Generate the example dataset."""
    script_dir = Path(__file__).parent
    data_dir = script_dir
    
    # Ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the example dataset 
    print("Generating example dataset (n=27, m=4)...")
    example_prefs = create_example_dataset()
    example_file = data_dir / 'election_data.csv'
    save_preferences_csv(example_prefs, str(example_file))
    total_voters = sum(count for _, count in example_prefs)
    print(f"Saved dataset to {example_file}")
    print(f"Total voters: {total_voters}")


if __name__ == "__main__":
    main()
