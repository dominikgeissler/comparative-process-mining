from datetime import timedelta
# Transfer seconds format in days-hours-minutes-seconds format:


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

# Calculates and returns the comparative metrics regarding the
# difference between two event logs in total and percentage(pct):


def get_total_pct(result_case1, result_case2):
    total = result_case1 - result_case2
    pct = total / (result_case1 + result_case2)
    return total, pct

# Calculates and returns the percentage value of a handed over metric:
# Accuracy: 2 decimal places


def get_pct(metric):
    return str(round(metric*100, 2)) + "%"
