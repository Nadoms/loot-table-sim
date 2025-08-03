class LoadingBar:

    def __init__(self, max_bars: int = 40):
        self.max_bars = max_bars

    def load(self, stage):
        filled = int(stage * self.max_bars)
        print(f"[ {'0' * filled}{'O' * (self.max_bars - filled)} ]", end="\r")

    def __del__(self):
        print("\r\033[K", end="")
