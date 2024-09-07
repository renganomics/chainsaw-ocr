def progress_bar(progress, total):
    percent = 100 * (progress/float(total))
    bar = "█" * int(percent) + "-" * (100 - int(percent))
    print(f"\r|{bar}| {percent:2f}%", end="\r")

if __name__ == "__main__":
    for count in range(1000, 20000):
        progress_bar(count, 20000)
