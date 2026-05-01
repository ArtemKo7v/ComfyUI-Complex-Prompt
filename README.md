# ComfyUI-Complex-Prompt
ComfyUI node for working with complex prompts with support for variables, randomness, and basic logic.

## Nodes

### Complex Prompt

Takes a multiline text prompt and expands dynamic prompt variants using `dynamicprompts`.
It can also accept optional `ComplexPromptVars` input and replace `$variable_name`
tokens after dynamic prompt expansion.

Example:

```text
a {red|green|blue} car
```

Outputs one randomly selected variant, such as:

```text
a green car
```

With variables:

```text
$person in a {red|green|blue} car
```

If `person` exists in `vars`, `$person` is replaced with its value.
Variable tokens are preserved while `dynamicprompts` is parsing the prompt.
The `seed` input is randomized after generation and is passed to `dynamicprompts`.

### Complex Prompt Set Variable

Creates or extends an `ComplexPromptVars` object.

- `vars` is optional. If it is not connected, the node creates a new object.
- `variable_name` is the key.
- `value` is multiline text expanded through `dynamicprompts`, then `$variable_name`
  tokens are replaced from the input `vars` before it is stored.
- `condition` is optional. If it is set, the variable is only stored when the
  expression evaluates to true.
- `seed` is randomized after generation and is passed to `dynamicprompts`.
- `wasSet` is true when the variable was stored and false when the condition
  prevented the update.

Condition example:

```text
(($var1 == "1") && ($var2 == "2")) || ($var3 < 10)
```

Conditions are evaluated with `simpleeval`. `$variable` tokens are resolved from
the input `vars`; missing variables make the condition false.

## Configuration

The configuration file is stored at:

```text
ComfyUI/user/default/ComfyUI-Complex-Prompt/config.json
```
