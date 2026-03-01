from pollyweb.utils.LOG import LOG
from pollyweb.utils.RUNNER import RUNNER
from pollyweb.utils.TEST_UTILS import TEST_UTILS


def main() -> None:
    print(LOG.hello())
    RUNNER.RunFromConsole(
        file=__file__,
        name=__name__,
        testFast=False,
        method=TEST_UTILS.TestUtils,
    )


def test_utils_runner() -> None:
    main()


if __name__ == "__main__":
    main()
