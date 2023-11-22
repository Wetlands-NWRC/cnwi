import ee


class Phase:
    def __init__(self, mode: int) -> None:
        self.mode = mode
        self._name = mode

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = f"phase_{value}"

    @property
    def sin(self) -> str:
        return f"sin_{self.mode}"

    @property
    def cos(self) -> str:
        return f"cos_{self.mode}"

    def compute(self, image: ee.Image) -> ee.Image:
        return image.select(self.cos).atan2(image.select(self.sin)).rename(self.name)


class Amplitude:
    def __init__(self, mode: int) -> None:
        self.mode = mode
        self._name = mode

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = f"amp_{value}"

    @property
    def sin(self) -> str:
        return f"sin_{self.mode}"

    @property
    def cos(self) -> str:
        return f"cos_{self.mode}"

    def compute(self, image: ee.Image) -> ee.Image:
        return image.select(self.cos).hypot(image.select(self.sin)).rename(self.name)
