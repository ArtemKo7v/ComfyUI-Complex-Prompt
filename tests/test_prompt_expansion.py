import atexit
import importlib
import shutil
import sys
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_RUNTIME_DIR = PROJECT_ROOT / ".test-runtime"
atexit.register(lambda: shutil.rmtree(TEST_RUNTIME_DIR, ignore_errors=True))
sys.path.insert(0, str(PROJECT_ROOT))
with patch("os.getcwd", return_value=str(TEST_RUNTIME_DIR)):
    nodes = importlib.import_module("nodes")


class PromptExpansionTests(unittest.TestCase):
    def setUp(self):
        self.prompt = nodes.ArtemKo7vComplexPrompt()
        self.variable = nodes.ArtemKo7vComplexPromptSetVariable()
        self.choice = nodes.ArtemKo7vComplexPromptSetVariableByChoice()
        self.combine = nodes.ArtemKo7vComplexPromptCombineVars()

    def test_single_option_and_empty_groups_are_expanded(self):
        for source, expected in [
            ("before {value1} after", "before value1 after"),
            ("{{{value1}}}", "value1"),
            ("before {} after", "before  after"),
        ]:
            with self.subTest(source=source):
                self.assertEqual(self.prompt.generate_prompt(source, 1), (expected,))

    def test_variants_introduced_by_selected_variable_are_expanded(self):
        variables = {"var1": "{value1|value2}", "var2": "{{value3|value4}}"}
        for seed in range(10):
            with self.subTest(seed=seed):
                result = self.prompt.generate_prompt(
                    "before {$var1|$var2} after", seed, variables
                )[0]
                self.assertIn(result, [f"before value{i} after" for i in range(1, 5)])
                self.assertEqual(
                    result,
                    self.prompt.generate_prompt(
                        "before {$var1|$var2} after", seed, variables
                    )[0],
                )

    def test_variable_references_across_combined_branches(self):
        first, _ = self.variable.set_variable("var1", "{$source1}", "", 1)
        second, _ = self.variable.set_variable("var2", "{{$source2}}", "", 2)
        sources = {"source1": "{value1|value2}", "source2": "{value3|value4}"}
        combined = self.combine.combine_vars(first, vars_2=second, vars_3=sources)[0]
        selected, _ = self.variable.set_variable(
            "selected", "{$var1|$var2}", "", 3, vars=combined
        )
        intermediate = self.prompt.generate_prompt("{$selected}", 4, selected)[0]
        result = self.prompt.generate_prompt(f"before {{{intermediate}}} after", 5)[0]
        self.assertIn(result, [f"before value{i} after" for i in range(1, 5)])
        self.assertEqual(sources["source1"], "{value1|value2}")

    def test_both_variable_nodes_expand_referenced_values_before_trimming(self):
        variables = {"source": "{value1|value2}", "kind": "test"}
        direct, was_set = self.variable.set_variable(
            "result", "  {$source}  ", "", 1, trim=True, vars=variables
        )
        chosen, choice_was_set = self.choice.set_variable_by_choice(
            "result", "kind", '{"test": "  {$source}  "}', 1,
            trim=True, vars=variables,
        )
        self.assertTrue(was_set)
        self.assertTrue(choice_was_set)
        self.assertIn(direct["result"], ["value1", "value2"])
        self.assertEqual(chosen["result"], direct["result"])
        self.assertNotIn("result", variables)

    def test_unknown_and_cyclic_references_remain_visible(self):
        for variables, source, expected in [
            ({}, "{$missing}", "$missing"),
            ({"a": "$a"}, "$a", "$a"),
            ({"a": "$b", "b": "$a"}, "$a", "$a"),
            ({"a": "prefix $a"}, "$a", "prefix $a"),
            ({"a": "$b", "b": "$missing"}, "$a", "$missing"),
        ]:
            with self.subTest(variables=variables):
                self.assertEqual(
                    self.prompt.generate_prompt(source, 1, variables), (expected,)
                )

    def test_plain_substitutions_preserve_whitespace_and_numeric_values(self):
        self.assertEqual(
            self.prompt.generate_prompt(
                "  $name  $count $empty  ", 1,
                {"name": "Ada", "count": 3, "empty": ""},
            ),
            ("  Ada  3   ",),
        )

    def test_existing_choice_seed_behavior_is_preserved(self):
        source = "{red|blue} {$var1|$var2}"
        variables = {"var1": "first", "var2": "second"}
        for seed in range(10):
            expected = nodes.apply_vars(
                nodes.generate_dynamic_prompt(source, seed), variables
            )
            self.assertEqual(
                self.prompt.generate_prompt(source, seed, variables), (expected,)
            )


if __name__ == "__main__":
    unittest.main()
