"""A stub for the real app runner that sends strings to AFL-perffuzz to run
and reports runtime analysis.

This is a stub to use in place targetAppConnect.py for smoke testing on the developer machine.
"""
from typing import Tuple, Union
import random

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# Tuple returned from run_input is
# actual_cost  (total control flow edge count)  (int)
# hnb  (has new bytes)   (int ... ?)
# hnm, (has new max)     (bool)
# hs  (hot spot)         (int)


class InputHandler:
    """A stub for testing with random feedback in the host environment,
    before moving execution onto the Docker image
    """
    def __init__(self):
        log.debug("STUB InputHandler created")

    @staticmethod
    def server_connect():
        """
        Setting up the client connection to the C app server.
        :return: socket
        """
        log.debug("FAKE connection to server")

    def is_connected(self) -> bool:
        return True

    def run_input(self,
                  test_case: Union[str, bytes],
                  run_type: str = "nml"
                  ) -> Tuple[int, bool, bool, int]:
        """This is a stub that generates fake feedback"""
        return (random.randint(0, 4),
                random.choice([True, False]),  # integer or boolean?
                random.choice([True, False]),
                random.randint(0, 4))

    def close_connection(self):
        print("\nSocket Closed")

    def open_connection(self):
        return
