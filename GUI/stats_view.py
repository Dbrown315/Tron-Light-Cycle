#
# File: stats_view.py
# Group: Group 9
# Purpose: Formatting helper for GUI leaderboard and telemetry overlay


def leaderboard_rows(records):
    """
    Return display-ready rows; rankings come from TelemetryRecorder ordering.
    """
    result = []
    for index, item in enumerate(records, 1):
        result.append(
            (
                str(index),
                str(item["player"]).strip()[:24],
                str(item["match_wins"]),
                str(item["match_losses"]),
                str(item["round_wins"]),
                str(item["matches_played"]),
            )
        )
    return result


def metric_rows(metrics):
    """
    Keep estimated ticks explicitly labeled as an estimate
    """
    return [
        ("Rounds recorded", str(metrics.get("rounds") or 0)),
        (
            "Average round duration",
            f'{float(metrics.get("avg_round_seconds") or 0):.1f} s',
        ),
        ("Longest round", f'{float(metrics.get("longest_round_seconds") or 0):.1f} s'),
        (
            "Estimated average ticks / round",
            f'{float(metrics.get("avg_round_ticks") or 0):.1f}',
        ),
        (
            "Average combined trail cells",
            f'{float(metrics.get("avg_combined_trail_cells") or 0):.1f}',
        ),
        ("Drawn rounds", str(metrics.get("draws") or 0)),
    ]
