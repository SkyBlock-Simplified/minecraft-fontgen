def progress_bar(current, total, padding=2, width=40):
    progress = current / total
    filled = int(width * progress)
    bar = '█' * filled + '-' * (width - filled)
    left_pad = ' ' * padding
    print(f"\r{left_pad}[{bar}] {current}/{total}", end='', flush=True)
