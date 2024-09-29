
class InvalidChar(Exception):
    def __init__(self, message: str):
        self.mesage = message
        super().__init__(self.mesage)