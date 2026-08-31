const assert = require("node:assert/strict");
const crypto = require("node:crypto");
const fs = require("node:fs");
const EWL = require("../ewl_core.js");
const Research = require("../research_core.js");

const PAYOFFS = { CC: [3, 3], CD: [0, 5], DC: [5, 0], DD: [1, 1] };

function makeRecord(sessionId, backend, disclosure, choiceOffset = 0) {
    const strategies = ["C", "D", "Q"];
    const events = [];
    let participantTotal = 0;
    let opponentTotal = 0;
    for (let index = 0; index < 12; index += 1) {
        const participant = strategies[(index + choiceOffset) % 3];
        const opponent = strategies[(index + 1) % 3];
        const gamma = [0, Math.PI / 4, Math.PI / 2][index % 3];
        const probabilities = EWL.distribution(participant, opponent, gamma);
        const randomDraw = 0.25;
        const outcome = EWL.sample(probabilities, randomDraw);
        const payoff = PAYOFFS[outcome];
        participantTotal += payoff[0];
        opponentTotal += payoff[1];
        events.push({
            round: index + 1,
            recorded_at: "2026-08-30T12:00:00.000Z",
            response_time_ms: 500 + index,
            participant_strategy: participant,
            opponent_strategy: opponent,
            coupling: ["low", "medium", "high"][index % 3],
            gamma,
            backend,
            disclosure,
            probabilities,
            random_draw: randomDraw,
            measured_outcome: outcome,
            participant_payoff: payoff[0],
            opponent_payoff: payoff[1],
            cumulative_participant_payoff: participantTotal,
            cumulative_opponent_payoff: opponentTotal
        });
    }
    return {
        protocol: Research.PROTOCOL,
        session_id: sessionId,
        created_at: "2026-08-30T12:00:00.000Z",
        consent: { adult_confirmed: true, voluntary_local_pilot_confirmed: true },
        assignments: { backend, disclosure },
        seeds: { assignment: 1, schedule: 2, outcome: 3 },
        random_source: "test fixture",
        schedule: [],
        current_round: 12,
        totals: { participant: participantTotal, opponent: opponentTotal },
        events,
        completed_at: "2026-08-30T12:05:00.000Z",
        integrity: { algorithm: "SHA-256", sha256: "placeholder" },
        interpretation_boundary: "test"
    };
}

const records = [
    makeRecord("session-classical-neutral", "classical-correlated", "neutral", 0),
    makeRecord("session-classical-labeled", "classical-correlated", "mechanism-labeled", 1),
    makeRecord("session-ewl-neutral", "ewl-simulator", "neutral", 2),
    makeRecord("session-ewl-labeled", "ewl-simulator", "mechanism-labeled", 0)
];

for (const record of records) assert.deepEqual(Research.validateRecord(record), { valid: true, errors: [] });

const tampered = JSON.parse(JSON.stringify(records[0]));
tampered.events[0].participant_payoff = 99;
assert.equal(Research.validateRecord(tampered).valid, false);
assert.ok(Research.validateRecord(tampered).errors.some(error => error.includes("payoff mismatch")));

const summary = Research.summarize(records);
assert.equal(summary.sessions, 4);
assert.equal(summary.rounds, 48);
assert.deepEqual(summary.arms.map(arm => arm.sessions), [1, 1, 1, 1]);
assert.ok(summary.effects.backend_ewl_minus_classical);
assert.ok(summary.effects.disclosure_labeled_minus_neutral);
assert.equal(Research.flattenEvents(records).length, 48);
assert.equal(JSON.parse(Research.canonicalString(records[0])).integrity, null);
assert.equal(Research.median([1, 7, 3, 5]), 4);

const browserFixture = JSON.parse(fs.readFileSync("tests/fixtures/researcher_valid_session.json", "utf8"));
assert.deepEqual(Research.validateRecord(browserFixture), { valid: true, errors: [] });
const fixtureHash = crypto.createHash("sha256").update(Research.canonicalString(browserFixture)).digest("hex");
assert.equal(fixtureHash, browserFixture.integrity.sha256);

console.log("Research console core checks passed.");
