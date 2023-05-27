__author__ = "Ziyad Alsaeed"
__email__ = "zalsaeed@cs.uoregon.edu"
__status__ = "Testing"

import socket
import logging
from ctypes import *
from typing import Union, Tuple

# this make the message exactly of size 512 bytes. To increase it, you must also increase it from afl-fuzz.c
# (BUFFSIZE) side.
_MAX_INPUT_SIZE = 490


class Payload(Structure):

    """ This class defines a C-like struct """
    _fields_ = [("exec_cost", c_uint32),  # total execution cost
                ("hnm", c_bool),  # has new max?
                ("hs", c_uint32),  # hot spot count. The edge hit the most for this input
                ("hnb", c_uint32),  # has new bits (coverage)? 0: No, 1: change to a particular tuple only, 2: new tuple
                ("run_type", c_char * 4),  # actual (nml) or warmup (wup)? Actual runs will change the perf_max values.
                ("input", c_char * _MAX_INPUT_SIZE)]  # the input itself


class InputHandler:

    def __init__(self, server="localhost", port=2300):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._server = InputHandler.server_connect(server, port)

    @staticmethod
    def server_connect(server="localhost", port=2300):
        """
        Setting up the client connection to the C app server.
        :return: socket
        """
        server_address = (server, port)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
        # s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)

        if s is None:
            print("Error creating socket")

        try:
            s.connect(server_address)
            print("Connected to %s" % repr(server_address))
            return s
        except ConnectionError:
            print(f"ERROR: Connection to {repr(server_address)} refused")
            return None
            # sys.exit(1)

    def is_connected(self) -> bool:
        return self._server is not None

    def run_input(self, test_case: Union[str, bytes], run_type: str = "nml") -> Tuple[int, int, bool, int]:
        """
        Run target application and log interactions.

        :param test_case: The input to run on the target application.
        :param run_type: The run type "***": would lead to changing the max_count on AFL side, "wup": will skip that.
        :return: A tuple of (total-execution-cost: int, hnb: int, hnm: bool, hotspot: int).
        """

        if len(test_case) > _MAX_INPUT_SIZE:
            raise RuntimeError(f"Got input with size ({len(test_case)}) larger than the allowed limit "
                               f"({_MAX_INPUT_SIZE})")

        if isinstance(test_case, str):
            test_case = test_case.encode('utf_8')

        payload_out = Payload(0,  # exec_cost
                              False,  # hnm
                              0,  # hs
                              0,  # hnb (has new bits, aka coverage)
                              run_type.encode('utf_8'),  # run type "wup": Warmup, "***": otherwise
                              test_case  # input (must be sent as a stream of bytes)
                              )
        # sending input to instrumentor to run on target app and collect cost
        self.logger.debug(f"Sending: input={payload_out.input}, run-type={payload_out.run_type}, "
                          f"execution_cost={payload_out.exec_cost}, hnb={payload_out.hnb}, hnm={payload_out.hnm}, "
                          f"hs={payload_out.hs}")
        nsent = self._server.send(payload_out)
        self.logger.debug("Sent %d bytes" % nsent)
        buff = self._server.recv(sizeof(Payload))
        payload_in = Payload.from_buffer_copy(buff)
        self.logger.debug(f"Received: input={payload_in.input}, run-type={payload_in.run_type}, "
                          f"execution_cost={payload_in.exec_cost}, hnb={payload_in.hnb}, hnm={payload_in.hnm}, "
                          f"hs={payload_in.hs}")
        return payload_in.exec_cost, payload_in.hnb, payload_in.hnm, payload_in.hs

    def close_connection(self):
        self._server.close()
        self._server = None
        print("\nSocket Closed")

    def open_connection(self):
        if self._server is not None:
            print("Socket already open!")
        else:
            self._server = InputHandler.server_connect()
            print("\nSocket Open")

    def restart(self):
        """Close and reopen to clear tables from current run"""
        self.close_connection()
        self.open_connection()
