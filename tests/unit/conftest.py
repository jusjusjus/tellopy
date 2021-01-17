def is_valid_ip(ip):
    """Check ip has form 'x.y.z.w'"""
    parts = [int(part) for part in ip.split('.')]
    valid = len(parts) == 4
    valid = all(0 <= int(part) < 256 for part in parts) and valid
    return valid
