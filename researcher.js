document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const recordFiles = document.getElementById("record-files");
    const btnProcessFiles = document.getElementById("btn-process-files");
    const btnClearRecords = document.getElementById("btn-clear-records");
    const importStatus = document.getElementById("import-status");
    const qualitySection = document.getElementById("quality-section");
    const analysisSection = document.getElementById("analysis-section");
    const validationRows = document.getElementById("validation-rows");
    const countFiles = document.getElementById("count-files");
    const countValid = document.getElementById("count-valid");
    const countInvalid = document.getElementById("count-invalid");
    const countDuplicates = document.getElementById("count-duplicates");
    const armRows = document.getElementById("arm-rows");
    const effectGrid = document.getElementById("effect-grid");
    const btnExportEvents = document.getElementById("btn-export-events");
    const btnExportSummary = document.getElementById("btn-export-summary");

    let acceptedRecords = [];
    let auditRows = [];

    function formatPercent(value) {
        return value === null ? "—" : `${(value * 100).toFixed(1)}%`;
    }

    function formatNumber(value, digits = 2) {
        return value === null ? "—" : value.toFixed(digits);
    }

    function formatMilliseconds(value) {
        return value === null ? "—" : `${Math.round(value)} ms`;
    }

    async function sha256(text) {
        if (!(window.crypto && window.crypto.subtle)) throw new Error("SHA-256 is unavailable in this browser context.");
        const digest = await window.crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
        return Array.from(new Uint8Array(digest)).map(byte => byte.toString(16).padStart(2, "0")).join("");
    }

    async function validateIntegrity(record) {
        if (!record.integrity || record.integrity.algorithm !== "SHA-256" || typeof record.integrity.sha256 !== "string") {
            return "A verified SHA-256 integrity record is required.";
        }
        const calculated = await sha256(window.ResearchCore.canonicalString(record));
        return calculated === record.integrity.sha256 ? null : "SHA-256 integrity mismatch.";
    }

    async function inspectFile(file, knownIds) {
        let record;
        try {
            record = JSON.parse(await file.text());
        } catch (error) {
            return { file: file.name, session: "—", status: "invalid", details: "File is not valid JSON." };
        }

        const sessionId = typeof record.session_id === "string" ? record.session_id : "—";
        if (sessionId !== "—" && knownIds.has(sessionId)) {
            return { file: file.name, session: sessionId, status: "duplicate", details: "Session ID was already accepted." };
        }

        const structure = window.ResearchCore.validateRecord(record);
        const errors = structure.errors.slice();
        if (structure.valid) {
            try {
                const integrityError = await validateIntegrity(record);
                if (integrityError) errors.push(integrityError);
            } catch (error) {
                errors.push(error.message || "Integrity validation failed.");
            }
        }
        if (errors.length) {
            return { file: file.name, session: sessionId, status: "invalid", details: errors.join(" ") };
        }

        knownIds.add(sessionId);
        acceptedRecords.push(record);
        return { file: file.name, session: sessionId, status: "valid", details: "Structure, replay fields, payoffs, and SHA-256 verified." };
    }

    function renderAuditTable() {
        validationRows.textContent = "";
        auditRows.forEach(row => {
            const tr = document.createElement("tr");
            for (const value of [row.file, row.session]) {
                const td = document.createElement("td");
                td.textContent = value;
                tr.appendChild(td);
            }
            const status = document.createElement("td");
            status.textContent = row.status.toUpperCase();
            status.className = `status-${row.status}`;
            tr.appendChild(status);
            const details = document.createElement("td");
            details.textContent = row.details;
            tr.appendChild(details);
            validationRows.appendChild(tr);
        });
        countFiles.textContent = String(auditRows.length);
        countValid.textContent = String(acceptedRecords.length);
        countInvalid.textContent = String(auditRows.filter(row => row.status === "invalid").length);
        countDuplicates.textContent = String(auditRows.filter(row => row.status === "duplicate").length);
    }

    function armLabel(arm) {
        const backend = arm.backend === "ewl-simulator" ? "EWL" : "Classical";
        const disclosure = arm.disclosure === "mechanism-labeled" ? "labeled" : "neutral";
        return `${backend} · ${disclosure}`;
    }

    function renderArmTable(summary) {
        armRows.textContent = "";
        summary.arms.forEach(arm => {
            const tr = document.createElement("tr");
            const values = [
                arm.backend,
                arm.disclosure,
                String(arm.sessions),
                formatPercent(arm.cooperation_rate),
                formatPercent(arm.q_strategy_rate),
                formatNumber(arm.mean_participant_payoff),
                formatNumber(arm.mean_joint_payoff),
                formatMilliseconds(arm.median_response_time_ms)
            ];
            values.forEach(value => {
                const td = document.createElement("td");
                td.textContent = value;
                tr.appendChild(td);
            });
            armRows.appendChild(tr);
        });
    }

    function renderBarChart(elementId, arms, metric, maximum, formatter) {
        const container = document.getElementById(elementId);
        container.textContent = "";
        const observed = arms.map(arm => arm[metric]).filter(value => value !== null);
        const scale = maximum || Math.max(...observed, 1);
        arms.forEach(arm => {
            const row = document.createElement("div");
            row.className = "bar-row";
            const label = document.createElement("span");
            label.className = "bar-label";
            label.textContent = armLabel(arm);
            const track = document.createElement("div");
            track.className = "bar-track";
            const fill = document.createElement("div");
            fill.className = "bar-fill";
            fill.style.width = arm[metric] === null ? "0" : `${Math.max(0, Math.min(100, (arm[metric] / scale) * 100))}%`;
            track.appendChild(fill);
            const value = document.createElement("span");
            value.className = `bar-value${arm[metric] === null ? " bar-empty" : ""}`;
            value.textContent = arm[metric] === null ? "no data" : formatter(arm[metric]);
            row.append(label, track, value);
            container.appendChild(row);
        });
    }

    function signed(value, formatter) {
        if (value === null) return "need both arms";
        const prefix = value > 0 ? "+" : "";
        return `${prefix}${formatter(value)}`;
    }

    function effectPanel(title, effect) {
        const panel = document.createElement("div");
        panel.className = "effect-panel";
        const heading = document.createElement("h3");
        heading.textContent = title;
        panel.appendChild(heading);
        if (!effect) {
            const empty = document.createElement("p");
            empty.className = "analysis-boundary";
            empty.textContent = "Both comparison arms need accepted sessions.";
            panel.appendChild(empty);
            return panel;
        }
        const list = document.createElement("div");
        list.className = "effect-list";
        const rows = [
            ["Cooperation", signed(effect.cooperation_rate, value => `${(value * 100).toFixed(1)} pp`)],
            ["Q strategy", signed(effect.q_strategy_rate, value => `${(value * 100).toFixed(1)} pp`)],
            ["Participant payoff", signed(effect.mean_participant_payoff, value => value.toFixed(2))],
            ["Joint payoff", signed(effect.mean_joint_payoff, value => value.toFixed(2))],
            ["Median response", signed(effect.median_response_time_ms, value => `${Math.round(value)} ms`)]
        ];
        rows.forEach(([label, value]) => {
            const labelNode = document.createElement("span");
            labelNode.textContent = label;
            const valueNode = document.createElement("strong");
            valueNode.textContent = value;
            list.append(labelNode, valueNode);
        });
        panel.appendChild(list);
        return panel;
    }

    function renderAnalysis() {
        if (!acceptedRecords.length) {
            analysisSection.hidden = true;
            return;
        }
        const summary = window.ResearchCore.summarize(acceptedRecords);
        renderArmTable(summary);
        renderBarChart("chart-cooperation", summary.arms, "cooperation_rate", 1, formatPercent);
        renderBarChart("chart-q-rate", summary.arms, "q_strategy_rate", 1, formatPercent);
        renderBarChart("chart-payoff", summary.arms, "mean_participant_payoff", 5, value => value.toFixed(2));
        renderBarChart("chart-response", summary.arms, "median_response_time_ms", null, value => `${Math.round(value)} ms`);
        effectGrid.textContent = "";
        effectGrid.append(
            effectPanel("Backend: EWL − classical", summary.effects.backend_ewl_minus_classical),
            effectPanel("Disclosure: labeled − neutral", summary.effects.disclosure_labeled_minus_neutral)
        );
        analysisSection.hidden = false;
    }

    async function processFiles() {
        const files = Array.from(recordFiles.files || []);
        if (!files.length) return;
        btnProcessFiles.disabled = true;
        importStatus.textContent = `Validating ${files.length} file${files.length === 1 ? "" : "s"}…`;
        const knownIds = new Set(acceptedRecords.map(record => record.session_id));
        for (const file of files) auditRows.push(await inspectFile(file, knownIds));
        renderAuditTable();
        renderAnalysis();
        qualitySection.hidden = false;
        btnClearRecords.disabled = false;
        recordFiles.value = "";
        importStatus.textContent = `${acceptedRecords.length} accepted session${acceptedRecords.length === 1 ? "" : "s"} in memory; ${auditRows.length} files inspected.`;
    }

    function clearRecords() {
        acceptedRecords = [];
        auditRows = [];
        validationRows.textContent = "";
        recordFiles.value = "";
        qualitySection.hidden = true;
        analysisSection.hidden = true;
        btnClearRecords.disabled = true;
        btnProcessFiles.disabled = true;
        importStatus.textContent = "No files selected.";
    }

    function csvCell(value) {
        const text = String(value ?? "");
        return `"${text.replace(/"/g, '""')}"`;
    }

    function downloadBlob(filename, content, type) {
        const url = URL.createObjectURL(new Blob([content], { type }));
        const link = document.createElement("a");
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        // Revoking synchronously can cancel a download that has not started yet in
        // some browsers; defer it to the next task instead.
        setTimeout(() => URL.revokeObjectURL(url), 0);
    }

    function exportEvents() {
        const rows = window.ResearchCore.flattenEvents(acceptedRecords).map(row => ({
            ...row,
            probability_CC: row.probabilities.CC,
            probability_CD: row.probabilities.CD,
            probability_DC: row.probabilities.DC,
            probability_DD: row.probabilities.DD
        }));
        const fields = [
            "protocol", "session_id", "created_at", "completed_at", "backend", "disclosure", "round",
            "response_time_ms", "participant_strategy", "opponent_strategy", "coupling", "gamma", "random_draw",
            "measured_outcome", "participant_payoff", "opponent_payoff", "cumulative_participant_payoff",
            "cumulative_opponent_payoff", "probability_CC", "probability_CD", "probability_DC", "probability_DD"
        ];
        const lines = [fields.map(csvCell).join(",")];
        rows.forEach(row => lines.push(fields.map(field => csvCell(row[field])).join(",")));
        downloadBlob("ewl-pilot-combined-events.csv", lines.join("\n"), "text/csv;charset=utf-8");
    }

    function exportSummary() {
        const output = {
            generated_at: new Date().toISOString(),
            accepted_session_ids: acceptedRecords.map(record => record.session_id),
            validation_counts: {
                files_inspected: auditRows.length,
                accepted: acceptedRecords.length,
                invalid: auditRows.filter(row => row.status === "invalid").length,
                duplicates: auditRows.filter(row => row.status === "duplicate").length
            },
            analysis: window.ResearchCore.summarize(acceptedRecords)
        };
        downloadBlob("ewl-pilot-summary.json", JSON.stringify(output, null, 2), "application/json");
    }

    recordFiles.addEventListener("change", () => {
        const count = recordFiles.files ? recordFiles.files.length : 0;
        btnProcessFiles.disabled = count === 0;
        importStatus.textContent = count ? `${count} file${count === 1 ? "" : "s"} selected; validation has not run.` : "No files selected.";
    });
    btnProcessFiles.addEventListener("click", processFiles);
    btnClearRecords.addEventListener("click", clearRecords);
    btnExportEvents.addEventListener("click", exportEvents);
    btnExportSummary.addEventListener("click", exportSummary);
});
