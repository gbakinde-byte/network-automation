import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyats import aetest

from utils.connection import connect_all, disconnect_all

log = logging.getLogger(__name__)


class TestConnectivity(aetest.Testcase):

    @aetest.setup
    def setup_test(self, testbed):
        self.devices = testbed.devices

    @aetest.test
    def connectivity(self):
        """Connect to each device in the testbed."""
        failed = connect_all(self.devices, log)
        if failed:
            self.failed(f"Could not connect to: {', '.join(failed)}")
        self.passed("Successfully connected to all devices.")

    @aetest.cleanup
    def cleanup(self):
        disconnect_all(self.devices, log)


if __name__ == "__main__":
    aetest.main()
