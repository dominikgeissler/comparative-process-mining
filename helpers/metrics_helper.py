from datetime import timedelta


def days_hours_minutes(total_seconds):
    """Transfer seconds format in days-hours-minutes-seconds format"""
    td = timedelta(seconds=total_seconds)
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds // 60) % 60
    seconds = td.seconds - hours * 3600 - minutes * 60
    return str(days) + "d "\
        + str(hours) + "h "\
        + str(minutes) + "m "\
        + str(seconds) + "s"


def get_difference(res1, res2):
    return [res1, str(res1 - res2) if res1 - res2 < 0 else "+" +
            str(res1 - res2) if res1 - res2 > 0 else "0"]


def get_difference_days_hrs_min(res1, res2):
    return [
        days_hours_minutes(res1),
        days_hours_minutes(
            res1 -
            res2) if res1 -
        res2 < 0 else "+" +
        days_hours_minutes(
            res1 -
            res2) if res1 -
        res2 > 0 else "0d"]
