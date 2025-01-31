import random
import math
class AngleDispersion:
    @staticmethod
    def truncated_gaussian(center=0.0, sigma=1.5, low=-20.0, high=20.0):
        while True:
            x = random.gauss(center, sigma)
            if low <= x <= high:
                return x

    @staticmethod
    def get_random_value_float(score, difficulty, max_score=35):
        alpha = score / max_score  # 0..1

        if difficulty:
            alpha += 0.9  # or some offset that you like
            #alpha = min(alpha, 1.0)  # clamp at 1 so it doesn't exceed 100% uniform
        if random.random() < alpha:
            return random.uniform(-20, 20)
        else:
            return AngleDispersion.truncated_gaussian(center=0.0, sigma=1.5, low=-20.0, high=20.0)

# ------------------------------------------------------------------
# Example: See the difference
if __name__ == "__main__":
    score = 0   # best possible score
    # Compare distributions with less_likely_zero=False vs. True
    N = 10_000

    samples_normal = [AngleDispersion.get_random_value_float(score, False) for _ in range(N)]
    samples_less   = [AngleDispersion.get_random_value_float(score, True)  for _ in range(N)]

    avg_normal = sum(samples_normal)/N
    avg_less   = sum(samples_less)/N

    print(AngleDispersion.get_random_value_float(30, False))
    print(AngleDispersion.get_random_value_float(0, True))

