"""
Voting Rules Implementation
===========================

This module implements various voting rules for the assignment.
"""

import csv
import random
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
    In case of ties, randomly select one winner.
    
    Args:
        preferences: List of voter preferences, each as a list of candidates
        
    Returns:
        List containing one winner (ties broken randomly)
    """
    # Count first-place votes for each candidate
    first_place_votes = Counter(pref[0] for pref in preferences)
    
    if not first_place_votes:
        return []
    
    # Find the maximum number of votes
    max_votes = max(first_place_votes.values())
    
    # Get all candidates with the maximum votes (tied candidates)
    tied_winners = [candidate for candidate, votes in first_place_votes.items() 
                    if votes == max_votes]
    
    # Randomly break ties by selecting one winner
    if len(tied_winners) > 1:
        winner = random.choice(tied_winners)
        return [winner]
    
    return tied_winners

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
        print(f"Tie in first round -> all move to runoff: {runoff_candidates}")
    else: 
        runoff_candidates = [candidate for candidate, votes in first_place_votes.most_common(2)]
        print(f"candidate {top_candidates[0]} got less than 50% of votes -> Top two candidates move to runoff: {runoff_candidates}")
        
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
        print(f"Tie in runoff -> randomly choosing winner from {runoff_winners}")
        return winner
    else:
        winner = runoff_winners[0]
        return winner


def CondorcetVoting(preferences: List[List[str]]) -> Optional[str]:
    """
    Compute the result of Condorcet voting.
    
    A Condorcet winner is a candidate who beats every other candidate
    in pairwise comparisons (wins more head-to-head matchups).
    In case of ties in pairwise comparisons, randomly breaks the tie.
    
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
            # If tied, randomly break the tie
            if votes_for_candidate < votes_for_opponent:
                is_condorcet_winner = False
                break
            elif votes_for_candidate == votes_for_opponent:
                # Tie: randomly decide winner of this pairwise comparison
                if random.choice([True, False]):  # Randomly choose if candidate wins the tie
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
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1], reverse=True))
    for candidate, score in sorted_scores.items():
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

def check_best_candidate_condition(preferences: List[List[str]], max_percentage: float = 0.5) -> bool:
    """
    Check if no more than the specified percentage of voters have the same best candidate.
    
    Args:
        preferences: List of voter preferences, each as a list of candidates
        max_percentage: Maximum allowed percentage (default: 0.5 for 50%)
        
    Returns:
        bool: True if condition is satisfied, False otherwise
    """
    if not preferences:
        return False
        
    # Count first place votes
    first_place_votes = Counter(pref[0] for pref in preferences)
    
    # Calculate maximum percentage of voters with same best candidate
    total_voters = len(preferences)
    max_votes = max(first_place_votes.values())
    max_percentage_actual = max_votes / total_voters
    
    return max_percentage_actual <= max_percentage

def check_worst_candidate_condition(preferences: List[List[str]], max_percentage: float = 0.4) -> bool:
    """
    Check if no more than the specified percentage of voters have the same worst candidate.
    
    Args:
        preferences: List of voter preferences, each as a list of candidates
        max_percentage: Maximum allowed percentage (default: 0.4 for 40%)
        
    Returns:
        bool: True if condition is satisfied, False otherwise
    """
    if not preferences:
        return False
        
    # Count last place votes
    last_place_votes = Counter(pref[-1] for pref in preferences)
    
    # Calculate maximum percentage of voters with same worst candidate
    total_voters = len(preferences)
    max_votes = max(last_place_votes.values())
    max_percentage_actual = max_votes / total_voters
    
    return max_percentage_actual <= max_percentage

def different_winners():
    """
    Create an election where all four methods produce different unique winners.
    Requirements: n ≥ 60, m ≥ 8, ≤50% same best, ≤40% same worst
    
    Strategy:
    - Group 1: A first (plurality winner) - rank C and D high for their wins
    - Group 2: B first (runoff winner) - rank B > C > D, put A low for runoff
    - Group 3: C first (Condorcet winner) - rank C > D > B, keep D high
    - Group 4: D first (Borda winner) - but also appear 2nd/3rd in other groups
    
    Key: Each group must STRATEGICALLY rank ALL candidates to help specific winners
    """
    candidates = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    preferences = []
    
    # Group 1: 20 voters (33.3%) - A for PLURALITY
    # Strategy: A first (most first-place votes)
    #           C and D ranked high (help them for Condorcet/Borda)
    #           B ranked low (hurt B's Borda score)
    #           A ranked middle elsewhere (won't win Borda/Condorcet)
    for i in range(20):
        preferences.append(['A', 'C', 'D', 'E', 'F', 'B', 'G', 'H'])
    
    # Group 2: 18 voters (30%) - B for RUNOFF
    # Strategy: B first (enough to reach runoff with A)
    #           A ranked VERY LOW (so B beats A in runoff)
    #           rank D higher than C to help D's Borda 
    for i in range(18):
        preferences.append(['B', 'D', 'E', 'C','F', 'A', 'H', 'G'])
    
    # Group 3: 12 voters (20%) - C for CONDORCET
    # Strategy: C first (some first-place support)
    #           D second (D gets high rankings for Borda)
    #           Rank C > D > B > A (C beats all in pairwise)
    for i in range(12):
        preferences.append(['C', 'D', 'B', 'E', 'G', 'A', 'H', 'F'])
    
    # Group 4: 10 voters (16.7%) - D for BORDA
    # Strategy: D first (some first-place support)
    #           C fourth (help  Condorcet)
    #           E third (diversify to meet constraints)
    #           KEY: D must appear 2nd or 3rd in other groups!
    for i in range(10):
        preferences.append(['D', 'B', 'C', 'F', 'G', 'A', 'H', 'E'])
    
    return preferences

def test_election():
    # Create example election
    preferences = different_winners()
    
    # Check conditions
    print("Checking conditions:")
    print(f"Best candidate condition satisfied: {check_best_candidate_condition(preferences)}")
    print(f"Worst candidate condition satisfied: {check_worst_candidate_condition(preferences)}")
    print()
    
    # Test all voting rules
    print("Testing voting rules:")
    
    print("------Plurality Voting------")
    plurality_winner = Plurality(preferences)
    print(f"Plurality winner: {plurality_winner}")
    print()

    print("------Plurality with Runoff Voting------")
    runoff_winner = PluralityRunoff(preferences)
    print(f"Plurality with Runoff winner: {runoff_winner}")
    print()

    print("------Condorcet Voting------")
    condorcet_winner = CondorcetVoting(preferences)
    print(f"Condorcet winner: {condorcet_winner}")
    print()
    
    print("------Borda Voting------")
    borda_winner = BordaVoting(preferences)
    print(f"Borda winner: {borda_winner}")



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

     # Question 4: Borda Voting
    print("\nQuestion 4: Borda Voting")
    borda_winner = BordaVoting(preferences)
    print(f"Borda Voting Winner: {borda_winner}")
    print()

    # Question 6: Election with different winners
    print("Question 6: Election with Different Winners")
    test_election()