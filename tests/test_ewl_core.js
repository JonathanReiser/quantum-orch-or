const assert = require("node:assert/strict");
const EWL = require("../ewl_core.js");

function approximately(actual, expected, tolerance = 1e-10) {
    assert.ok(Math.abs(actual - expected) <= tolerance, `${actual} != ${expected}`);
}

for (const first of ["C", "D", "Q"]) {
    for (const second of ["C", "D", "Q"]) {
        const probabilities = EWL.distribution(first, second, Math.PI / 3);
        approximately(Object.values(probabilities).reduce((sum, value) => sum + value, 0), 1);
    }
}

assert.deepEqual(EWL.distribution("C", "C", 0), { CC: 1, CD: 0, DC: 0, DD: 0 });
assert.deepEqual(EWL.distribution("D", "C", 0), { CC: 0, CD: 0, DC: 1, DD: 0 });
assert.deepEqual(EWL.distribution("Q", "D", Math.PI / 2), { CC: 0, CD: 0, DC: 1, DD: 0 });

const firstRandom = EWL.mulberry32(42);
const secondRandom = EWL.mulberry32(42);
for (let index = 0; index < 20; index += 1) approximately(firstRandom(), secondRandom());

console.log("EWL browser core checks passed.");
