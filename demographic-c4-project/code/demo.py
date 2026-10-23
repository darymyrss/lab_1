"""Демонстрация динамической подмены стратегии классификации тепловой карты.

Значения — условные демонстрационные данные (изменение численности
населения муниципалитетов за период, %), а не официальная статистика.
"""
from __future__ import annotations

from heatmap_styler import (
    HeatmapStyle,
    HeatmapStylerContext,
    PaletteRegistry,
    RegionMetric,
    default_registry,
)

DEMO_METRICS: list[RegionMetric] = [
    RegionMetric("45000000", "Городской округ А", 4.8),
    RegionMetric("46000000", "Городской округ Б", 2.1),
    RegionMetric("46601000", "Муниципальный район В", -1.3),
    RegionMetric("46602000", "Муниципальный район Г", -3.9),
    RegionMetric("46603000", "Муниципальный округ Д", -6.7),
    RegionMetric("46604000", "Муниципальный район Е", 0.4),
    RegionMetric("46605000", "Муниципальный район Ж", -2.2),
    RegionMetric("46606000", "Муниципальный округ З", None),
]


def print_style(style: HeatmapStyle) -> None:
    print(f"\nМетод: {style.method_name}")
    for color_class in style.classes:
        print(f"  класс {color_class.index}: {color_class.label:<20} {color_class.color}")
    for region in style.regions:
        value = "нет данных" if region.value is None else f"{region.value:+.1f} %"
        print(f"  {region.name:<24} {value:>11}  -> {region.color}")


def main() -> None:
    registry = default_registry()
    context = HeatmapStylerContext(registry.create("equal"), PaletteRegistry(), class_count=4)
    print_style(context.style(DEMO_METRICS))

    # Пользователь меняет метод в легенде карты — подменяется только стратегия.
    for key in ("quantile", "diverging"):
        context.set_strategy(registry.create(key))
        print_style(context.style(DEMO_METRICS))


if __name__ == "__main__":
    main()
