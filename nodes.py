import json
import os
import re
from pathlib import Path
from typing import Any


USER_DIR = Path(os.getcwd()) / "user" / "default"
CONFIG_DIR = USER_DIR / "ComfyUI-Complex-Prompt"
CONFIG_PATH = CONFIG_DIR / "config.json"
DEFAULT_CONFIG: dict[str, Any] = {}


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

_PROMPT_GENERATOR = None


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


def generate_dynamic_prompt(prompt: str) -> str:
    generator = get_prompt_generator()
    prompts = generator.generate(prompt, 1)
    return prompts[0] if prompts else ""


def apply_vars(prompt: str, vars: dict[str, str] | None = None) -> str:
    if not vars:
        return prompt

    def replace(match: re.Match[str]) -> str:
        variable_name = match.group(1)
        if variable_name not in vars:
            return match.group(0)

        return str(vars[variable_name])

    return re.sub(r"\$([A-Za-z_][A-Za-z0-9_]*)", replace, prompt)


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
            },
            "optional": {
                "vars": (ARTEMKO7V_COMPLEX_PROMPT_VARS,),
            },
        }

    def generate_prompt(
        self,
        prompt: str,
        vars: dict[str, str] | None = None,
    ):
        generated_prompt = generate_dynamic_prompt(prompt)
        return (apply_vars(generated_prompt, vars),)


class ArtemKo7vComplexPropmptSetVariable:
    CATEGORY = "ArtemKo7v"
    RETURN_TYPES = (ARTEMKO7V_COMPLEX_PROMPT_VARS,)
    RETURN_NAMES = ("vars",)
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
            },
            "optional": {
                "vars": (ARTEMKO7V_COMPLEX_PROMPT_VARS,),
            },
        }

    def set_variable(
        self,
        variable_name: str,
        value: str,
        vars: dict[str, str] | None = None,
    ):
        result = dict(vars or {})
        generated_value = generate_dynamic_prompt(value)
        result[variable_name] = apply_vars(generated_value, vars)
        return (result,)


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
