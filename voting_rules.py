"""
Voting Rules Implementation
===========================

This module implements various voting rules for the assignment.
"""

import csv
from typing import List, Optional
from collections import Counter
from pathlib import Path


def load_election_data(csv_file: str) -> List[List[str]]:
    """
    Load election data from CSV file.
    
    Args:
        csv_file: Path to CSV file
        
    Returns:
        List of voter preferences, each as a list of candidates in order
    """
    preferences = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract all rank columns
            pref = [row[key] for key in sorted(row.keys()) if key != 'Voter' and row[key]]
            preferences.append(pref)
    return preferences


def Plurality(preferences: List[List[str]]) -> List[str]:
    """
    Compute the result of plurality voting.
    
    In plurality voting, each voter votes for their top choice.
    The candidate(s) with the most first-place votes win(s).
    
    Args:
        preferences: List of voter preferences, each as a list of candidates
        
    Returns:
        List of winner(s) (may contain multiple in case of tie)
    """
    # Count first-place votes for each candidate
    first_place_votes = Counter(pref[0] for pref in preferences)
    
    if not first_place_votes:
        return []
    
    # Find the maximum number of votes
    max_votes = max(first_place_votes.values())
    
    # Return all candidates with the maximum votes
    winners = [candidate for candidate, votes in first_place_votes.items() 
               if votes == max_votes]
    
    return winners


def CondorcetVoting(preferences: List[List[str]]) -> Optional[str]:
    """
    Compute the result of Condorcet voting.
    
    A Condorcet winner is a candidate who beats every other candidate
    in pairwise comparisons (wins more head-to-head matchups).
    
    Args:
        preferences: List of voter preferences, each as a list of candidates
        
    Returns:
        The Condorcet winner if one exists, None otherwise
    """
    if not preferences or not preferences[0]:
        return None
    
    # Get all unique candidates
    all_candidates = set(candidate for pref in preferences for candidate in pref)
    
    if not all_candidates:
        return None
    
    # For each candidate, check if they beat all others
    for candidate in all_candidates:
        is_condorcet_winner = True
        
        for opponent in all_candidates:
            if candidate == opponent:
                continue
            
            # Count voters who prefer candidate over opponent
            votes_for_candidate = 0
            votes_for_opponent = 0
            
            for pref in preferences:
                candidate_pos = pref.index(candidate) if candidate in pref else len(pref)
                opponent_pos = pref.index(opponent) if opponent in pref else len(pref)
                
                if candidate_pos < opponent_pos:
                    votes_for_candidate += 1
                elif opponent_pos < candidate_pos:
                    votes_for_opponent += 1
            
            # Candidate must beat opponent (more voters prefer candidate)
            if votes_for_candidate <= votes_for_opponent:
                is_condorcet_winner = False
                break
        
        if is_condorcet_winner:
            return candidate
    
    return None


if __name__ == "__main__":
    # Test with example dataset
    data_file = Path("data/election_data.csv")
    
    print("Loading election data...")
    preferences = load_election_data(str(data_file))
    print(f"Loaded {len(preferences)} voters")
    print()
    
    # Question 1: Plurality
    print("Question 1: Plurality Voting")
    plurality_winners = Plurality(preferences)
    print(f"Winner(s): {plurality_winners}")
    print()
    
    # Question 3: Condorcet
    print("Question 3: Condorcet Voting")
    condorcet_winner = CondorcetVoting(preferences)
    if condorcet_winner:
        print(f"Condorcet Winner: {condorcet_winner}")
    else:
        print("No Condorcet winner exists")
