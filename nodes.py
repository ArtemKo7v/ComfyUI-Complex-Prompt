import json
import os
import re
from pathlib import Path
from typing import Any


USER_DIR = Path(os.getcwd()) / "user" / "default"
CONFIG_DIR = USER_DIR / "ComfyUI-Complex-Prompt"
CONFIG_PATH = CONFIG_DIR / "config.json"
DEFAULT_CONFIG: dict[str, Any] = {}
CONDITION_FUNCTIONS = {
    "float": float,
    "int": int,
    "str": str,
}


def log(message: str) -> None:
    print(f"[ComfyUI-Complex-Prompt]: {message}")


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: Path, data: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def load_config() -> dict[str, Any]:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not CONFIG_PATH.exists():
        write_json(CONFIG_PATH, DEFAULT_CONFIG)
        log(f"Created config file at {CONFIG_PATH}")
        return DEFAULT_CONFIG.copy()

    log(f"Reading config from {CONFIG_PATH}")
    return read_json(CONFIG_PATH)


CONFIG = load_config()

ARTEMKO7V_COMPLEX_PROMPT_VARS = "ArtemKo7vComplexPromptVars"
VAR_PATTERN = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")

_PROMPT_GENERATOR = None


class ConditionValue:
    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

    def __repr__(self) -> str:
        return repr(str(self))

    def __bool__(self) -> bool:
        return bool(str(self))

    def __int__(self) -> int:
        return int(str(self))

    def __float__(self) -> float:
        return float(str(self))

    def __eq__(self, other: Any) -> bool:
        return str(self) == str(self.unwrap(other))

    def __ne__(self, other: Any) -> bool:
        return not self == other

    def __lt__(self, other: Any) -> bool:
        return self.compare(other, lambda left, right: left < right)

    def __le__(self, other: Any) -> bool:
        return self.compare(other, lambda left, right: left <= right)

    def __gt__(self, other: Any) -> bool:
        return self.compare(other, lambda left, right: left > right)

    def __ge__(self, other: Any) -> bool:
        return self.compare(other, lambda left, right: left >= right)

    def unwrap(self, other: Any) -> Any:
        if isinstance(other, ConditionValue):
            return other.value

        return other

    def compare(self, other: Any, operation):
        other = self.unwrap(other)

        try:
            return operation(float(self), float(other))
        except (TypeError, ValueError):
            return operation(str(self), str(other))


def get_prompt_generator():
    global _PROMPT_GENERATOR

    if _PROMPT_GENERATOR is None:
        try:
            from dynamicprompts.generators import RandomPromptGenerator
        except ImportError as error:
            raise ImportError(
                "ComfyUI-Complex-Prompt requires the 'dynamicprompts' package. "
                "Install this extension's requirements.txt dependencies."
            ) from error

        _PROMPT_GENERATOR = RandomPromptGenerator()

    return _PROMPT_GENERATOR


def mask_vars(prompt: str) -> tuple[str, dict[str, str]]:
    placeholders: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        placeholder = f"AK7VCOMPLEXPROMPTVAR{len(placeholders)}TOKEN"
        placeholders[placeholder] = match.group(0)
        return placeholder

    return VAR_PATTERN.sub(replace, prompt), placeholders


def restore_vars(prompt: str, placeholders: dict[str, str]) -> str:
    for placeholder, variable in placeholders.items():
        prompt = prompt.replace(placeholder, variable)

    return prompt


def generate_dynamic_prompt(prompt: str, seed: int) -> str:
    masked_prompt, placeholders = mask_vars(prompt)
    generator = get_prompt_generator()
    prompts = generator.generate(masked_prompt, 1, seeds=seed)
    generated_prompt = prompts[0] if prompts else ""
    return restore_vars(generated_prompt, placeholders)



def apply_vars(prompt: str, vars: dict[str, str] | None = None) -> str:
    if not vars:
        return prompt

    def replace(match: re.Match[str]) -> str:
        variable_name = match.group(1)
        if variable_name not in vars:
            return match.group(0)

        return str(vars[variable_name])

    return VAR_PATTERN.sub(replace, prompt)


def normalize_condition(condition: str) -> str:
    normalized = VAR_PATTERN.sub(r"\1", condition)
    normalized = normalized.replace("&&", " and ")
    normalized = normalized.replace("||", " or ")
    normalized = re.sub(r"!(?!=)", " not ", normalized)
    return normalized


def should_set_variable(
    condition: str,
    vars: dict[str, str] | None = None,
) -> bool:
    condition = condition.strip()
    if not condition:
        return True

    try:
        from simpleeval import NameNotDefined, SimpleEval
    except ImportError as error:
        raise ImportError(
            "ComfyUI-Complex-Prompt conditional variables require the "
            "'simpleeval' package. Install this extension's requirements.txt "
            "dependencies."
        ) from error

    evaluator = SimpleEval(
        functions=CONDITION_FUNCTIONS,
        names={
            key: ConditionValue(value)
            for key, value in (vars or {}).items()
            if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key)
        },
    )

    try:
        return bool(evaluator.eval(normalize_condition(condition)))
    except NameNotDefined:
        return False


class ArtemKo7vComplexPrompt:
    CATEGORY = "ArtemKo7v"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "generate_prompt"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 18446744073709551615,
                        "control_after_generate": "randomize",
                    },
                ),
            },
            "optional": {
                "vars": (ARTEMKO7V_COMPLEX_PROMPT_VARS,),
            },
        }

    def generate_prompt(
        self,
        prompt: str,
        seed: int,
        vars: dict[str, str] | None = None,
    ):
        generated_prompt = generate_dynamic_prompt(prompt, seed)
        return (apply_vars(generated_prompt, vars),)


class ArtemKo7vComplexPropmptSetVariable:
    CATEGORY = "ArtemKo7v"
    RETURN_TYPES = (ARTEMKO7V_COMPLEX_PROMPT_VARS, "BOOLEAN")
    RETURN_NAMES = ("vars", "wasSet")
    FUNCTION = "set_variable"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "variable_name": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
                "value": (
                    "STRING",
                    {
                        "multiline": True,
                        "dynamicPrompts": False,
                    },
                ),
                "condition": (
                    "STRING",
                    {
                        "default": "",
                    },
                ),
                "seed": (
                    "INT",
                    {
                        "default": 0,
                        "min": 0,
                        "max": 18446744073709551615,
                        "control_after_generate": "randomize",
                    },
                ),
            },
            "optional": {
                "vars": (ARTEMKO7V_COMPLEX_PROMPT_VARS,),
            },
        }

    def set_variable(
        self,
        variable_name: str,
        value: str,
        condition: str,
        seed: int,
        vars: dict[str, str] | None = None,
    ):
        result = dict(vars or {})
        if not should_set_variable(condition, vars):
            return (result, False)

        generated_value = generate_dynamic_prompt(value, seed)
        result[variable_name] = apply_vars(generated_value, vars)
        return (result, True)


class ArtemKo7vComplexPromptEmptyString:
    CATEGORY = "ArtemKo7v"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("string",)
    FUNCTION = "get_empty_string"

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    def get_empty_string(self):
        return ("",)


NODE_CLASS_MAPPINGS = {
    "ArtemKo7vComplexPrompt": ArtemKo7vComplexPrompt,
    "ArtemKo7vComplexPropmptSetVariable": ArtemKo7vComplexPropmptSetVariable,
    "ArtemKo7vComplexPromptEmptyString": ArtemKo7vComplexPromptEmptyString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArtemKo7vComplexPrompt": "Complex Prompt",
    "ArtemKo7vComplexPropmptSetVariable": "Complex Prompt Set Variable",
    "ArtemKo7vComplexPromptEmptyString": "Complex Prompt Empty String",
}
