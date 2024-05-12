import random
import numpy as np

# Define the weights
weights = {
    "Weekly": 168,
    "TenD": 240,
    "FiveD": 120,
    "ThreeD": 72,
    "TwoD": 48,
    "Daily": 24,
    "TwelveH": 12,
    "EightH": 8,
    "SixH": 6,
    "FourH": 4,
    "ThreeH": 3,
    "TwoH": 2,
    "OneH": 1,
    "HalfH": 0.5,
    "FifteenM": 0.25
}

# Define possible signals
signals = ["long", "short"]

# Generate 100 samples
samples = []

# Your list of scores here
scores = []

for _ in range(100):
    sample = {}
    score = 0
    for time_unit, weight in weights.items():
        signal = random.choice(signals)
        sample[time_unit] = signal
        # Calculate the score
        score += weight if signal == "long" else -weight
    sample['Score'] = score
    scores.append(score)
    samples.append(sample)

# Print the samples and their scores
# for index, sample in enumerate(samples):
#     print(f"Sample {index + 1}:")
#     for key, value in sample.items():
#         print(f"  {key}: {value}")
#     print()

print(f"Scores: {scores}")

mean_score = np.mean(scores)
median_score = np.median(scores)
std_deviation = np.std(scores)

print(f"Mean Score: {mean_score}")
print(f"Median Score: {median_score}")
print(f"Standard Deviation: {std_deviation}")

# # Define neutral range based on observed mean and standard deviation
neutral_range_lower = mean_score - 50
neutral_range_upper = mean_score + 50
print(f"Proposed Neutral Range: {neutral_range_lower} to {neutral_range_upper}")