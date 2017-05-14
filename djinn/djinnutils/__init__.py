import time


def get_epoch_time_of_weeks_ago(weeks):
    """
    Helper method to figure out epoch time for X weeks ago.
    :param weeks: number of weeks to subtract from current time as int.
    :return: epoch millisecond timestamp as string, or None if weeks is None or zero.
    """
    if not weeks:
        return None
    weekms = 604800000  # Milliseconds in a week
    now = int(time.time() * 1000.0)
    timestamp = now - (weekms * weeks)
    return str(timestamp)
