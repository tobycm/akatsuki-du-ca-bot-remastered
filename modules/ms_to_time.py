from typing import Tuple


def mstotime(ms) -> Tuple(("hours", "minutes", "seconds")):
    """
    Convert milliseconds to time.
    """
    millis = int(ms)
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24
    hours = int(hours)
    return (hours, minutes, seconds)