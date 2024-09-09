import math


def progress_bar(progress, total):
    """To be used within a for loop to keep track of progress over iterations"""
    percent = 100 * (progress/float(total))
    # Connect "█" to percentage to overtake "-" and display progress percentage
    # to two decimal places
    bar = "█" * int(percent) + "-" * (100 - int(percent))
    print(f"\r|{bar}| {percent:.2f}%", end="\r")


if __name__ == "__main__":
    numbers = [x * 5 for x in range(2000, 3000)]
    results = []

    progress_bar(0, len(numbers))
    for i, x in enumerate(numbers):
        results.append(math.factorial(x))
        progress_bar(i, len(numbers))
