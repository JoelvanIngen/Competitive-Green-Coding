import pytest

from execution_engine.docker.gather import _parse_runtime


@pytest.fixture(name="time_output")
def time_output_fixture():
    return {
        "contents": """User time (seconds): 4.60
        System time (seconds): 6.10
        Percent of CPU this job got: 66%
        Elapsed (wall clock) time (h:mm:ss or m:ss): 0:06.21
        Average shared text size (kbytes): 30
        Average unshared data size (kbytes): 50
        Average stack size (kbytes): 30
        Average total size (kbytes): 100
        Maximum resident set size (kbytes): 1804
        Average resident set size (kbytes): 0
        Major (requiring I/O) page faults: 0
        Minor (reclaiming a frame) page faults: 78
        Voluntary context switches: 1
        Involuntary context switches: 3
        Swaps: 0
        File system inputs: 0
        File system outputs: 0
        Socket messages sent: 0
        Socket messages received: 0
        Signals delivered: 0
        Page size (bytes): 4096
        Exit status: 0""",
        "user_time": 6.1,
        "max_ram_kbytes": 1804,
    }



def test_parse_runtime(time_output):
    test_user_time, test_max_ram_kbytes = _parse_runtime(time_output["contents"])
    assert test_user_time == time_output["user_time"]
    assert test_max_ram_kbytes == time_output["max_ram_kbytes"]
