/* Pure validation and descriptive-analysis helpers for EWL pilot records. */
(function exposeResearchCore(root, factory) {
    const ewl = typeof module !== "undefined" && module.exports ? require("./ewl_core.js") : root.EWLCore;
    const api = factory(ewl);
    if (typeof module !== "undefined" && module.exports) module.exports = api;
    if (root) root.ResearchCore = api;
}(typeof globalThis !== "undefined" ? globalThis : this, function createResearchCore(EWLCore) {
    "use strict";

    const PROTOCOL = "ewl-participant-pilot/v1";
    const BACKENDS = ["classical-correlated", "ewl-simulator"];
    const DISCLOSURES = ["neutral", "mechanism-labeled"];
    const STRATEGIES = ["C", "D", "Q"];
    // study.js declares exactly these couplings; gamma is derived from the name,
    // so a record whose gamma disagrees with its declared coupling has been
    // altered or mis-generated.
    const COUPLING_GAMMA = { low: 0, medium: Math.PI / 4, high: Math.PI / 2 };
    const PAYOFFS = { CC: [3, 3], CD: [0, 5], DC: [5, 0], DD: [1, 1] };

    function approximately(first, second, tolerance = 1e-9) {
        return Number.isFinite(first) && Number.isFinite(second) && Math.abs(first - second) <= tolerance;
    }

    function canonicalString(record) {
        const clone = JSON.parse(JSON.stringify(record));
        clone.integrity = null;
        return JSON.stringify(clone);
    }

    function validateRecord(record) {
        const errors = [];
        if (!record || typeof record !== "object" || Array.isArray(record)) {
            return { valid: false, errors: ["Record must be a JSON object."] };
        }
        if (record.protocol !== PROTOCOL) errors.push(`Unsupported protocol: ${record.protocol ?? "missing"}.`);
        if (typeof record.session_id !== "string" || record.session_id.length < 8) errors.push("Missing or invalid session_id.");
        if (!record.assignments || !BACKENDS.includes(record.assignments.backend)) errors.push("Invalid backend assignment.");
        if (!record.assignments || !DISCLOSURES.includes(record.assignments.disclosure)) errors.push("Invalid disclosure assignment.");
        if (!record.completed_at) errors.push("Session is incomplete: completed_at is missing.");
        if (!record.consent || record.consent.adult_confirmed !== true || record.consent.voluntary_local_pilot_confirmed !== true) {
            errors.push("Required consent flags are missing.");
        }
        if (!Array.isArray(record.events) || record.events.length !== 12) {
            errors.push("A complete session must contain exactly 12 events.");
            return { valid: false, errors };
        }

        let participantTotal = 0;
        let opponentTotal = 0;
        record.events.forEach((event, index) => {
            const prefix = `Round ${index + 1}`;
            if (event.round !== index + 1) errors.push(`${prefix}: non-sequential round number.`);
            if (!STRATEGIES.includes(event.participant_strategy) || !STRATEGIES.includes(event.opponent_strategy)) {
                errors.push(`${prefix}: invalid strategy.`);
                return;
            }
            if (event.backend !== record.assignments.backend || event.disclosure !== record.assignments.disclosure) {
                errors.push(`${prefix}: treatment assignment changed within session.`);
            }
            if (!(event.coupling in COUPLING_GAMMA)) {
                errors.push(`${prefix}: missing or unknown coupling.`);
            } else if (!approximately(event.gamma, COUPLING_GAMMA[event.coupling], 1e-9)) {
                errors.push(`${prefix}: gamma does not match declared coupling "${event.coupling}".`);
            }
            if (!Number.isFinite(event.response_time_ms) || event.response_time_ms < 0) errors.push(`${prefix}: invalid response time.`);
            if (!Number.isFinite(event.random_draw) || event.random_draw < 0 || event.random_draw >= 1) errors.push(`${prefix}: invalid random draw.`);
            if (!PAYOFFS[event.measured_outcome]) {
                errors.push(`${prefix}: invalid measured outcome.`);
                return;
            }
            let expected;
            try {
                expected = EWLCore.distribution(event.participant_strategy, event.opponent_strategy, event.gamma);
            } catch (error) {
                errors.push(`${prefix}: invalid EWL parameters.`);
                return;
            }
            for (const outcome of EWLCore.OUTCOMES) {
                if (!event.probabilities || !approximately(event.probabilities[outcome], expected[outcome])) {
                    errors.push(`${prefix}: stored probabilities do not reproduce.`);
                    break;
                }
            }
            if (Number.isFinite(event.random_draw) && EWLCore.sample(expected, event.random_draw) !== event.measured_outcome) {
                errors.push(`${prefix}: outcome does not reproduce from its random draw.`);
            }
            const payoff = PAYOFFS[event.measured_outcome];
            if (event.participant_payoff !== payoff[0] || event.opponent_payoff !== payoff[1]) errors.push(`${prefix}: payoff mismatch.`);
            participantTotal += payoff[0];
            opponentTotal += payoff[1];
            if (event.cumulative_participant_payoff !== participantTotal || event.cumulative_opponent_payoff !== opponentTotal) {
                errors.push(`${prefix}: cumulative payoff mismatch.`);
            }
        });
        if (!record.totals || record.totals.participant !== participantTotal || record.totals.opponent !== opponentTotal) {
            errors.push("Session totals do not match event totals.");
        }
        return { valid: errors.length === 0, errors };
    }

    function median(values) {
        if (!values.length) return null;
        const sorted = values.slice().sort((a, b) => a - b);
        const middle = Math.floor(sorted.length / 2);
        return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
    }

    function armKey(backend, disclosure) {
        return `${backend}|${disclosure}`;
    }

    function summarizeArm(sessions, backend, disclosure) {
        const selected = sessions.filter(session => session.assignments.backend === backend && session.assignments.disclosure === disclosure);
        const events = selected.flatMap(session => session.events);
        const count = events.length;
        return {
            backend,
            disclosure,
            key: armKey(backend, disclosure),
            sessions: selected.length,
            rounds: count,
            cooperation_rate: count ? events.filter(event => event.participant_strategy === "C").length / count : null,
            q_strategy_rate: count ? events.filter(event => event.participant_strategy === "Q").length / count : null,
            mean_participant_payoff: count ? events.reduce((sum, event) => sum + event.participant_payoff, 0) / count : null,
            mean_joint_payoff: count ? events.reduce((sum, event) => sum + event.participant_payoff + event.opponent_payoff, 0) / count : null,
            median_response_time_ms: median(events.map(event => event.response_time_ms))
        };
    }

    function aggregateMetric(sessions, field, value) {
        const selected = sessions.filter(session => session.assignments[field] === value);
        const events = selected.flatMap(session => session.events);
        if (!events.length) return null;
        return {
            cooperation_rate: events.filter(event => event.participant_strategy === "C").length / events.length,
            q_strategy_rate: events.filter(event => event.participant_strategy === "Q").length / events.length,
            mean_participant_payoff: events.reduce((sum, event) => sum + event.participant_payoff, 0) / events.length,
            mean_joint_payoff: events.reduce((sum, event) => sum + event.participant_payoff + event.opponent_payoff, 0) / events.length,
            median_response_time_ms: median(events.map(event => event.response_time_ms))
        };
    }

    function difference(left, right) {
        if (!left || !right) return null;
        const result = {};
        for (const metric of ["cooperation_rate", "q_strategy_rate", "mean_participant_payoff", "mean_joint_payoff", "median_response_time_ms"]) {
            result[metric] = left[metric] - right[metric];
        }
        return result;
    }

    function summarize(sessions) {
        const arms = [];
        for (const backend of BACKENDS) {
            for (const disclosure of DISCLOSURES) arms.push(summarizeArm(sessions, backend, disclosure));
        }
        return {
            sessions: sessions.length,
            rounds: sessions.reduce((sum, session) => sum + session.events.length, 0),
            arms,
            effects: {
                backend_ewl_minus_classical: difference(
                    aggregateMetric(sessions, "backend", "ewl-simulator"),
                    aggregateMetric(sessions, "backend", "classical-correlated")
                ),
                disclosure_labeled_minus_neutral: difference(
                    aggregateMetric(sessions, "disclosure", "mechanism-labeled"),
                    aggregateMetric(sessions, "disclosure", "neutral")
                )
            },
            interpretation_boundary: "Descriptive differences are not causal estimates or significance tests. Use a preregistered analysis and adequate sample size."
        };
    }

    function flattenEvents(sessions) {
        return sessions.flatMap(session => session.events.map(event => ({
            protocol: session.protocol,
            session_id: session.session_id,
            created_at: session.created_at,
            completed_at: session.completed_at,
            backend: session.assignments.backend,
            disclosure: session.assignments.disclosure,
            ...event
        })));
    }

    return { PROTOCOL, BACKENDS, DISCLOSURES, canonicalString, validateRecord, summarize, flattenEvents, median };
}));
