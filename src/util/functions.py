def progress_bar(current, total, width=40):
    progress = current / total
    filled = int(width * progress)
    bar = '█' * filled + '-' * (width - filled)
    print(f"\r  [{bar}] {current}/{total}", end='', flush=True)
