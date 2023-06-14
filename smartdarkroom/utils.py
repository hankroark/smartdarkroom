# Copyright 2023 Hank Roark
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
"""
Holds some common utilities that might be used that aren't necessarily considered
part of a darkroom.
"""

import threading
import time
import signal


class RepeatedTimer(object):
    """
    Repeated Timer executes a user supplied function on a regular interval.  The timer starts
    at the construction of the object and stops when told to stop. The first execution
    of the provided function starts at time zero (0).  The timer runs on a background
    thread so other things can execute while this is running.  The times takes into account the
    time to run the given function and as such protects against drift.
    """

    def __init__(self, interval, function, *args, **kwargs):
        """
        Constructs a new instance of the Repeated Timer.

        Parameters:
            interval (float): Required. The number of seconds between execution of the function
            function (function): Required. The function to execute every interval seconds
            *args: The arguments to pass to the function
            **kwargs:  The keywork arguements to pass to the function
        """
        self._timer = None
        self.interval = interval
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.is_running = False
        self._time_zero()
        self.next_call = time.time()
        self.start()

    def _time_zero(self):
        """
        What to do at time zero.  Default is to run the function once.
        """
        self.function(*self.args, **self.kwargs)

    def _run(self):
        """
        Restarts the interval and runs the function in parallel.
        """
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        """
        Starts the time running at every interval.
        """
        if not self.is_running:
            self.next_call += self.interval
            self._timer = threading.Timer(self.next_call - time.time(), self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        """
        Stops the timer from running.  Can be restarted with start function.
        """
        self._timer.cancel()
        self.is_running = False


# From https://stackoverflow.com/questions/2281850/timeout-function-if-it-takes-too-long-to-finish

class Timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)
