def snake_pick_numbers(teams: int, slot: int, rounds: int) -> list[int]:
    """Return overall pick numbers for a team in a snake draft."""
    if teams < 2:
        raise ValueError("teams must be at least 2")
    if not 1 <= slot <= teams:
        raise ValueError("slot must be between 1 and teams")
    if rounds < 1:
        raise ValueError("rounds must be at least 1")

    picks = []

    for round_number in range(1, rounds + 1):
        if round_number % 2 == 1:
            pick_in_round = slot
        else:
            pick_in_round = teams - slot + 1

        overall_pick = (round_number - 1) * teams + pick_in_round
        picks.append(overall_pick)

    return picks


def picks_until_next_pick(
    teams: int,
    slot: int,
    current_round: int,
) -> int:
    """Number of opponent selections between two of your picks."""
    picks = snake_pick_numbers(teams, slot, current_round + 1)
    return picks[current_round] - picks[current_round - 1] - 1
