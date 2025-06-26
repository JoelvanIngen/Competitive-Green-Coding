"""
Populate the DB so the UserProfileResponse endpoint can serve data.

* Creates 30 users  (same helper: create_users)
* Adds   10 problems (same helper: add_problems)
* Inserts submissions for every user / problem
  → backend will auto-derive solved counts, language stats, recent submissions

If your backend requires an explicit “mark as solved” call,
adapt write_result() at the bottom.
"""

import random, requests, os, time
from uuid import uuid4

# ──────────────────────────────────────────────
# Re-use existing helpers from leaderboard_populator
# (If you keep the file in the same dir, you can:  from leaderboard_populator import …)
# ──────────────────────────────────────────────
from scripts.leaderboard_populator import (
    create_users,
    add_problems,
    login_user,
    get_users_full,
    submit,
    write_result,
    Difficulty,
    Language,
)

BACKEND = "http://localhost:8080"     # or os.getenv("BACKEND_BASE", …)

# ------------------------------------------------------------------#
# MAIN WORK                                                         #
# ------------------------------------------------------------------#
def create_profile_data(n_problems=10):
    users = get_users_full()           # [{ uuid, username, … }]
    uuid_to_token = {
        u["uuid"]: login_user(u["username"], "Wafel123!")
        for u in users
    }

    for pid in range(1, n_problems + 1):
        for u in users:
            sub_uuid = uuid4()
            submission = {
                "submission_uuid": str(sub_uuid),
                "problem_id": pid,
                "user_uuid": u["uuid"],
                "language": random.choice(
                    [l.value for l in (Language.PYTHON, Language.C)]
                ),
                "timestamp": time.time(),
                "code": "print('green')",
            }
            submit(submission, uuid_to_token[u["uuid"]])

            # simple pass/fail toggle just for variety
            ok = random.random() > 0.2
            write_result(
                {
                    "submission_uuid": str(sub_uuid),
                    "runtime_ms": random.randint(50, 3000),
                    "emissions_kg": round(random.uniform(0.05, 0.4), 3),
                    "energy_usage_kwh": round(random.uniform(0.001, 0.02), 3),
                    "successful": ok,
                    # choose a valid enum value when the run failed
                    "error_reason": None
                        if ok
                        else random.choice(
                            [
                                "tests_failed",
                                "runtime_error",
                                "timeout",
                                "compile_error",
                                "mem_limit",
                                "security",
                                "internal_error",
                            ]
                        ),
                    "error_msg": None if ok else "Expected 42 got 13",
                }
            )


def main():
    create_users()         # 30 by default
    add_problems(10)
    create_profile_data(10)
    print("✅  DB ready for /api/profile/<username>")


if __name__ == "__main__":
    main()
