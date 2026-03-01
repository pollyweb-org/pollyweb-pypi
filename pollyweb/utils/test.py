from .LOG import LOG
from .RUNNER import RUNNER
from .TEST_UTILS import TEST_UTILS


def main() -> None:
    print(LOG.hello())
    RUNNER.RunFromConsole(
        file=__file__,
        name=__name__,
        testFast=False,
        method=TEST_UTILS.TestUtils,
    )


main()
