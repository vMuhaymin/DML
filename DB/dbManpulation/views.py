from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.shortcuts import render


# ----- Admin-required actions -----

@require_http_methods(["GET", "POST"])
def add_race_view(request):
    from django.db import transaction, connection
    from django.shortcuts import render

    if request.method == "GET":
        # just show empty form
        return render(request, "dbManpulation/add_race.html")

    # POST case: read form fields
    raceId = request.POST.get("raceId")
    raceName = request.POST.get("raceName")
    trackName = request.POST.get("trackName")
    raceDate = request.POST.get("raceDate")
    raceTime = request.POST.get("raceTime")

    # We'll collect up to 3 result rows
    result_rows = []
    for i in ["1", "2", "3"]:
        horseId = request.POST.get(f"horseId_{i}")
        resultVal = request.POST.get(f"result_{i}")
        prizeVal = request.POST.get(f"prize_{i}")

        if horseId and resultVal:
            # prize may be blank → treat as NULL
            if prizeVal == "" or prizeVal is None:
                prizeVal = None
            result_rows.append((raceId, horseId, resultVal, prizeVal))

    # Now insert into DB in a transaction
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                # insert race first
                cursor.execute("""
                    INSERT INTO race (raceId, raceName, trackName, raceDate, raceTime)
                    VALUES (%s, %s, %s, %s, %s);
                """, [raceId, raceName, trackName, raceDate, raceTime])

                # insert each race result
                for (rId, hId, resTxt, prizeAmt) in result_rows:
                    cursor.execute("""
                        INSERT INTO raceresults (raceId, horseId, results, prize)
                        VALUES (%s, %s, %s, %s);
                    """, [rId, hId, resTxt, prizeAmt])

        # success
        return render(
            request,
            "dbManpulation/add_race.html",
            {"message": "Race and results saved successfully.", "error": False},
        )

    except Exception as e:
        # something went wrong (bad trackName FK, duplicate raceId, invalid date format, etc.)
        return render(
            request,
            "dbManpulation/add_race.html",
            {"message": f"Error: {e}", "error": True},
        )


@require_http_methods(["GET", "POST"])
def delete_owner_view(request):
    from django.db import connection, transaction
    from django.shortcuts import render

    if request.method == "GET":
        return render(request, "dbManpulation/delete_owner.html")

    owner_id = request.POST.get("ownerId")

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("CALL delete_owner_and_related(%s);", [owner_id])

        return render(
            request,
            "dbManpulation/delete_owner.html",
            {"message": f"Owner {owner_id} and related info deleted.", "error": False},
        )

    except Exception as e:
        return render(
            request,
            "dbManpulation/delete_owner.html",
            {"message": f"Error: {e}", "error": True},
        )


@require_http_methods(["GET", "POST"])
def move_horse_view(request):
    from django.db import connection, transaction
    from django.shortcuts import render

    if request.method == "GET":
        return render(request, "dbManpulation/move_horse.html")

    horse_id = request.POST.get("horseId")
    new_stable_id = request.POST.get("newStableId")

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE horse
                    SET stableId = %s
                    WHERE horseId = %s;
                """, [new_stable_id, horse_id])

        return render(
            request,
            "dbManpulation/move_horse.html",
            {"message": f"Horse {horse_id} moved to stable {new_stable_id}.", "error": False},
        )

    except Exception as e:
        return render(
            request,
            "dbManpulation/move_horse.html",
            {"message": f"Error: {e}", "error": True},
        )


@require_http_methods(["GET", "POST"])
def approve_trainer_view(request):
    from django.db import connection, transaction
    from django.shortcuts import render

    if request.method == "GET":
        return render(request, "dbManpulation/approve_trainer.html")

    trainer_id = request.POST.get("trainerId")
    stable_id = request.POST.get("stableId")

    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE trainer
                    SET stableId = %s
                    WHERE trainerId = %s;
                """, [stable_id, trainer_id])

        return render(
            request,
            "dbManpulation/approve_trainer.html",
            {"message": f"Trainer {trainer_id} assigned to stable {stable_id}.", "error": False},
        )

    except Exception as e:
        return render(
            request,
            "dbManpulation/approve_trainer.html",
            {"message": f"Error: {e}", "error": True},
        )



# ----- Guest browsing / reporting -----
@require_http_methods(["GET"])
def horses_by_owner_view(request):
    from django.db import connection
    from django.shortcuts import render

    lname = request.GET.get("lname", "").strip()

    rows = []
    if lname:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    h.horseName AS horseName,
                    h.age AS age,
                    tr.fname AS trainerFname,
                    tr.lname AS trainerLname
                FROM owner ow
                JOIN owns o
                    ON ow.ownerId = o.ownerId
                JOIN horse h
                    ON h.horseId = o.horseId
                LEFT JOIN trainer tr
                    ON tr.stableId = h.stableId
                WHERE ow.lname = %s;
            """, [lname])
            data = cursor.fetchall()

        for horseName, age, trainerFname, trainerLname in data:
            rows.append({
                "horseName": horseName,
                "age": age,
                "trainerFname": trainerFname,
                "trainerLname": trainerLname,
            })

    return render(request, "dbManpulation/horses_by_owner.html", {
        "lname": lname,
        "rows": rows,
    })


@require_http_methods(["GET"])
def winning_trainers_view(request):
    from django.db import connection
    from django.shortcuts import render

    rows = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                tr.fname       AS trainerFname,
                tr.lname       AS trainerLname,
                h.horseName    AS horseName,
                r.raceName     AS raceName
            FROM raceresults rr
            JOIN horse h
                ON h.horseId = rr.horseId
            JOIN race r
                ON r.raceId = rr.raceId
            JOIN trainer tr
                ON tr.stableId = h.stableId
            WHERE rr.results = 'first';
        """)
        data = cursor.fetchall()

    for trainerFname, trainerLname, horseName, raceName in data:
        rows.append({
            "trainerFname": trainerFname,
            "trainerLname": trainerLname,
            "horseName": horseName,
            "raceName": raceName,
        })

    return render(request, "dbManpulation/winning_trainers.html", {"rows": rows})



@require_http_methods(["GET"])
def trainer_winnings_view(request):
    from django.db import connection
    from django.shortcuts import render

    rows = []
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                tr.fname AS trainerFname,
                tr.lname AS trainerLname,
                SUM(rr.prize) AS totalPrize
            FROM trainer tr
            JOIN horse h
                ON h.stableId = tr.stableId
            JOIN raceresults rr
                ON rr.horseId = h.horseId
            GROUP BY tr.trainerId, tr.fname, tr.lname
            ORDER BY totalPrize DESC;
        """)
        data = cursor.fetchall()

    for trainerFname, trainerLname, totalPrize in data:
        rows.append({
            "trainerFname": trainerFname,
            "trainerLname": trainerLname,
            "totalPrize": totalPrize,
        })

    return render(request, "dbManpulation/trainer_winnings.html", {"rows": rows})


@require_http_methods(["GET"])
def track_stats_view(request):
    """
    For each track:
    - trackname
    - number of races held there
    - total number of horse entries participating in races on that track
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
                t.trackName AS trackname,
                COUNT(DISTINCT r.raceId) AS race_count,
                COUNT(rr.horseId) AS horse_entries
            FROM track t
            LEFT JOIN race r
                ON r.trackName = t.trackName
            LEFT JOIN raceresults rr
                ON rr.raceId = r.raceId
            GROUP BY t.trackName
            ORDER BY t.trackName;
        """)
        rows = cursor.fetchall()

    # rows is a list of tuples. Let's map them to dicts for the template.
    stats = []
    for trackname, race_count, horse_entries in rows:
        stats.append({
            "trackname": trackname,
            "race_count": race_count,
            "horse_entries": horse_entries,
        })

    return render(request, "dbManpulation/track_stats.html", {"stats": stats})
