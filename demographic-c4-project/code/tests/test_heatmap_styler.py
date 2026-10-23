"""Модульные тесты компонента Heatmap Styler (запуск: python -m unittest)."""
from __future__ import annotations

import unittest
from collections.abc import Sequence

from heatmap_styler import (
    ClassificationStrategy,
    DivergingStrategy,
    EqualIntervalStrategy,
    HeatmapStylerContext,
    PaletteKind,
    PaletteRegistry,
    QuantileStrategy,
    RegionMetric,
    default_registry,
)

VALUES: list[float] = [-6.0, -2.0, 0.0, 1.0, 4.0]


class EqualIntervalTests(unittest.TestCase):
    def test_breaks_split_range_evenly(self) -> None:
        self.assertEqual(EqualIntervalStrategy().compute_breaks(VALUES, 5), [-6.0, -4.0, -2.0, 0.0, 2.0, 4.0])

    def test_constant_values_give_single_class(self) -> None:
        self.assertEqual(EqualIntervalStrategy().compute_breaks([3.0, 3.0], 4), [3.0, 3.0])

    def test_class_count_below_two_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            EqualIntervalStrategy().compute_breaks(VALUES, 1)


class QuantileTests(unittest.TestCase):
    def test_breaks_follow_order_statistics(self) -> None:
        self.assertEqual(QuantileStrategy().compute_breaks(VALUES, 4), [-6.0, -2.0, 0.0, 1.0, 4.0])

    def test_duplicate_breaks_are_removed(self) -> None:
        breaks = QuantileStrategy().compute_breaks([1.0, 1.0, 1.0, 5.0], 4)
        self.assertEqual(breaks, sorted(set(breaks)))


class DivergingTests(unittest.TestCase):
    def test_scale_is_symmetric_around_zero(self) -> None:
        breaks = DivergingStrategy().compute_breaks(VALUES, 4)
        self.assertEqual(breaks, [-6.0, -3.0, 0.0, 3.0, 6.0])
        self.assertIs(DivergingStrategy().palette_kind, PaletteKind.DIVERGING)


class ContextTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metrics = [
            RegionMetric("1", "A", -6.0),
            RegionMetric("2", "B", 4.0),
            RegionMetric("3", "C", None),
        ]
        self.context = HeatmapStylerContext(EqualIntervalStrategy(), PaletteRegistry(), class_count=4)

    def test_extreme_values_land_in_first_and_last_class(self) -> None:
        style = self.context.style(self.metrics)
        self.assertEqual(style.regions[0].class_index, 0)
        self.assertEqual(style.regions[1].class_index, 3)

    def test_region_without_data_gets_no_data_color(self) -> None:
        style = self.context.style(self.metrics)
        self.assertIsNone(style.regions[2].class_index)
        self.assertEqual(style.regions[2].color, "#D9D9D9")

    def test_strategy_can_be_swapped_at_runtime(self) -> None:
        first = self.context.style(self.metrics)
        self.context.set_strategy(DivergingStrategy())
        second = self.context.style(self.metrics)
        self.assertNotEqual(first.method_name, second.method_name)
        self.assertEqual(second.classes[-1].upper, 6.0)

    def test_all_regions_without_data(self) -> None:
        style = self.context.style([RegionMetric("1", "A", None)])
        self.assertEqual(style.classes, ())
        self.assertIsNone(style.regions[0].class_index)

    def test_new_strategy_needs_no_context_changes(self) -> None:
        class FixedBreaksStrategy(ClassificationStrategy):
            @property
            def name(self) -> str:
                return "Фиксированные границы"

            @property
            def palette_kind(self) -> PaletteKind:
                return PaletteKind.SEQUENTIAL

            def compute_breaks(self, values: Sequence[float], class_count: int) -> list[float]:
                return [-10.0, 0.0, 10.0]

        registry = default_registry()
        registry.register("fixed", FixedBreaksStrategy)
        self.context.set_strategy(registry.create("fixed"))
        style = self.context.style(self.metrics)
        self.assertEqual(len(style.classes), 2)
        self.assertEqual(style.regions[1].class_index, 1)


class RegistryTests(unittest.TestCase):
    def test_default_keys(self) -> None:
        self.assertEqual(default_registry().keys(), ["equal", "quantile", "diverging"])

    def test_unknown_key_raises(self) -> None:
        with self.assertRaises(KeyError):
            default_registry().create("jenks")


if __name__ == "__main__":
    unittest.main()
