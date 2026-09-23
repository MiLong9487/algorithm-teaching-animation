from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

from manim import AnimationGroup, FadeOut, Rectangle, RIGHT, Scene, Square, Text, Transform, VGroup


RUNNER_PATH = Path(__file__).resolve().parents[1] / "scripts" / "run_layout_audit.py"
SPEC = importlib.util.spec_from_file_location("layout_runner_parity", RUNNER_PATH)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)

AUDITOR_PATH = RUNNER_PATH.with_name("visible_layout_audit.py")
AUDITOR_SPEC = importlib.util.spec_from_file_location("visible_layout_manim_parity", AUDITOR_PATH)
assert AUDITOR_SPEC is not None and AUDITOR_SPEC.loader is not None
auditor = importlib.util.module_from_spec(AUDITOR_SPEC)
sys.modules[AUDITOR_SPEC.name] = auditor
AUDITOR_SPEC.loader.exec_module(auditor)


class LayoutRunnerManimParityTests(unittest.TestCase):
    def test_transform_of_group_child_does_not_readd_or_dissolve_group(self) -> None:
        scene = Scene()
        child = Square()
        graph = VGroup(child)
        scene.add(graph)

        runner.dry_play(scene, Transform(child, child.copy().shift(RIGHT)))

        self.assertEqual(scene.mobjects, [graph])
        self.assertIn(child, graph.submobjects)
        self.assertAlmostEqual(child.get_center()[0], 1.0)

    def test_remover_cleanup_still_follows_real_scene_restructuring(self) -> None:
        scene = Scene()
        departing, remaining = Square(), Square().shift(RIGHT)
        graph = VGroup(departing, remaining)
        scene.add(graph)

        runner.dry_play(scene, FadeOut(departing))

        self.assertNotIn(departing, scene.get_mobject_family_members())
        self.assertIn(remaining, scene.get_mobject_family_members())
        self.assertNotIn(graph, scene.mobjects)

    def test_composition_is_not_flattened_into_independent_scene_adds(self) -> None:
        scene = Scene()
        first, second = Square(), Square().shift(RIGHT)
        graph = VGroup(first, second)
        scene.add(graph)

        runner.dry_play(
            scene,
            AnimationGroup(
                Transform(first, first.copy().shift(RIGHT)),
                Transform(second, second.copy().shift(RIGHT)),
            ),
        )

        self.assertAlmostEqual(first.get_center()[0], 1.0)
        self.assertAlmostEqual(second.get_center()[0], 2.0)
        self.assertEqual(len(scene.get_mobject_family_members()), len(set(scene.get_mobject_family_members())))

    def test_real_text_glyphs_require_strictly_higher_z_index(self) -> None:
        scene = Scene()
        panel = Rectangle(width=2, height=1).set_fill(opacity=1)
        label = Text("A")
        scene.add(VGroup(panel, label))

        equal_z = auditor.audit_scene_visible_mobjects(scene)
        self.assertIn("text-occlusion", [finding.relation for finding in equal_z.findings])

        label.set_z_index(1)
        higher_z = auditor.audit_scene_visible_mobjects(scene)
        self.assertNotIn("text-occlusion", [finding.relation for finding in higher_z.findings])


if __name__ == "__main__":
    unittest.main()
