"""
Voting Rules Implementation
===========================

This module implements various voting rules for the assignment.
"""

import csv
from typing import List, Optional
from collections import Counter
from pathlib import Path
import random


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

def PluralityRunoff(preferences):
    """
    Compute the result of plurality runoff voting.

    In plurality with runoff, if the candidate with most votes in the first round
    does not have more than 50% of the votes, the top two candidates move on to
    the second round, and the candidate with most votes in the second round wins.

    Ties:
        - If there is a tie in the first round and majority, the winner is randomly chosen between them.
        - If there is a tie in the first round and not majority, all tied top candidates move on.
        - If there is a tie in the second round, the winner is randomly chosen between them.
    """

    total_voters = len(preferences)
    print(f"Total voters: {total_voters}")

    # Round 1: Count first place votes
    first_place_votes = Counter(pref[0] for pref in preferences)
    print(f"Round 1 votes: {first_place_votes}")

    if not first_place_votes:
        return "No votes cast"

    max_votes = max(first_place_votes.values())

    # Get top candidates with the most votes
    top_candidates = [candidate for candidate, votes in first_place_votes.items() if votes == max_votes]

    # Check if top candidate has more than 50% of votes
    if max_votes > total_voters / 2:
        print(f"{top_candidates[0]} wins outright with {max_votes}/{total_voters} votes")
        if len(top_candidates) > 1:
            print(f"Tie detected, randomly choosing winner from {top_candidates}")
            return random.choice(top_candidates)
        else:
            return top_candidates[0]

    # Round 2: Determine top two candidates
    # if tie at top, all tied top candidates move on; otherwise, the top two candidates move on
    if len(top_candidates) > 1:
        runoff_candidates = top_candidates
        print(f"Tie in first round→ all move to runoff: {runoff_candidates}")
    else: 
        runoff_candidates = [candidate for candidate, votes in first_place_votes.most_common(2)]
        print(f"candidate {top_candidates[0]} got less than 50% of votes → Top two candidates move to runoff: {runoff_candidates}")
        
    # Count votes considering only the runoff candidates
    runoff_votes = []
    for pref in preferences:
        for candidate in pref:
            if candidate in runoff_candidates:
                runoff_votes.append(candidate)
                break

    round2_counts = Counter(runoff_votes)
    print(f"Round 2 votes: {round2_counts}")

    runoff_max_votes = max(round2_counts.values())
    runoff_winners = [candidate for candidate, votes in round2_counts.items() if votes == runoff_max_votes]

    # If tie, randomly choose a winner
    if len(runoff_winners) > 1:
        winner = random.choice(runoff_winners)
        print(f"Tie in runoff→ randomly choosing winner from {runoff_winners}")
        return winner
    else:
        winner = runoff_winners[0]
        return winner


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

def BordaVoting(preferences: List[List[str]]) -> List[str]:
    """
    Compute the result of Borda count voting.

    In Borda voting, each voter ranks all candidates.
    Candidates receive points based on their position in each ranking:
        If there are n candidates:
            1st place = n-1 points
            2nd place = n-2 points
            ...
            last place = 0 points
    The candidate with the most points wins.

    Ties:
        - If there is a tie, the winner is randomly chosen between the tied candidates.
    """
    if not preferences or not preferences[0]:
        return "No votes cast"

    n_candidates = len(preferences[0])
    print(f"Number of candidates: {n_candidates}")

    scores = Counter()
    for i, voter in enumerate(preferences, start=1):
        for rank, candidate in enumerate(voter):
            scores[candidate] += n_candidates - rank - 1

    # Show total scores
    print("--- Total Scores ---")
    for candidate, score in scores.items():
        print(f"{candidate}: {score} points")

    max_score = max(scores.values())
    winning_candidates = [candidate for candidate, score in scores.items() if score == max_score]
    
    if len(winning_candidates) > 1:
        winner = random.choice(winning_candidates)
        print(f"Tie detected, randomly choosing winner from {winning_candidates}")
        return winner
    else:
        winner = winning_candidates[0]
        return winner

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

    # Question 2: Plurality Voting with Runoff
    print("Question 2: Plurality Voting with Runoff")
    plurality_runoff_winner = PluralityRunoff(preferences)
    print(f"Plurality Runoff Winner: {plurality_runoff_winner}")
    print()
    
    # Question 3: Condorcet
    print("Question 3: Condorcet Voting")
    condorcet_winner = CondorcetVoting(preferences)
    if condorcet_winner:
        print(f"Condorcet Winner: {condorcet_winner}")
    else:
        print("No Condorcet winner exists")

     # Question 4: Plurality Voting with Runoff
    print("\nQuestion 4: Borda Voting")
    borda_winner = BordaVoting(preferences)
    print(f"Borda Voting Winner: {borda_winner}")
    print()
