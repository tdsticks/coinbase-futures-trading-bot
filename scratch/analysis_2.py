from collections import OrderedDict
import random
from pprint import pprint as pp


def calculate_market_direction(p_weights, p_directions, p_neutral_range):
    """
    Calculate the market direction based on weights and signal directions.
    weights: Dictionary of weights by time unit
    directions: Dictionary of signal directions by time unit, 'short' or 'long'
    """
    calc_score = 0
    for time_unit, weight in p_weights.items():
        direction_multiplier = 1 if p_directions[time_unit] == 'long' else -1
        calc_score += weight * direction_multiplier

        # Determine if the score is within the neutral range
    if -neutral_range <= calc_score <= p_neutral_range:
        cacl_market_direction = 'neutral'
    else:
        cacl_market_direction = 'long' if calc_score > 0 else 'short'
    return cacl_market_direction, calc_score


# Define weights and directions
# Define weights in an OrderedDict to preserve order
weights = OrderedDict([
    ("Weekly", 168), ("Ten Day", 240), ("Five Day", 120), ("Three Day", 72),
    ("Two Day", 48), ("Daily", 24), ("Twelve Hour", 12), ("Eight Hour", 8),
    ("Six Hour", 6), ("Four Hour", 4), ("Three Hour", 3), ("Two Hour", 2),
    ("One Hour", 1), ("Half Hour", 0.5), ("Fifteen Min", 0.25)
])
# weights = {
#     "Weekly": 168, "Ten Day": 240, "Five Day": 120, "Three Day": 72,
#     "Two Day": 48, "Daily": 24, "Twelve Hour": 12, "Eight Hour": 8,
#     "Six Hour": 6, "Four Hour": 4, "Three Hour": 3, "Two Hour": 2,
#     "One Hour": 1, "Half Hour": 0.5, "Fifteen Min": 0.25
# }

# Calculate max and min scores and neutral range
max_score = sum(weights.values())
min_score = -max_score
neutral_range = max_score / 2  # Neutral range is 1/3 of max score

# Initialize results list
results = []

# Generate 100 random market scenarios
for _ in range(100):
    # Randomly assign directions
    directions = {time_unit: random.choice(['long', 'short']) for time_unit in weights}

    # Calculate market direction and score
    # market_direction, score = calculate_market_direction(weights, directions)
    # Calculate market direction and score
    market_direction, score = calculate_market_direction(weights, directions, neutral_range)

    # Append the result
    results.append((market_direction, score, directions))

# Display the results
for result in results:
    direction, score, scenario = result
    # print(f"Market Direction: {direction}, Score: {score}, Scenario: {scenario}")
    # print(f"Market Direction: {direction}, Score: {score}, Scenario:")
    # pp(scenario)
    scenario_str = ', '.join(f"{unit}: {scenario[unit]}" for unit in weights)  # Order preserved
    # print(f"Market Direction: {direction}, Score: {score}, Scenario: {scenario_str}")
    if direction == 'neutral':
        print(f"    >>> Market Direction: {direction}, Score: {score}")
    else:
        print(f"Market Direction: {direction}, Score: {score}")
    # pp(scenario_str)