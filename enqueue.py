from app.tasks.jobs import q, add_coupon

# test data
selections = [
    {
        "game_id": 1,
        "team_home": "Panathinaikos",
        "team_away": "Slovan Bratislava",
        "score_home": 1,
        "score_away": 1,
        "start": "2021-08-20T18:00:00",
        "location": "GREECE"
    },
    {
        "game_id": 2,
        "team_home": "Partizan Belgrade",
        "team_away": "Ludogorets",
        "score_home": 2,
        "score_away": 0,
        "start": "2022-09-10T17:30:00",
        "location": "SERBIA"
    }
]

user_id = 2

# send job to redis # this works even with app not running
job = q.enqueue(add_coupon, selections, user_id)
print(f"Job {job.id} enqueued")
