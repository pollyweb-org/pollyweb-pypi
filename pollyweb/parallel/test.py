import sys

from pollyweb import utils as pw

sys.modules.setdefault("PW_UTILS", pw)

from pollyweb.parallel.TEST_PARALLEL import TEST_PARALLEL

def main() -> None:
    print(pw.LOG.hello())
    pw.RUNNER.RunFromConsole(
        file=__file__,
        name=__name__,
        testFast=False,
        method=TEST_PARALLEL.TestParallel,
    )


def test_parallel_runner() -> None:
    main()


if __name__ == "__main__":
    main()