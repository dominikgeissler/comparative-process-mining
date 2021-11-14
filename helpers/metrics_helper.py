from datetime import timedelta
# Transfer seconds format in days-hours-minutes format:


def days_hours_minutes(total_seconds):
    td = timedelta(seconds=total_seconds)
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds // 60) % 60
    seconds = td.seconds - hours * 3600 - minutes * 60
    return str(days) + "d "\
        + str(hours) + "h "\
        + str(minutes) + "m "\
        + str(seconds) + "s"


def get_total_pct(result_case1, result_case2):
    total = result_case1 - result_case2
    pct = total / (result_case1 + result_case2)
    return total, pct
