"""Consecutive-failure throttling (SP 800-63B: no more than 100 consecutive failed attempts)."""

MAX_CONSECUTIVE_FAILURES = 100


class Throttle:
    def __init__(self):
        self._failures = {}

    def record_failure(self, account):
        self._failures[account] = self._failures.get(account, 0) + 1

    def record_success(self, account):
        self._failures[account] = 0

    def failures(self, account):
        return self._failures.get(account, 0)

    def is_locked(self, account):
        return self.failures(account) >= MAX_CONSECUTIVE_FAILURES
