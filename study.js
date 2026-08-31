document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const TOTAL_ROUNDS = 12;
    const PAYOFFS = {
        CC: [3, 3],
        CD: [0, 5],
        DC: [5, 0],
        DD: [1, 1]
    };
    const COUPLINGS = [
        { name: "low", gamma: 0 },
        { name: "medium", gamma: Math.PI / 4 },
        { name: "high", gamma: Math.PI / 2 }
    ];

    const screens = {
        consent: document.getElementById("consent-screen"),
        game: document.getElementById("game-screen"),
        debrief: document.getElementById("debrief-screen")
    };
    const consentAge = document.getElementById("consent-age");
    const consentLocal = document.getElementById("consent-local");
    const btnBegin = document.getElementById("btn-begin-study");
    const sessionLabel = document.getElementById("session-label");
    const roundLabel = document.getElementById("round-label");
    const mechanismLabel = document.getElementById("mechanism-label");
    const conditionDescription = document.getElementById("condition-description");
    const couplingDescription = document.getElementById("coupling-description");
    const strategyButtons = document.querySelectorAll(".strategy-button");
    const participantScore = document.getElementById("participant-score");
    const opponentScore = document.getElementById("opponent-score");
    const roundResult = document.getElementById("round-result");
    const outcomeHeading = document.getElementById("outcome-heading");
    const outcomeDetail = document.getElementById("outcome-detail");
    const btnNextRound = document.getElementById("btn-next-round");
    const debriefSummary = document.getElementById("debrief-summary");
    const assignmentReveal = document.getElementById("assignment-reveal");
    const integrityStatus = document.getElementById("integrity-status");
    const btnDownloadJson = document.getElementById("btn-download-json");
    const btnDownloadCsv = document.getElementById("btn-download-csv");
    const btnNewSession = document.getElementById("btn-new-session");

    let session = null;
    let outcomeRandom = null;
    let decisionStartedAt = 0;

    function secureUint32() {
        if (window.crypto && window.crypto.getRandomValues) {
            const values = new Uint32Array(1);
            window.crypto.getRandomValues(values);
            return values[0];
        }
        return Math.floor(Math.random() * 4294967296) >>> 0;
    }

    function makeSessionId() {
        if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
        return `local-${secureUint32().toString(16)}-${secureUint32().toString(16)}`;
    }

    function shuffle(items, random) {
        const copy = items.slice();
        for (let index = copy.length - 1; index > 0; index -= 1) {
            const swapIndex = Math.floor(random() * (index + 1));
            [copy[index], copy[swapIndex]] = [copy[swapIndex], copy[index]];
        }
        return copy;
    }

    function buildSchedule(seed) {
        const balanced = [];
        for (const coupling of COUPLINGS) {
            for (const opponent of ["C", "D", "Q"]) {
                balanced.push({ opponent, coupling: coupling.name, gamma: coupling.gamma });
            }
        }
        for (const opponent of ["C", "D", "Q"]) {
            balanced.push({ opponent, coupling: "medium", gamma: Math.PI / 4 });
        }
        return shuffle(balanced, window.EWLCore.mulberry32(seed));
    }

    function showScreen(name) {
        Object.entries(screens).forEach(([screenName, element]) => {
            const active = screenName === name;
            element.hidden = !active;
            element.classList.toggle("active-study-screen", active);
        });
    }

    function updateConsentButton() {
        btnBegin.disabled = !(consentAge.checked && consentLocal.checked);
    }

    function createSession() {
        const assignmentSeed = secureUint32();
        const scheduleSeed = secureUint32();
        const outcomeSeed = secureUint32();
        const assignmentRandom = window.EWLCore.mulberry32(assignmentSeed);
        const backend = assignmentRandom() < 0.5 ? "classical-correlated" : "ewl-simulator";
        const disclosure = assignmentRandom() < 0.5 ? "neutral" : "mechanism-labeled";
        return {
            protocol: "ewl-participant-pilot/v1",
            session_id: makeSessionId(),
            created_at: new Date().toISOString(),
            consent: { adult_confirmed: true, voluntary_local_pilot_confirmed: true },
            assignments: { backend, disclosure },
            seeds: { assignment: assignmentSeed, schedule: scheduleSeed, outcome: outcomeSeed },
            random_source: window.crypto && window.crypto.getRandomValues ? "Web Crypto seed + recorded PRNG" : "Math.random fallback seed + recorded PRNG",
            schedule: buildSchedule(scheduleSeed),
            current_round: 0,
            totals: { participant: 0, opponent: 0 },
            events: [],
            completed_at: null,
            integrity: null,
            interpretation_boundary: "This local pilot tests data collection and mechanism framing. It is not evidence of quantum advantage, consciousness, or Orch-OR."
        };
    }

    function mechanismCopy() {
        if (session.assignments.disclosure === "neutral") {
            return {
                label: "Mechanism: undisclosed",
                description: "You are playing a mediated strategic game. The mechanism assignment will be revealed after the final round."
            };
        }
        if (session.assignments.backend === "ewl-simulator") {
            return {
                label: "Mechanism: EWL simulator",
                description: "Outcomes are calculated with an exact Eisert–Wilkens–Lewenstein statevector simulation and sampled locally."
            };
        }
        return {
            label: "Mechanism: classical correlated",
            description: "Outcomes are sampled locally by a conventional correlated mediator matched to a declared target distribution."
        };
    }

    function renderRound() {
        const round = session.schedule[session.current_round];
        const mechanism = mechanismCopy();
        sessionLabel.textContent = `Session ${session.session_id.slice(0, 8)}`;
        roundLabel.textContent = `Round ${session.current_round + 1} of ${TOTAL_ROUNDS}`;
        mechanismLabel.textContent = mechanism.label;
        conditionDescription.textContent = mechanism.description;
        couplingDescription.textContent = session.assignments.disclosure === "mechanism-labeled"
            ? `Declared coupling: ${round.coupling} (γ = ${round.gamma.toFixed(3)}).`
            : `Interaction strength: ${round.coupling}.`;
        participantScore.textContent = String(session.totals.participant);
        opponentScore.textContent = String(session.totals.opponent);
        roundResult.hidden = true;
        strategyButtons.forEach(button => { button.disabled = false; });
        decisionStartedAt = performance.now();
    }

    function playRound(participantStrategy) {
        const round = session.schedule[session.current_round];
        strategyButtons.forEach(button => { button.disabled = true; });
        const responseTimeMs = Math.max(0, Math.round(performance.now() - decisionStartedAt));
        const probabilities = window.EWLCore.distribution(participantStrategy, round.opponent, round.gamma);
        const randomDraw = outcomeRandom();
        const outcome = window.EWLCore.sample(probabilities, randomDraw);
        const payoff = PAYOFFS[outcome];
        session.totals.participant += payoff[0];
        session.totals.opponent += payoff[1];
        session.events.push({
            round: session.current_round + 1,
            recorded_at: new Date().toISOString(),
            response_time_ms: responseTimeMs,
            participant_strategy: participantStrategy,
            opponent_strategy: round.opponent,
            coupling: round.coupling,
            gamma: round.gamma,
            backend: session.assignments.backend,
            disclosure: session.assignments.disclosure,
            probabilities,
            random_draw: randomDraw,
            measured_outcome: outcome,
            participant_payoff: payoff[0],
            opponent_payoff: payoff[1],
            cumulative_participant_payoff: session.totals.participant,
            cumulative_opponent_payoff: session.totals.opponent
        });

        participantScore.textContent = String(session.totals.participant);
        opponentScore.textContent = String(session.totals.opponent);
        outcomeHeading.textContent = `${outcome}: you +${payoff[0]}, opponent +${payoff[1]}`;
        outcomeDetail.textContent = `You chose ${participantStrategy}; the opponent chose ${round.opponent}. Response time: ${responseTimeMs} ms.`;
        btnNextRound.textContent = session.current_round + 1 === TOTAL_ROUNDS ? "Finish and debrief" : "Next round";
        roundResult.hidden = false;
    }

    function canonicalRecord() {
        const clone = JSON.parse(JSON.stringify(session));
        clone.integrity = null;
        return JSON.stringify(clone);
    }

    function enableDownloads() {
        btnDownloadJson.disabled = false;
        btnDownloadCsv.disabled = false;
    }

    function fallbackHash(text) {
        // window.crypto.subtle is unavailable in non-secure contexts, including
        // file:// in Chrome. Without a fallback, a participant who simply opens
        // this page from disk produces an unhashed record that the researcher
        // console rejects outright, silently losing real data.
        if (!(window.Sha256Fallback && typeof window.Sha256Fallback.hex === "function")) return null;
        return window.Sha256Fallback.hex(text);
    }

    async function addIntegrityHash() {
        const canonical = canonicalRecord();
        try {
            let hash = null;
            if (window.crypto && window.crypto.subtle) {
                const digest = await window.crypto.subtle.digest("SHA-256", new TextEncoder().encode(canonical));
                hash = Array.from(new Uint8Array(digest)).map(byte => byte.toString(16).padStart(2, "0")).join("");
            } else {
                hash = fallbackHash(canonical);
            }
            if (hash) {
                session.integrity = { algorithm: "SHA-256", sha256: hash };
                integrityStatus.textContent = `Record SHA-256: ${hash}`;
            } else {
                session.integrity = { algorithm: "unavailable", sha256: null };
                integrityStatus.textContent = "SHA-256 could not be computed; this record will not import into the researcher console.";
            }
        } catch (error) {
            const hash = fallbackHash(canonical);
            if (hash) {
                session.integrity = { algorithm: "SHA-256", sha256: hash };
                integrityStatus.textContent = `Record SHA-256: ${hash}`;
            } else {
                session.integrity = { algorithm: "error", sha256: null };
                integrityStatus.textContent = "The integrity hash could not be generated; this record will not import into the researcher console.";
            }
        } finally {
            enableDownloads();
        }
    }

    function finishSession() {
        session.completed_at = new Date().toISOString();
        const counts = { C: 0, D: 0, Q: 0 };
        session.events.forEach(event => { counts[event.participant_strategy] += 1; });
        debriefSummary.textContent = `Your total payoff was ${session.totals.participant}; the opponent's was ${session.totals.opponent}. Your choices: C ${counts.C}, D ${counts.D}, Q ${counts.Q}.`;
        assignmentReveal.textContent = `Assignment revealed: backend “${session.assignments.backend}”; disclosure arm “${session.assignments.disclosure}”.`;
        showScreen("debrief");
        addIntegrityHash();
    }

    function downloadBlob(filename, content, mimeType) {
        const url = URL.createObjectURL(new Blob([content], { type: mimeType }));
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    function csvCell(value) {
        const text = String(value ?? "");
        return `"${text.replace(/"/g, '""')}"`;
    }

    function downloadCsv() {
        const fields = [
            "session_id", "round", "response_time_ms", "participant_strategy", "opponent_strategy",
            "coupling", "gamma", "backend", "disclosure", "measured_outcome", "participant_payoff",
            "opponent_payoff", "cumulative_participant_payoff", "cumulative_opponent_payoff"
        ];
        const lines = [fields.map(csvCell).join(",")];
        session.events.forEach(event => {
            const row = { session_id: session.session_id, ...event };
            lines.push(fields.map(field => csvCell(row[field])).join(","));
        });
        downloadBlob(`ewl-study-${session.session_id}.csv`, lines.join("\n"), "text/csv;charset=utf-8");
    }

    consentAge.addEventListener("change", updateConsentButton);
    consentLocal.addEventListener("change", updateConsentButton);
    btnBegin.addEventListener("click", () => {
        if (!(consentAge.checked && consentLocal.checked)) return;
        session = createSession();
        outcomeRandom = window.EWLCore.mulberry32(session.seeds.outcome);
        showScreen("game");
        renderRound();
    });
    strategyButtons.forEach(button => {
        button.addEventListener("click", () => playRound(button.dataset.strategy));
    });
    btnNextRound.addEventListener("click", () => {
        session.current_round += 1;
        if (session.current_round >= TOTAL_ROUNDS) finishSession();
        else renderRound();
    });
    btnDownloadJson.addEventListener("click", () => {
        downloadBlob(`ewl-study-${session.session_id}.json`, JSON.stringify(session, null, 2), "application/json");
    });
    btnDownloadCsv.addEventListener("click", downloadCsv);
    btnNewSession.addEventListener("click", () => window.location.reload());
});
