"""Контекст паттерна «Стратегия» и реестр стратегий компонента Heatmap Styler."""
from __future__ import annotations

from bisect import bisect_right
from collections.abc import Callable, Sequence

from .models import ColorClass, HeatmapStyle, RegionMetric, StyledRegion
from .palettes import PaletteRegistry
from .strategies import (
    ClassificationStrategy,
    DivergingStrategy,
    EqualIntervalStrategy,
    QuantileStrategy,
)


class HeatmapStylerContext:
    """Раскрашивает территории, делегируя расчёт границ текущей стратегии.

    Контекст не знает, как именно считаются границы: алгоритм подменяется
    методом set_strategy() во время работы, без изменения кода контекста.
    """

    def __init__(
        self,
        strategy: ClassificationStrategy,
        palettes: PaletteRegistry,
        class_count: int = 5,
    ) -> None:
        if class_count < 2:
            raise ValueError("class_count должен быть не меньше 2")
        self._strategy: ClassificationStrategy = strategy
        self._palettes: PaletteRegistry = palettes
        self._class_count: int = class_count

    @property
    def strategy(self) -> ClassificationStrategy:
        return self._strategy

    def set_strategy(self, strategy: ClassificationStrategy) -> None:
        """Подменить алгоритм классификации (выбор пользователя в легенде карты)."""
        self._strategy = strategy

    def style(self, metrics: Sequence[RegionMetric]) -> HeatmapStyle:
        """Построить легенду и цвет каждой территории."""
        values = [m.value for m in metrics if m.value is not None]
        breaks = self._strategy.compute_breaks(values, self._class_count)
        class_total = max(len(breaks) - 1, 0)
        palette = self._palettes.get(self._strategy.palette_kind, max(class_total, 1))

        classes = tuple(
            ColorClass(
                index=i,
                lower=breaks[i],
                upper=breaks[i + 1],
                color=palette.colors[i],
                label=self._format_label(breaks[i], breaks[i + 1]),
            )
            for i in range(class_total)
        )

        regions: list[StyledRegion] = []
        for metric in metrics:
            if metric.value is None or not classes:
                regions.append(StyledRegion(metric.region_id, metric.name, metric.value,
                                            palette.no_data_color, None))
                continue
            index = self._class_index(breaks, metric.value, class_total)
            regions.append(StyledRegion(metric.region_id, metric.name, metric.value,
                                        classes[index].color, index))

        return HeatmapStyle(method_name=self._strategy.name, classes=classes, regions=tuple(regions))

    @staticmethod
    def _class_index(breaks: Sequence[float], value: float, class_total: int) -> int:
        """Номер класса для значения; верхняя граница включается в последний класс."""
        index = bisect_right(breaks, value) - 1
        return min(max(index, 0), class_total - 1)

    @staticmethod
    def _format_label(lower: float, upper: float) -> str:
        return f"{lower:,.1f} … {upper:,.1f}".replace(",", " ")


StrategyFactory = Callable[[], ClassificationStrategy]


class StrategyRegistry:
    """Каталог доступных стратегий для выпадающего списка «Метод классификации».

    Новая стратегия подключается вызовом register() — без правки контекста
    и существующих стратегий (принцип открытости/закрытости).
    """

    def __init__(self) -> None:
        self._factories: dict[str, StrategyFactory] = {}

    def register(self, key: str, factory: StrategyFactory) -> None:
        if key in self._factories:
            raise ValueError(f"стратегия '{key}' уже зарегистрирована")
        self._factories[key] = factory

    def create(self, key: str) -> ClassificationStrategy:
        try:
            return self._factories[key]()
        except KeyError as error:
            raise KeyError(f"неизвестная стратегия '{key}'") from error

    def keys(self) -> list[str]:
        return list(self._factories)


def default_registry() -> StrategyRegistry:
    """Реестр со стратегиями, доступными пользователю по умолчанию."""
    registry = StrategyRegistry()
    registry.register("equal", EqualIntervalStrategy)
    registry.register("quantile", QuantileStrategy)
    registry.register("diverging", DivergingStrategy)
    return registry
