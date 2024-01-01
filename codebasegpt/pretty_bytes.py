def bytes_to_str(num, suffix='B'):
    k_base = 1000.0
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < k_base:
            if unit == '':
                # bytes
                return "%.0f %s%s" % (num, unit, suffix)
            else:
                return "%3.1f %s%s" % (num, unit, suffix)
        num /= k_base
    return "%.1f %s%s" % (num, 'Y', suffix)
