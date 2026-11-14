def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def ease_out_back(t, s=1.70158):
    c3 = s + 1
    return 1 + c3 * pow(t - 1, 3) + s * pow(t - 1, 2)
