"""Logarithmically scaled integer bins for counts"""


class LgBins:
    """Binned counts, log2 scaled, accommodates values up to 2^63"""
    def __init__(self):
        """bins, total, count, maximum, last_bin are public read-only attributes."""
        # bins[0] is count of zeros.
        # bins[k], k>0, is count of elements with values < 2^k and >= 2^(k-1)
        self.bins = [0] * 64
        self.total = 0
        self.count = 0
        self.maximum = 0
        self.last_bin = 0

    def add(self, value: int):
        """Log a value, which must be a non-negative integer."""
        assert value >= 0, "LgBins is for non-negative integers only"
        self.total += value
        self.count += 1
        bin_ = value.bit_length()
        if bin_ > self.last_bin:
            self.last_bin = bin_
        self.bins[bin_] += 1
        if value > self.maximum:
            self.maximum = value

    def mean(self) -> float:
        return self.total / self.count
