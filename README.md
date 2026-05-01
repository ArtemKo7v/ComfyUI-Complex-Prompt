# ComfyUI-Complex-Prompt
ComfyUI node for working with complex prompts with support for variables, randomness, and basic logic.

## Nodes

### Complex Prompt

Takes a multiline text prompt and expands dynamic prompt variants using `dynamicprompts`.

Example:

```text
a {red|green|blue} car
```

Outputs one randomly selected variant, such as:

```text
a green car
```

### Complex Prompt Set Variable

Creates or extends an `ArtemKo7vComplexPromptVars` object.

- `vars` is optional. If it is not connected, the node creates a new object.
- `variable_name` is the key.
- `value` is multiline text expanded through `dynamicprompts` before it is stored.

## Configuration

The configuration file is stored at:

```text
ComfyUI/user/default/ComfyUI-Complex-Prompt/config.json
```
