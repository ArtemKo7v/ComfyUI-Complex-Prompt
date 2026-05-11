import atexit
import importlib
import random
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


class ParseJSONVarsTests(unittest.TestCase):
    def test_creates_vars_from_string_and_number_values(self):
        result = nodes.parse_json_vars(
            '{"name": "Ada", "age": 37, "score": 9.5}',
            seed=1,
        )

        self.assertEqual(result, {"name": "Ada", "age": 37, "score": 9.5})

    def test_accepts_object_body_without_outer_braces(self):
        result = nodes.parse_json_vars(
            '"name": "Ada", "age": 37',
            seed=1,
        )

        self.assertEqual(result, {"name": "Ada", "age": 37})

    def test_empty_json_text_creates_empty_vars_like_empty_choices(self):
        result = nodes.parse_json_vars("", seed=1)

        self.assertEqual(result, {})

    def test_extends_existing_vars_and_overwrites_matching_keys(self):
        result = nodes.parse_json_vars(
            '{"name": "Ada", "age": 37}',
            seed=1,
            vars={"name": "Grace", "city": "London"},
        )

        self.assertEqual(result, {"name": "Ada", "city": "London", "age": 37})

    def test_selects_random_item_from_string_or_number_arrays(self):
        seed = 42
        expected_color = random.Random(seed).choice(["red", "green", "blue"])
        rng = random.Random(seed)
        rng.choice(["red", "green", "blue"])
        expected_size = rng.choice([1, 2, 3])

        result = nodes.parse_json_vars(
            '{"color": ["red", "green", "blue"], "size": [1, 2, 3]}',
            seed=seed,
        )

        self.assertEqual(result, {"color": expected_color, "size": expected_size})

    def test_ignores_unsupported_values(self):
        result = nodes.parse_json_vars(
            """
            {
              "enabled": true,
              "empty": [],
              "missing": null,
              "object": {"value": "nested"},
              "mixed": ["ok", false],
              "valid": "kept"
            }
            """,
            seed=1,
        )

        self.assertEqual(result, {"valid": "kept"})

    def test_rejects_invalid_json(self):
        with self.assertRaisesRegex(ValueError, "Invalid JSON"):
            nodes.parse_json_vars("{", seed=1)

    def test_rejects_non_object_json(self):
        with self.assertRaisesRegex(ValueError, "JSON must be an object"):
            nodes.parse_json_vars('["name", "Ada"]', seed=1)


class ParseJSONNodeTests(unittest.TestCase):
    def test_node_returns_vars_tuple(self):
        node = nodes.ArtemKo7vComplexPromptParseJSON()

        result = node.parse_json('{"name": "Ada"}', seed=1)

        self.assertEqual(result, ({"name": "Ada"},))

    def test_json_text_input_matches_choices_text_widget_behavior(self):
        json_text_config = nodes.ArtemKo7vComplexPromptParseJSON.INPUT_TYPES()[
            "required"
        ]["json_text"][1]
        choices_config = nodes.ArtemKo7vComplexPromptSetVariableByChoice.INPUT_TYPES()[
            "required"
        ]["choices"][1]

        self.assertEqual(json_text_config, choices_config)


if __name__ == "__main__":
    unittest.main()
