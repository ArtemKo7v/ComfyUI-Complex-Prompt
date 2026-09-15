import { app } from "../../scripts/app.js";

const NODE_TYPE = "ArtemKo7vComplexPromptCombineVars";
const VARS_PREFIX = "vars_";
const MAX_VAR_INDEX = 64;

function varsIndex(name) {
    const match = new RegExp(`^${VARS_PREFIX}(\\d+)$`).exec(name ?? "");
    return match ? Number(match[1]) : null;
}

function varsInputs(node) {
    return (node.inputs ?? [])
        .map((input) => ({ input, index: varsIndex(input.name) }))
        .filter((entry) => entry.index !== null)
        .sort((left, right) => left.index - right.index);
}

function resetDynamicInputs(node) {
    for (let index = (node.inputs?.length ?? 0) - 1; index >= 0; index -= 1) {
        if ((varsIndex(node.inputs[index].name) ?? 0) >= 2) {
            node.removeInput(index);
        }
    }
}

function markDirty(node) {
    node.setSize?.(node.computeSize?.() ?? node.size);
    app.graph?.setDirtyCanvas?.(true, true);
}

function addInput(node, index) {
    if (!node.inputs?.some((input) => input.name === `${VARS_PREFIX}${index}`)) {
        node.addInput(`${VARS_PREFIX}${index}`, "ArtemKo7vComplexPromptVars");
    }
}

function removeLastInput(node, entry) {
    node.removeInput(node.inputs.indexOf(entry.input));
}

function normalize(node) {
    if (node.__combineVarsUpdating) {
        return;
    }
    node.__combineVarsUpdating = true;
    try {
        let inputs = varsInputs(node);
        if (inputs.length === 0) {
            addInput(node, 1);
            inputs = varsInputs(node);
        }

        let last = inputs.at(-1);
        if (last.input.link != null && last.index < MAX_VAR_INDEX) {
            addInput(node, last.index + 1);
            inputs = varsInputs(node);
        }

        while (inputs.length > 1) {
            last = inputs.at(-1);
            const previous = inputs.at(-2);
            if (last.input.link != null || previous.input.link != null) {
                break;
            }
            removeLastInput(node, last);
            inputs = varsInputs(node);
        }
    } finally {
        node.__combineVarsUpdating = false;
    }
}

function restoreInputs(node, data) {
    const savedIndexes = (data?.inputs ?? [])
        .map((input) => varsIndex(input.name))
        .filter((index) => index !== null)
        .sort((left, right) => left - right);
    const highestIndex = Math.min(savedIndexes.at(-1) ?? 1, MAX_VAR_INDEX);
    for (let index = 2; index <= highestIndex; index += 1) {
        addInput(node, index);
    }
}

app.registerExtension({
    name: "ArtemKo7v.ComplexPrompt.CombineVars",
    nodeCreated(node) {
        if (node.constructor.type !== NODE_TYPE) {
            return;
        }

        const originalOnConfigure = node.onConfigure;
        node.onConfigure = function (data) {
            restoreInputs(this, data);
            originalOnConfigure?.apply(this, arguments);
            restoreInputs(this, data);
            normalize(this);
        };

        const originalOnConnectionsChange = node.onConnectionsChange;
        node.onConnectionsChange = function () {
            originalOnConnectionsChange?.apply(this, arguments);
            normalize(this);
            markDirty(this);
        };

        resetDynamicInputs(node);
        normalize(node);
    },
});
