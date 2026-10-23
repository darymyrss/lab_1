"""Heatmap Styler — компонент контейнера «Веб-интерфейс аналитика» (C4 Level 4).

Прототип логики классификации тепловой карты с паттерном «Стратегия».
"""
from .context import HeatmapStylerContext, StrategyRegistry, default_registry
from .models import ColorClass, HeatmapStyle, Palette, PaletteKind, RegionMetric, StyledRegion
from .palettes import PaletteRegistry
from .strategies import (
    ClassificationStrategy,
    DivergingStrategy,
    EqualIntervalStrategy,
    QuantileStrategy,
)

__all__ = [
    "ClassificationStrategy",
    "ColorClass",
    "DivergingStrategy",
    "EqualIntervalStrategy",
    "HeatmapStyle",
    "HeatmapStylerContext",
    "Palette",
    "PaletteKind",
    "PaletteRegistry",
    "QuantileStrategy",
    "RegionMetric",
    "StrategyRegistry",
    "StyledRegion",
    "default_registry",
]
