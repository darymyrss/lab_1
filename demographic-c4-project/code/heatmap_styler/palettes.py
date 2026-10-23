"""Реестр цветовых шкал (последовательные и расходящиеся палитры)."""
from __future__ import annotations

from typing import Final

from .models import Palette, PaletteKind

# Последовательная шкала: светлый — мало, тёмный — много.
_SEQUENTIAL: Final[tuple[str, ...]] = (
    "#FFF5EB", "#FEE6CE", "#FDD0A2", "#FDAE6B", "#FD8D3C", "#F16913", "#D94801", "#8C2D04",
)
# Расходящаяся шкала: красный — убыль, белый — около нуля, синий — рост.
_DIVERGING: Final[tuple[str, ...]] = (
    "#B2182B", "#D6604D", "#F4A582", "#FDDBC7", "#F7F7F7", "#D1E5F0", "#92C5DE", "#4393C3", "#2166AC",
)


class PaletteRegistry:
    """Выдаёт палитру нужного типа на заданное число классов."""

    def get(self, kind: PaletteKind, class_count: int) -> Palette:
        if class_count < 1:
            raise ValueError("class_count должен быть положительным")
        source = _SEQUENTIAL if kind is PaletteKind.SEQUENTIAL else _DIVERGING
        if class_count > len(source):
            raise ValueError(f"палитра поддерживает не более {len(source)} классов")
        return Palette(kind=kind, colors=self._sample(source, class_count))

    @staticmethod
    def _sample(source: tuple[str, ...], count: int) -> tuple[str, ...]:
        """Равномерно выбрать count цветов из шкалы, включая крайние."""
        if count == 1:
            return (source[len(source) // 2],)
        last = len(source) - 1
        return tuple(source[round(i * last / (count - 1))] for i in range(count))
