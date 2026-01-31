# bots/utils.py
from typing import Optional, Set

def final_step_len(game, player) -> int:
    """Return number of on-board steps for player (FINAL_STEP)."""
    return len(game.path(player))

def landing_step(game, player: int, piece: int, roll: int) -> Optional[int]:
    """
    Return the landing *step index* along the player's path (0..FINAL_STEP-1),
    or FINAL_STEP if piece finishes, or None if roll == 0 or move illegal (overshoot).
    Does NOT check for occupancy/capture legality — only arithmetic.
    """
    if roll == 0:
        return None
    pos = game.pos[player][piece]
    final = final_step_len(game, player)
    new = pos + roll
    if new > final:
        return None
    return new

def landing_square(game, player: int, piece: int, roll: int) -> Optional[int]:
    """
    Return board square index where the piece would land,
    or None if finishing or move invalid.
    """
    step = landing_step(game, player, piece, roll)
    if step is None:
        return None
    final = final_step_len(game, player)
    if step == final:
        return None
    return game.path(player)[step]

def is_rosette(game, square: int) -> bool:
    return square in getattr(game, "ROSETTES", set())

def is_safe_square(game, square: int) -> bool:
    return square in getattr(game, "SAFE_SQUARES", set())

def will_capture(game, player: int, piece: int, roll: int) -> bool:
    """
    Return True if playing this move would capture an opponent piece (per engine rules).
    Respects SAFE_SQUARES (i.e., landing on a safe square cannot capture).
    """
    sq = landing_square(game, player, piece, roll)
    if sq is None:
        return False
    if is_safe_square(game, sq):
        return False
    opp = 1 - player
    opp_path = game.path(opp)
    for i,opp_pos in enumerate(game.pos[opp]):
        if 0 <= opp_pos < final_step_len(game, opp):
            if opp_path[opp_pos] == sq:
                return True
    return False

def can_opp_capture_after_move(game, player: int, piece: int, roll: int) -> bool:
    """
    Simulate the move (without mutating original): if after the move the opponent
    has ANY legal single-turn move that would capture the moved piece, return True.
    This checks all opponent pieces and all rolls 1..4 for a capturing landing square
    and that the landing move would be legal (not blocked by their own piece and not landing on SAFE).
    """
    # clone game and perform move on the clone
    g = game.clone()
    g.play_move(piece, roll)

    # find where our moved piece ended up; if finished => cannot be captured
    new_step = g.pos[player][piece]
    final = final_step_len(g, player)
    if new_step >= final:
        return False
    landing_sq = g.path(player)[new_step]

    opp = 1 - player
    opp_path = g.path(opp)
    final_opp = final_step_len(g, opp)

    for opp_idx, opp_pos in enumerate(g.pos[opp]):
        # try all opponent rolls that would land on landing_sq
        for r in (1,2,3,4):
            # compute resulting step for this opp piece
            if opp_pos == -1:
                new_opp_step = r - 1
            else:
                new_opp_step = opp_pos + r

            if new_opp_step < 0 or new_opp_step > final_opp:
                continue
            if new_opp_step == final_opp:
                # finishing move; cannot capture our piece
                continue
            # check if that step corresponds to landing_sq
            if opp_path[new_opp_step] != landing_sq:
                continue

            # now check legality for opponent: not landing on their own piece
            blocked = False
            for other_idx, other_pos in enumerate(g.pos[opp]):
                if other_idx == opp_idx:
                    continue
                if 0 <= other_pos < final_opp and other_pos == new_opp_step:
                    blocked = True
                    break
            if blocked:
                continue

            # landing on SAFE prevents capture (engine disallows capture on safe)
            if is_safe_square(g, landing_sq):
                continue

            # passed all checks: opponent *can* capture on next turn with roll r
            return True

    return False

