"""File where we will define how a score is calcualted

Currently score is only based on runtime_ms
Returns a score between 1-100, 100 being lowest possible runtime_ms

(in db_populate_dummy.py the min and max runtime are set to 69 and 4200 respectively)
"""

def get_score(runtime_ms):
    if runtime_ms == 0:
        return 0

    min_runtime = 69
    max_runtime = 4200
    runtime_ms = max(min_runtime, min(runtime_ms, max_runtime))
    score = 100 - ((runtime_ms - min_runtime) / (max_runtime - min_runtime)) * 99
    return round(score)
