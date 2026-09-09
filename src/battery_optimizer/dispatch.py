def percentile(values: list[float], target_percentile: float) -> float:
    sorted_values = sorted(values)
    number_of_values = len(sorted_values)
    if number_of_values == 1:
        return sorted_values[0]

    rank = (target_percentile / 100) * (number_of_values - 1)
    lower_index = int(rank)
    upper_index = min(lower_index + 1, number_of_values - 1)
    fraction = rank - lower_index

    return sorted_values[lower_index] + (sorted_values[upper_index] - sorted_values[lower_index]) * fraction
