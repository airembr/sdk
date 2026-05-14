def pretty_time_format(time_in_seconds: float) -> str:
    hours = int(time_in_seconds // 3600)
    minutes = int((time_in_seconds % 3600) // 60)
    seconds = int(time_in_seconds % 60)
    milliseconds = int((time_in_seconds % 1) * 1000)

    if hours > 0:
        return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:05}"
    else:
        return f"{minutes:02}:{seconds:02}.{milliseconds:05}"

def pretty_ms_format(time_in_seconds: float) -> str:
    seconds = int(time_in_seconds % 60)
    milliseconds = int((time_in_seconds % 1) * 1000)

    return f"{seconds:02}.{milliseconds:05}"


def pretty_seconds(total_seconds: int) -> str:
    total_seconds = int(total_seconds)
    days = total_seconds // 86400
    remainder = total_seconds % 86400
    hours = (remainder // 3600)
    remainder %= 3600
    minutes = (remainder // 60)
    seconds = (remainder % 60)

    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        return f"{minutes}:{seconds:02d}m"
    elif total_seconds < 86400:
        if seconds == 0:
            return f"{hours}:{minutes:02d}h"
        else:
            return f"{hours}:{minutes:02d}:{seconds:02d}h"
    else:
        day_str = f"{days}day" if days == 1 else f"{days}days"
        if seconds == 0:
            return f"{day_str} {hours:02d}:{minutes:02d}h"
        else:
            return f"{day_str} {hours:02d}:{minutes:02d}:{seconds:02d}h"


def seconds_to_minutes_seconds(seconds):
    sign = "-" if seconds < 0 else ""
    seconds = abs(seconds)
    minutes = seconds // 60
    remaining_seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{sign}{int(minutes)}:{remaining_seconds:02d}.{milliseconds:03d}"