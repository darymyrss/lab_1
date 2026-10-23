"""Стратегии классификации значений показателя для тепловой карты.

Паттерн «Стратегия»: каждый класс инкапсулирует один алгоритм расчёта
границ классов и взаимозаменяем через общий интерфейс ClassificationStrategy.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence

from .models import PaletteKind


class ClassificationStrategy(ABC):
    """Интерфейс стратегии: по набору значений возвращает границы классов."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Название метода для легенды и выпадающего списка в интерфейсе."""

    @property
    @abstractmethod
    def palette_kind(self) -> PaletteKind:
        """Тип цветовой шкалы, подходящий методу."""

    @abstractmethod
    def compute_breaks(self, values: Sequence[float], class_count: int) -> list[float]:
        """Вернуть возрастающие границы классов: [b0, b1, ..., bk], k <= class_count.

        Пустой список означает, что классифицировать нечего.
        """


def _validate(values: Sequence[float], class_count: int) -> None:
    if class_count < 2:
        raise ValueError("class_count должен быть не меньше 2")
    for v in values:
        if v != v:  # NaN
            raise ValueError("values не должны содержать NaN")


def _dedupe(breaks: Sequence[float]) -> list[float]:
    """Убрать совпадающие границы, сохранив порядок."""
    result: list[float] = []
    for b in breaks:
        if not result or b > result[-1]:
            result.append(b)
    return result


class EqualIntervalStrategy(ClassificationStrategy):
    """Равные интервалы: диапазон [min, max] делится на равные части."""

    @property
    def name(self) -> str:
        return "Равные интервалы"

    @property
    def palette_kind(self) -> PaletteKind:
        return PaletteKind.SEQUENTIAL

    def compute_breaks(self, values: Sequence[float], class_count: int) -> list[float]:
        _validate(values, class_count)
        if not values:
            return []
        low, high = min(values), max(values)
        if low == high:
            return [low, high]
        step = (high - low) / class_count
        breaks = [low + i * step for i in range(class_count)]
        breaks.append(high)
        return breaks


class QuantileStrategy(ClassificationStrategy):
    """Квантили: в каждый класс попадает примерно одинаковое число территорий."""

    @property
    def name(self) -> str:
        return "Квантили"

    @property
    def palette_kind(self) -> PaletteKind:
        return PaletteKind.SEQUENTIAL

    def compute_breaks(self, values: Sequence[float], class_count: int) -> list[float]:
        _validate(values, class_count)
        if not values:
            return []
        ordered = sorted(values)
        last = len(ordered) - 1
        breaks: list[float] = []
        for i in range(class_count + 1):
            position = last * i / class_count
            lower_index = int(position)
            upper_index = min(lower_index + 1, last)
            fraction = position - lower_index
            breaks.append(ordered[lower_index] + (ordered[upper_index] - ordered[lower_index]) * fraction)
        deduped = _dedupe(breaks)
        if len(deduped) == 1:
            return [deduped[0], deduped[0]]
        return deduped


class DivergingStrategy(ClassificationStrategy):
    """Расхождение от нуля: симметричная шкала «убыль — рост».

    Подходит для показателей со знаком, например изменения численности
    населения за период в процентах.
    """

    @property
    def name(self) -> str:
        return "Убыль / рост относительно 0"

    @property
    def palette_kind(self) -> PaletteKind:
        return PaletteKind.DIVERGING

    def compute_breaks(self, values: Sequence[float], class_count: int) -> list[float]:
        _validate(values, class_count)
        if not values:
            return []
        bound = max(abs(min(values)), abs(max(values)))
        if bound == 0:
            return [0.0, 0.0]
        step = 2 * bound / class_count
        breaks = [-bound + i * step for i in range(class_count)]
        breaks.append(bound)
        return breaks
