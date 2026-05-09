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


class SetVariableNodeTests(unittest.TestCase):
    def test_unset_value_is_stored_as_empty_string(self):
        node = nodes.ArtemKo7vComplexPromptSetVariable()

        with patch.object(nodes, "get_prompt_generator") as get_prompt_generator:
            result = node.set_variable("name", None, "", seed=1)

        get_prompt_generator.assert_not_called()
        self.assertEqual(result, ({"name": ""}, True))

    def test_empty_value_does_not_call_dynamic_prompt_generator(self):
        node = nodes.ArtemKo7vComplexPromptSetVariable()

        with patch.object(nodes, "get_prompt_generator") as get_prompt_generator:
            result = node.set_variable("name", "", "", seed=1)

        get_prompt_generator.assert_not_called()
        self.assertEqual(result, ({"name": ""}, True))

    def test_empty_value_can_be_applied_to_prompt(self):
        prompt = nodes.apply_vars("Hello<$name>", {"name": ""})

        self.assertEqual(prompt, "Hello<>")

    def test_trim_removes_surrounding_whitespace_before_storing_value(self):
        node = nodes.ArtemKo7vComplexPromptSetVariable()

        result = node.set_variable("name", "\n  Ada Lovelace \t", "", seed=1, trim=True)

        self.assertEqual(result, ({"name": "Ada Lovelace"}, True))

    def test_trim_false_preserves_surrounding_whitespace(self):
        node = nodes.ArtemKo7vComplexPromptSetVariable()

        result = node.set_variable("name", "\n  Ada Lovelace \t", "", seed=1)

        self.assertEqual(result, ({"name": "\n  Ada Lovelace \t"}, True))

    def test_trim_is_applied_after_variable_replacement(self):
        node = nodes.ArtemKo7vComplexPromptSetVariable()

        result = node.set_variable(
            "greeting",
            " $name ",
            "",
            seed=1,
            trim=True,
            vars={"name": "Ada"},
        )

        self.assertEqual(result, ({"name": "Ada", "greeting": "Ada"}, True))


class ComplexPromptNodeTests(unittest.TestCase):
    def test_plain_text_with_variable_does_not_call_dynamic_prompt_generator(self):
        node = nodes.ArtemKo7vComplexPrompt()

        with patch.object(nodes, "get_prompt_generator") as get_prompt_generator:
            result = node.generate_prompt(
                "test $anyvar test",
                seed=1,
                vars={"anyvar": ""},
            )

        get_prompt_generator.assert_not_called()
        self.assertEqual(result, ("test  test",))

    def test_dynamic_prompt_syntax_still_calls_generator(self):
        generator = unittest.mock.Mock()
        generator.generate.return_value = ["test red $anyvar"]

        with patch.object(nodes, "get_prompt_generator", return_value=generator):
            result = nodes.generate_dynamic_prompt("test {red|blue} $anyvar", seed=5)

        generator.generate.assert_called_once()
        self.assertEqual(result, "test red $anyvar")


if __name__ == "__main__":
    unittest.main()
