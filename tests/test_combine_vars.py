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


class CombineVarsNodeTests(unittest.TestCase):
    def test_combines_vars_in_input_order(self):
        node = nodes.ArtemKo7vComplexPromptCombineVars()

        result = node.combine_vars(
            {"subject": "Ada", "style": "sketch"},
            vars_2={"style": "cinematic", "city": "London"},
            vars_3={"subject": "Grace"},
        )

        self.assertEqual(
            result,
            ({"subject": "Grace", "style": "cinematic", "city": "London"},),
        )

    def test_skips_unconnected_optional_inputs(self):
        node = nodes.ArtemKo7vComplexPromptCombineVars()

        result = node.combine_vars({"subject": "Ada"}, vars_2=None)

        self.assertEqual(result, ({"subject": "Ada"},))

    def test_does_not_mutate_input_vars(self):
        node = nodes.ArtemKo7vComplexPromptCombineVars()
        first_vars = {"subject": "Ada"}

        node.combine_vars(first_vars, vars_2={"style": "cinematic"})

        self.assertEqual(first_vars, {"subject": "Ada"})

    def test_declares_only_first_input_in_backend_schema(self):
        input_types = nodes.ArtemKo7vComplexPromptCombineVars.INPUT_TYPES()

        self.assertEqual(
            input_types,
            {
                "required": {
                    "vars_1": (nodes.ARTEMKO7V_COMPLEX_PROMPT_VARS,),
                },
            },
        )


if __name__ == "__main__":
    unittest.main()
