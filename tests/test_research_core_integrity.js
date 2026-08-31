/* Regression tests for the validator's integrity checks.

   These exist because the original QA fixture was degenerate: every round was
   C vs C at gamma = 0, so every outcome had probability 1 and the random-draw
   replay check — one of the console's main guarantees — could never fail. The
   fixtures now contain probabilistic rounds, and these tests fail if that
   property is ever lost. */
const assert = require("assert");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const ResearchCore = require(path.join(root, "research_core.js"));
const EWLCore = require(path.join(root, "ewl_core.js"));

const load = name => JSON.parse(fs.readFileSync(path.join(root, "tests/fixtures", name), "utf8"));
const clone = record => JSON.parse(JSON.stringify(record));
const fixtures = ["researcher_valid_session.json", "researcher_valid_session_two.json"].map(load);

// Both fixtures are valid to begin with.
for (const record of fixtures) {
    const result = ResearchCore.validateRecord(record);
    assert.ok(result.valid, `${record.session_id} should validate: ${result.errors.join("; ")}`);
}

// The fixtures must retain probabilistic rounds, or the replay check is vacuous.
for (const record of fixtures) {
    const probabilistic = record.events.filter(e => Math.max(...Object.values(e.probabilities)) < 1);
    assert.ok(probabilistic.length >= 4,
        `${record.session_id} needs probabilistic rounds to exercise replay; found ${probabilistic.length}`);
}

// Tampering the random draw on a probabilistic round must be caught.
{
    const record = clone(fixtures[0]);
    const index = record.events.findIndex(e => Math.max(...Object.values(e.probabilities)) < 1);
    const event = record.events[index];
    const original = event.measured_outcome;
    event.random_draw = event.random_draw < 0.5 ? 0.95 : 0.05;
    assert.notStrictEqual(EWLCore.sample(event.probabilities, event.random_draw), original,
        "the substituted draw must select a different outcome for this test to mean anything");
    const result = ResearchCore.validateRecord(record);
    assert.ok(!result.valid, "a tampered random draw must be rejected");
    assert.ok(result.errors.some(e => /does not reproduce/.test(e)), result.errors.join("; "));
}

// coupling is written by study.js and must be present and consistent with gamma.
{
    const missing = clone(fixtures[0]);
    missing.events.forEach(event => delete event.coupling);
    assert.ok(!ResearchCore.validateRecord(missing).valid, "a record without coupling must be rejected");

    const mismatched = clone(fixtures[0]);
    mismatched.events[0].coupling = mismatched.events[0].coupling === "low" ? "high" : "low";
    const result = ResearchCore.validateRecord(mismatched);
    assert.ok(!result.valid, "coupling inconsistent with gamma must be rejected");
    assert.ok(result.errors.some(e => /does not match declared coupling/.test(e)), result.errors.join("; "));
}

// Flattened export rows must never contain a column that is empty for every row.
{
    const rows = ResearchCore.flattenEvents(fixtures);
    const fields = ["protocol", "session_id", "backend", "disclosure", "round", "coupling",
                    "gamma", "random_draw", "measured_outcome", "participant_payoff"];
    const alwaysEmpty = fields.filter(f => rows.every(r => r[f] === undefined || r[f] === null || r[f] === ""));
    assert.deepStrictEqual(alwaysEmpty, [], `export columns empty in every row: ${alwaysEmpty.join(", ")}`);
}

// The pure-JS SHA-256 fallback must agree with Node's crypto, including on the
// real canonical record, or file:// participants produce unverifiable data.
{
    const Sha256Fallback = require(path.join(root, "sha256_fallback.js"));
    const crypto = require("crypto");
    const vectors = ["", "abc", "a".repeat(55), "a".repeat(56), "a".repeat(64), "héllo wörld 🌍"];
    for (const vector of vectors) {
        assert.strictEqual(Sha256Fallback.hex(vector),
            crypto.createHash("sha256").update(vector, "utf8").digest("hex"),
            `SHA-256 fallback mismatch for a ${vector.length}-char input`);
    }
    for (const record of fixtures) {
        const canonical = ResearchCore.canonicalString(record);
        assert.strictEqual(Sha256Fallback.hex(canonical), record.integrity.sha256,
            `${record.session_id}: fallback hash must reproduce the stored integrity hash`);
    }
}

console.log("Research console integrity checks passed.");
