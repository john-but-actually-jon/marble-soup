import time


class ProgBar:
    def __init__(self, n_iter: int):
        self.n_iter = n_iter

    def update(self, iter: int):
        n_fin = int(iter / self.n_iter * 82)
        print(
            "[" + "=" * n_fin + " " * (82 - n_fin) + f"] {iter/self.n_iter*100:.2f}%",
            end="\r",
        )
        time.sleep(0)  # Weird hack to get jupyter carriage return to render
