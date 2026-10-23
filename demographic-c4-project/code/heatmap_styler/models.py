"""Модели данных компонента Heatmap Styler (неизменяемые DTO)."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PaletteKind(Enum):
    """Тип цветовой шкалы, которую требует метод классификации."""

    SEQUENTIAL = "sequential"  # от меньшего к большему (плотность, численность)
    DIVERGING = "diverging"  # убыль <- 0 -> рост (изменение численности, %)


@dataclass(frozen=True)
class RegionMetric:
    """Значение показателя для одной территории (приходит из App State Store)."""

    region_id: str  # код ОКТМО или код субъекта
    name: str
    value: float | None  # None — данных нет


@dataclass(frozen=True)
class Palette:
    """Набор цветов шкалы и цвет для территорий без данных."""

    kind: PaletteKind
    colors: tuple[str, ...]
    no_data_color: str = "#D9D9D9"


@dataclass(frozen=True)
class ColorClass:
    """Один класс легенды: интервал значений и его цвет."""

    index: int
    lower: float
    upper: float
    color: str
    label: str


@dataclass(frozen=True)
class StyledRegion:
    """Территория с назначенным цветом — готова к передаче в слой Leaflet."""

    region_id: str
    name: str
    value: float | None
    color: str
    class_index: int | None  # None — территория без данных


@dataclass(frozen=True)
class HeatmapStyle:
    """Результат работы компонента: легенда и раскраска территорий."""

    method_name: str
    classes: tuple[ColorClass, ...]
    regions: tuple[StyledRegion, ...]
