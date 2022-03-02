from typing import Optional


class Slots:
    """
    stores global values
    for any tasks to use
    """

    def __init__(
        self,
        name: Optional[str] = None,
        location: Optional[str] = None,
        time: Optional[str] = None,
    ) -> None:
        self.name = name
        self.location = location
        self.time = time
