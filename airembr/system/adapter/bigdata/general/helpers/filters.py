def within(interval) -> str:
    return f"DATE_SUB(NOW(), INTERVAL {interval})"