class LoginGuard:
    def __init__(self):
        self.n = {}

    def failed(self, a):
        self.n[a] = self.n.get(a, 0) + 1

    def succeeded(self, a):
        self.n[a] = 0

    def locked(self, a):
        return self.n.get(a, 0) >= 100
