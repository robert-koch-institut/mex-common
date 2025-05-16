from mex.common.exceptions import MExError, TimedReadTimeout


def test_mex_error_str() -> None:
    assert (
        str(MExError("I", "have", 5, object, "arguments"))
        == "MExError: I, have, 5, <class 'object'>, arguments"
    )


def test_timed_read_timeout_str() -> None:
    assert (
        str(TimedReadTimeout("I have 2", "args", seconds=5.3))
        == "I have 2, args (seconds elapsed=5.300)"
    )
