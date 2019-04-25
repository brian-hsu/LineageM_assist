from ControllerLineageM import LM


class Main:
    def __init__(self):
        self.LM = LM(path=r'./Data/')

    def start(self):
        self.LM.go_thread()


if __name__ == "__main__":
    obj = Main()
    obj.start()
