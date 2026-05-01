import json
import os
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
    "ArtemKo7vComplexPromptEmptyString": ArtemKo7vComplexPromptEmptyString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ArtemKo7vComplexPromptEmptyString": "Complex Prompt Empty String",
}
