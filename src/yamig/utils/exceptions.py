from pathlib import Path


class ParamsError(Exception):
    pass


class FileExpectedError(OSError):
    def __init__(self, path: Path | str) -> None:
        super().__init__(f"{path!s} is not a file")
