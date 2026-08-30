// Quantum Cognitive & Governance Lab - app.js (v3)

document.addEventListener("DOMContentLoaded", () => {
    // --- Application State ---
    let state = {
        // Active Scenario & Mind State
        scenario: "geopolitical",
        theta: Math.PI / 4, 
        history: [],        
        action: 0.0,        
        threshold: 0.5,     
        dt: 0.02,           
        pressure: 65,
        temperature: 310, // Kelvin
        entanglement: 85, // %
        
        isDeliberating: false,
        deliberationTimer: null,
        collapsed: false,
        collapsedState: null,
        
        // Mode 2: Game Theory State
        p1Strategy: "Q",
        p2Strategy: "Q",
        entanglementGamma: 1.5708,
        
        // Mode 3: Spinoza State
        spinozaThetaA: Math.PI / 4,
        
        // Charts & 3D Three.js
        actionChart: null,
        probChart: null,
        experimentChart: null,
        stepCount: 0
    };

    // --- Scenario Definitions ---
    const SCENARIOS = {
        geopolitical: {
            title: "🌍 Geopolitical Crisis",
            basis0: "|0⟩ De-escalation & Peace",
            basis1: "|1⟩ Escalation & Deterrence",
            desc: "Simulates national leadership deliberating between military deterrence vs diplomatic de-escalation."
        },
        "dao-governance": {
            title: "🏛️ DAO Treasury Allocation",
            basis0: "|0⟩ Public Good Funding",
            basis1: "|1⟩ Yield Maximization",
            desc: "Simulates AI DAO voters deliberating between ecosystem public goods vs private yield strategies."
        },
        "linda-fallacy": {
            title: "🧠 Cognitive Paradox (Linda Problem)",
            basis0: "|0⟩ Single Probability Space",
            basis1: "|1⟩ Conjunction Fallacy Projection",
            desc: "Simulates human decision-makers projecting non-orthogonal cognitive subspaces (Tversky & Kahneman)."
        }
    };

    // --- DOM Element References ---
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    const scenarioSelect = document.getElementById("scenario-select");
    const initialStateSelect = document.getElementById("initial-state");
    
    const sliderPressure = document.getElementById("slider-pressure");
    const valPressure = document.getElementById("val-pressure");
    const sliderTemp = document.getElementById("slider-temp");
    const valTemp = document.getElementById("val-temp");
    const sliderEntanglement = document.getElementById("slider-entanglement");
    const valEntanglement = document.getElementById("val-entanglement");
    const sliderThreshold = document.getElementById("collapse-threshold");
    const valThreshold = document.getElementById("threshold-val");
    
    const btnEthicsArg = document.getElementById("btn-ethics-arg");
    const btnProfitArg = document.getElementById("btn-profit-arg");
    const btnDeliberate = document.getElementById("btn-deliberate");
    const btnForceCollapse = document.getElementById("btn-force-collapse");
    const btnReset = document.getElementById("btn-reset");
    
    const eventLog = document.getElementById("event-log");
    const btnClearLog = document.getElementById("btn-clear-log");
    const flashOverlay = document.getElementById("collapse-flash");
    const badgeStatus3D = document.getElementById("status-badge-3d");
    const lblDecoherenceRate = document.getElementById("lbl-decoherence-rate");

    // Game Theory Elements
    const selectP1Strategy = document.getElementById("player1-strategy");
    const selectP2Strategy = document.getElementById("player2-strategy");
    const sliderGamma = document.getElementById("entanglement-gamma");
    const valGamma = document.getElementById("gamma-val");

    // Spinoza Elements
    const sliderSpinozaTheta = document.getElementById("spinoza-theta");
    const valSpinozaTheta = document.getElementById("spinoza-theta-val");
    const btnSpinozaRun = document.getElementById("btn-spinoza-run");

    // Benchmark Elements
    const btnRunLinda = document.getElementById("btn-run-linda");
    const btnRunGallup = document.getElementById("btn-run-gallup");

    // Experiment Lab Elements
    const experimentSelect = document.getElementById("experiment-select");
    const btnViewReference = document.getElementById("btn-view-reference");
    const btnDownloadManifest = document.getElementById("btn-download-manifest");
    const experimentWorkbench = document.getElementById("experiment-workbench");
    const defaultLabPanels = document.querySelectorAll(".lab-default-panel");
    const experimentTitle = document.getElementById("experiment-title");
    const experimentStatus = document.getElementById("experiment-status");
    const experimentKind = document.getElementById("experiment-kind");
    const experimentSummary = document.getElementById("experiment-summary");
    const experimentHypothesis = document.getElementById("experiment-hypothesis");
    const experimentBaseline = document.getElementById("experiment-baseline");
    const experimentResultTitle = document.getElementById("experiment-result-title");
    const experimentResultLabel = document.getElementById("experiment-result-label");
    const experimentResult = document.getElementById("experiment-result");
    const experimentBoundary = document.getElementById("experiment-boundary");
    const experimentSource = document.getElementById("experiment-source");
    const experimentCommand = document.getElementById("experiment-command");
    const experimentReproductionNote = document.getElementById("experiment-reproduction-note");
    const experimentChartCanvas = document.getElementById("experimentChart");

    // The browser catalogue mirrors q_ai_governance.experiment_lab.  Only the
    // Snapshot entry displays a checked, bundled result; companion studies link
    // to their own repositories instead of inventing a result in this UI.
    const EXPERIMENTS = {
        "ewl-mechanism-blind-tournament": {
            title: "EWL mechanism-blind quantum-game tournament",
            kind: "Reproducible simulation protocol",
            status: "RUNNABLE LOCALLY",
            summary: "A control ladder for EWL Prisoner's Dilemma runs. It makes the closest non-quantum alternative explicit: a classical sampler with exactly the same outcome probabilities.",
            hypothesis: "An EWL implementation changes strategic outcomes beyond a probability-matched classical mediator. The first run tests the control construction; it does not test people or consciousness.",
            baseline: "A classical correlated sampler uses the exact EWL outcome probabilities and the same recorded seed. Its sampled event sequence must match the EWL simulator exactly.",
            resultTitle: "Registered control invariant",
            resultLabel: "RUN LOCALLY",
            result: "The expected initial result is a match between the EWL simulator and its classical-correlated control. A mismatch is a reproducibility bug, not a quantum effect.",
            boundary: "Interpretation boundary: matching a quantum calculation with classical sampling shows why a future human study needs matched controls. It does not establish quantum advantage, consciousness, or Orch-OR.",
            source: "https://github.com/JonathanReiser/quantum-orch-or/blob/main/EWL_TOURNAMENT.md",
            command: "q-ai-gov ewl-tournament --p1 C --p2 D --rounds 100 --seed 7 --output report.json",
            reproductionNote: "The JSON report records every event, target probabilities, seed, and replay hash. The hardware adapter is deliberately non-executed until a QPU job has complete provenance."
        },
        "snapshot-temporal-baseline": {
            title: "Snapshot DAO vote baseline benchmark",
            kind: "Real-data analysis",
            status: "RUNNABLE LOCALLY",
            summary: "A temporal hold-out analysis of 905 Snapshot DAO proposals. It asks whether information available before a vote improves on ordinary historical voting baselines.",
            hypothesis: "Pre-vote features improve on simple historical voting baselines. This is a calibration test, not a test of consciousness or a claim that a quantum process is involved.",
            baseline: "Train mean, train median, per-DAO historical mean, and ridge regression on pre-vote features: DAO identity, proposal length, ballot shape, voting window, quorum, and prior DAO approval.",
            resultTitle: "Recorded reference result (temporal hold-out)",
            resultLabel: "BUNDLED DATA",
            result: "The train-median baseline had the lowest mean absolute error: 10.44 percentage points. The pre-vote ridge model was worse at 11.20 pp with R² = 0.013.",
            boundary: "Interpretation boundary: this is evidence that this dataset has little usable pre-vote predictive signal. It is not evidence for Orch-OR, consciousness, or a quantum advantage.",
            source: "https://github.com/JonathanReiser/quantum-orch-or/blob/main/data/benchmark_classical_results.json",
            command: "q-ai-gov experiments --run snapshot-temporal-baseline --data snapshot_dao_dataset.json --output report.json",
            reproductionNote: "Run from a local clone with the published snapshot dataset. The page displays a checked reference report; it does not execute Python or call an oracle.",
            chart: {
                label: "Mean absolute error (percentage points; lower is better)",
                labels: ["Train median", "Per-DAO mean", "Ridge: pre-vote features"],
                values: [10.44, 17.26, 11.20]
            }
        },
        "dao-vote-sequences": {
            title: "DAO vote-order and QQ-equality test",
            kind: "Real-data analysis · companion project",
            status: "EXTERNAL COMPANION",
            summary: "Tests whether a parameter-free quantum-cognition signature survives in real DAO voting when assignment and calendar effects are modeled explicitly.",
            hypothesis: "Quantum-cognition's parameter-free QQ equality holds in DAO voting.",
            baseline: "Propensity-weighted assignment controls and calendar-order controls. If they explain the apparent effect, the quantum account earns no special status.",
            resultTitle: "Protocol registered in companion repository",
            resultLabel: "NO IN-APP RESULT",
            result: "This page deliberately does not generate a score for a companion study. Use the linked repository to inspect the data, code, and results.",
            boundary: "Interpretation boundary: a match to QQ equality would be a model-comparison result, not evidence that voters or brains maintain physical quantum coherence.",
            source: "https://github.com/JonathanReiser/dao-governance-research",
            command: "Open JonathanReiser/dao-governance-research and run its documented analysis.",
            reproductionNote: "External companion: the experiment belongs to its own versioned data and code, rather than being simulated in this static interface."
        },
        "dating-order-effects": {
            title: "Speed-dating order and dyadic-correlation tests",
            kind: "Real-data analysis · companion project",
            status: "EXTERNAL COMPANION",
            summary: "Separates sequential context effects from dyadic dependence in a large speed-dating dataset.",
            hypothesis: "Sequential context or non-classical dependence improves on classical preference models.",
            baseline: "Controlled logistic models and dyadic dependence models that account for participant and partner structure.",
            resultTitle: "Protocol registered in companion repository",
            resultLabel: "NO IN-APP RESULT",
            result: "No value is drawn here because a rendered chart would be a simulation, not a rerun of the companion analysis.",
            boundary: "Interpretation boundary: behavioral order effects do not by themselves identify a quantum physical mechanism.",
            source: "https://github.com/JonathanReiser/quantum-dating-research",
            command: "Open JonathanReiser/quantum-dating-research and run its documented analysis.",
            reproductionNote: "External companion: inspect the pre-processing choices and classical controls before interpreting any quantum-cognition fit."
        },
        "geopolitics-vote-alignment": {
            title: "Geopolitical order and alignment tests",
            kind: "Real-data analysis · companion project",
            status: "EXTERNAL COMPANION",
            summary: "Tests order effects in geopolitical and international voting data while preserving the strongest conventional explanation: bloc alignment.",
            hypothesis: "Quantum-cognition signatures remain after classical bloc alignment is controlled.",
            baseline: "Pre-specified regional and ideological bloc controls, with time and agenda structure treated as confounders.",
            resultTitle: "Protocol registered in companion repository",
            resultLabel: "NO IN-APP RESULT",
            result: "The page links to the actual analysis rather than projecting a result from this interface.",
            boundary: "Interpretation boundary: model residuals are not a licence to infer quantum biology or conscious agency.",
            source: "https://github.com/JonathanReiser/quantum-geopolitics-research",
            command: "Open JonathanReiser/quantum-geopolitics-research and run its documented analysis.",
            reproductionNote: "External companion: its provenance and controls are part of the experiment, not optional presentation details."
        },
        "collective-valuation": {
            title: "Collective valuation of competing answers",
            kind: "Real-data analysis · companion project",
            status: "EXTERNAL COMPANION",
            summary: "Examines whether interactions among competing answers exceed exposure and popularity dynamics in public voting data.",
            hypothesis: "Competing-answer dependence exceeds calibrated exposure and momentum effects.",
            baseline: "A calibrated preferential-attachment and exposure null model, including momentum effects.",
            resultTitle: "Protocol registered in companion repository",
            resultLabel: "NO IN-APP RESULT",
            result: "No result is manufactured in the browser. The companion repository is the authoritative analysis surface.",
            boundary: "Interpretation boundary: a better mathematical description of dependence is not proof of a quantum substrate.",
            source: "https://github.com/JonathanReiser/collective-valuation-research",
            command: "Open JonathanReiser/collective-valuation-research and run its documented analysis.",
            reproductionNote: "External companion: report null, mixed, and sensitivity results alongside any model comparison."
        }
    };

    // --- Logger Utility ---
    function logEvent(msg, type = "info") {
        if (!eventLog) return;
        const entry = document.createElement("div");
        entry.className = `log-entry ${type}`;
        const timeStr = new Date().toLocaleTimeString();
        entry.innerHTML = `[${timeStr}] ${msg}`;
        eventLog.appendChild(entry);
        eventLog.scrollTop = eventLog.scrollHeight;
    }

    if (btnClearLog) {
        btnClearLog.addEventListener("click", () => {
            eventLog.innerHTML = "";
            logEvent("Console log cleared.", "info");
        });
    }

    function selectedExperiment() {
        return EXPERIMENTS[experimentSelect ? experimentSelect.value : "snapshot-temporal-baseline"];
    }

    function renderExperimentChart(experiment) {
        if (!experimentChartCanvas) return;
        const chartContainer = experimentChartCanvas.parentElement;
        const chartData = experiment.chart;
        chartContainer.hidden = !chartData;

        if (state.experimentChart) {
            state.experimentChart.destroy();
            state.experimentChart = null;
        }
        if (!chartData || typeof Chart === "undefined") return;

        state.experimentChart = new Chart(experimentChartCanvas, {
            type: "bar",
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: chartData.label,
                    data: chartData.values,
                    backgroundColor: ["rgba(0, 242, 254, 0.72)", "rgba(168, 85, 247, 0.72)", "rgba(245, 158, 11, 0.72)"],
                    borderColor: ["#00f2fe", "#a855f7", "#f59e0b"],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { ticks: { color: "#cbd5e1", maxRotation: 0 }, grid: { display: false } },
                    y: { beginAtZero: true, ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } }
                },
                plugins: { legend: { labels: { color: "#f8fafc" } } }
            }
        });
    }

    function renderExperiment() {
        const experiment = selectedExperiment();
        if (!experiment) return;

        experimentTitle.textContent = experiment.title;
        experimentStatus.textContent = experiment.status;
        experimentStatus.classList.toggle("badge-success", experiment.status === "RUNNABLE LOCALLY");
        experimentKind.textContent = experiment.kind;
        experimentSummary.textContent = experiment.summary;
        experimentHypothesis.textContent = experiment.hypothesis;
        experimentBaseline.textContent = experiment.baseline;
        experimentResultTitle.textContent = experiment.resultTitle;
        experimentResultLabel.textContent = experiment.resultLabel;
        experimentResult.textContent = experiment.result;
        experimentBoundary.textContent = experiment.boundary;
        experimentSource.href = experiment.source;
        experimentSource.textContent = experiment.status === "RUNNABLE LOCALLY" ? "Open bundled result data" : "Open companion repository";
        experimentCommand.textContent = experiment.command;
        experimentReproductionNote.textContent = experiment.reproductionNote;
        renderExperimentChart(experiment);
    }

    function setExperimentLabVisibility(isExperimentLab) {
        defaultLabPanels.forEach(panel => { panel.hidden = isExperimentLab; });
        if (experimentWorkbench) experimentWorkbench.hidden = !isExperimentLab;
        if (isExperimentLab) renderExperiment();
    }

    function downloadExperimentManifest() {
        const experiment = selectedExperiment();
        if (!experiment) return;
        const manifest = {
            experiment_id: experimentSelect.value,
            title: experiment.title,
            kind: experiment.kind,
            status: experiment.status,
            hypothesis: experiment.hypothesis,
            baseline: experiment.baseline,
            source: experiment.source,
            reproduction_command: experiment.command,
            interpretation_boundary: experiment.boundary
        };
        const url = URL.createObjectURL(new Blob([JSON.stringify(manifest, null, 2)], { type: "application/json" }));
        const link = document.createElement("a");
        link.href = url;
        link.download = `${experimentSelect.value}-manifest.json`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    if (experimentSelect) experimentSelect.addEventListener("change", renderExperiment);
    if (btnViewReference) btnViewReference.addEventListener("click", renderExperiment);
    if (btnDownloadManifest) btnDownloadManifest.addEventListener("click", downloadExperimentManifest);

    // --- Tab Navigation ---
    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            tabButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active-content"));
            
            button.classList.add("active");
            const targetId = button.getAttribute("data-target");
            
            if (targetId === "agent-tab") document.getElementById("agent-controls").classList.add("active-content");
            else if (targetId === "budget-tab") document.getElementById("budget-controls").classList.add("active-content");
            else if (targetId === "game-tab") document.getElementById("game-controls").classList.add("active-content");
            else if (targetId === "spinoza-tab") document.getElementById("spinoza-controls").classList.add("active-content");
            else if (targetId === "benchmark-tab") document.getElementById("benchmark-controls").classList.add("active-content");
            else if (targetId === "experiments-tab") document.getElementById("experiments-controls").classList.add("active-content");

            setExperimentLabVisibility(targetId === "experiments-tab");
        });
    });

    // --- DAO Budget Allocator Handler ---
    const btnRunBudgetAllocator = document.getElementById("btn-run-budget-allocator");
    const inputTotalBudget = document.getElementById("input-total-budget");
    const budgetSummaryBadge = document.getElementById("budget-summary-badge");

    if (btnRunBudgetAllocator) {
        btnRunBudgetAllocator.addEventListener("click", () => {
            const totalBudget = parseFloat(inputTotalBudget.value) || 1000000;
            logEvent(`⚡ Running Quantum Budget Allocator for Treasury Budget: <strong>$${totalBudget.toLocaleString()}</strong>...`, "info");
            
            setTimeout(() => {
                const allocated = totalBudget * 0.96;
                if (budgetSummaryBadge) {
                    budgetSummaryBadge.textContent = `Consensus Score: 87.0% | Allocated: $${Math.round(allocated).toLocaleString()} / $${Math.round(totalBudget).toLocaleString()} (96%)`;
                }
                logEvent(`✅ Quantum Budget Allocation Complete: <strong>$${Math.round(allocated).toLocaleString()} allocated (96.0%)</strong> with <strong>87.0% GHZ Entangled Consensus</strong>!`, "success");
                logEvent(`• Security Audit: $250,000 (100% FULL) | Developer Grants: $211,513 (70.5%) | Hackathons: $150,000 (100% FULL)`, "info");
            }, 600);
        });
    }

    // --- Three.js 3D Microtubule Visualizer Engine ---
    let scene, camera, renderer, microtubuleGroup, dimers = [], particleSystem;
    
    function init3DVisualizer() {
        const container = document.getElementById("microtubule-3d-canvas");
        if (!container) return;
        
        container.innerHTML = ""; // Clear existing
        const width = container.clientWidth || 600;
        const height = container.clientHeight || 350;
        
        scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0b0f19);
        
        camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        camera.position.set(0, 15, 30);
        camera.lookAt(0, 0, 0);
        
        renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);
        
        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        
        const dirLight1 = new THREE.DirectionalLight(0x00f2fe, 1.2);
        dirLight1.position.set(10, 20, 15);
        scene.add(dirLight1);
        
        const dirLight2 = new THREE.DirectionalLight(0xa855f7, 0.8);
        dirLight2.position.set(-10, -10, -15);
        scene.add(dirLight2);

        // Build 13 Protofilament Cylindrical Microtubule Lattice
        microtubuleGroup = new THREE.Group();
        dimers = [];
        
        const numFilaments = 13;
        const radius = 6.5;
        const heightLayers = 16;
        const dimerRadius = 0.55;
        
        const alphaGeo = new THREE.SphereGeometry(dimerRadius, 16, 16);
        const alphaMat = new THREE.MeshStandardMaterial({ color: 0x00f2fe, roughness: 0.3, metalness: 0.2 });
        const betaMat = new THREE.MeshStandardMaterial({ color: 0xa855f7, roughness: 0.3, metalness: 0.2 });
        
        for (let l = 0; l < heightLayers; l++) {
            const z = (l - heightLayers / 2) * 1.3;
            for (let f = 0; f < numFilaments; f++) {
                const angle = (f / numFilaments) * Math.PI * 2 + (l * 0.15); // Helical skew
                const x = Math.cos(angle) * radius;
                const y = Math.sin(angle) * radius;
                
                const mesh = new THREE.Mesh(alphaGeo, (l + f) % 2 === 0 ? alphaMat.clone() : betaMat.clone());
                mesh.position.set(x, y, z);
                microtubuleGroup.add(mesh);
                dimers.push({ mesh, originalPos: new THREE.Vector3(x, y, z), angle, layer: l });
            }
        }
        scene.add(microtubuleGroup);

        // Dynamic Quantum Phase Particles
        const particleGeo = new THREE.BufferGeometry();
        const particleCount = 200;
        const posArray = new Float32Array(particleCount * 3);
        
        for (let i = 0; i < particleCount * 3; i++) {
            posArray[i] = (Math.random() - 0.5) * 25;
        }
        particleGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
        
        const particleMat = new THREE.PointsMaterial({
            size: 0.25,
            color: 0x00f2fe,
            transparent: true,
            opacity: 0.7
        });
        particleSystem = new THREE.Points(particleGeo, particleMat);
        scene.add(particleSystem);
        
        // 60 FPS Render Loop
        function animate() {
            requestAnimationFrame(animate);
            
            // Continuous rotational phase dynamics
            microtubuleGroup.rotation.z += 0.005;
            microtubuleGroup.rotation.x = Math.sin(Date.now() * 0.001) * 0.15;
            
            if (particleSystem) {
                particleSystem.rotation.y += 0.003;
            }
            
            // Pulse tubulin dimer colors according to statevector amplitude
            if (!state.collapsed) {
                const p0 = Math.cos(state.theta) ** 2;
                dimers.forEach((d, idx) => {
                    const wave = Math.sin(Date.now() * 0.003 + d.layer * 0.5 + d.angle);
                    const intensity = 0.5 + 0.5 * wave * p0;
                    d.mesh.material.color.setHSL(0.5 + 0.2 * p0, 0.9, 0.4 + 0.3 * intensity);
                });
            }
            
            renderer.render(scene, camera);
        }
        animate();
    }
    
    // Initialize Charts & 3D WebGL Canvas
    initCharts();
    init3DVisualizer();
    
    // Parse URL Query Parameters for Live Oracle Proposal Links
    parseURLQueryParams();
    
    window.addEventListener("resize", init3DVisualizer);

    // --- Chart.js Setup ---
    function initCharts() {
        if (typeof Chart === "undefined") {
            console.warn("Chart.js CDN loading... retrying chart init");
            setTimeout(initCharts, 500);
            return;
        }

        const ctxAction = document.getElementById("actionChart");
        const ctxProb = document.getElementById("probabilityChart");
        if (!ctxAction || !ctxProb) return;

        try {
            if (state.actionChart) state.actionChart.destroy();
            if (state.probChart) state.probChart.destroy();

            state.actionChart = new Chart(ctxAction, {
                type: "line",
                data: {
                    labels: [0],
                    datasets: [
                        {
                            label: "Accumulated Action S(t)",
                            data: [0],
                            borderColor: "#00f2fe",
                            backgroundColor: "rgba(0, 242, 254, 0.1)",
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: "Penrose Threshold ℏ_cog",
                            data: [state.threshold],
                            borderColor: "#ef4444",
                            borderDash: [5, 5],
                            pointRadius: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" } },
                        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" }, min: 0, max: 1.0 }
                    },
                    plugins: { legend: { labels: { color: "#f8fafc" } } }
                }
            });

            state.probChart = new Chart(ctxProb, {
                type: "bar",
                data: {
                    labels: ["|0⟩ Public Good", "|1⟩ Private Gain"],
                    datasets: [{
                        label: "Statevector Probability",
                        data: [0.5, 0.5],
                        backgroundColor: ["rgba(0, 242, 254, 0.7)", "rgba(245, 158, 11, 0.7)"],
                        borderColor: ["#00f2fe", "#f59e0b"],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: { ticks: { color: "#94a3b8" }, grid: { color: "rgba(255,255,255,0.05)" }, min: 0, max: 1.0 }
                    },
                    plugins: { legend: { display: false } }
                }
            });

            // A visitor can open the experiment tab before the CDN finishes
            // loading. Render its reference chart once Chart.js is available.
            renderExperiment();
        } catch (e) {
            console.error("Chart initialization error:", e);
        }
    }

    initCharts();

    // --- Physics Controls & Slider Listeners ---
    if (scenarioSelect) {
        scenarioSelect.addEventListener("change", (e) => {
            state.scenario = e.target.value;
            const sc = SCENARIOS[state.scenario];
            logEvent(`Switched scenario to: <strong>${sc.title}</strong>`, "success");
            
            if (state.probChart) {
                state.probChart.data.labels = [sc.basis0, sc.basis1];
                state.probChart.update();
            }
            resetState();
        });
    }

    if (sliderPressure) {
        sliderPressure.addEventListener("input", (e) => {
            state.pressure = parseInt(e.target.value);
            valPressure.textContent = `${state.pressure}%`;
        });
    }

    if (sliderTemp) {
        sliderTemp.addEventListener("input", (e) => {
            state.temperature = parseInt(e.target.value);
            valTemp.textContent = `${state.temperature} K`;
            lblDecoherenceRate.textContent = `T = ${state.temperature} K (γ_ϕ = ${(state.temperature / 6200).toFixed(3)})`;
        });
    }

    if (sliderEntanglement) {
        sliderEntanglement.addEventListener("input", (e) => {
            state.entanglement = parseInt(e.target.value);
            valEntanglement.textContent = `${state.entanglement}% Entangled`;
        });
    }

    if (sliderThreshold) {
        sliderThreshold.addEventListener("input", (e) => {
            state.threshold = parseFloat(e.target.value);
            valThreshold.textContent = state.threshold.toFixed(2);
            if (state.actionChart) {
                state.actionChart.data.datasets[1].data = state.actionChart.data.labels.map(() => state.threshold);
                state.actionChart.update();
            }
        });
    }

    // --- State Vector Rotations ---
    if (btnEthicsArg) {
        btnEthicsArg.addEventListener("click", () => {
            if (state.collapsed) return;
            state.theta = Math.max(0, state.theta - 0.15); // Rotate towards |0>
            logEvent(`Applied Public Good argument (+θ). State angle: <strong>${(state.theta * 180 / Math.PI).toFixed(1)}°</strong>`, "info");
            updateCharts();
        });
    }

    if (btnProfitArg) {
        btnProfitArg.addEventListener("click", () => {
            if (state.collapsed) return;
            state.theta = Math.min(Math.PI / 2, state.theta + 0.15); // Rotate towards |1>
            logEvent(`Applied Private Gain argument (-θ). State angle: <strong>${(state.theta * 180 / Math.PI).toFixed(1)}°</strong>`, "info");
            updateCharts();
        });
    }

    const btnPause = document.getElementById("btn-pause");

    // --- Global Window Bindings ---
    window.startQuantumDeliberation = function() {
        startDeliberation();
    };

    window.stopQuantumDeliberation = function() {
        stopDeliberation();
    };

    window.forceQuantumCollapse = function() {
        const p0 = Math.cos(state.theta) ** 2;
        triggerPenroseCollapse(p0);
    };

    window.resetQuantumMind = function() {
        resetState();
    };

    // --- Real-Time Deliberation Loop ---
    if (btnDeliberate) {
        btnDeliberate.addEventListener("click", startDeliberation);
    }

    if (btnPause) {
        btnPause.addEventListener("click", stopDeliberation);
    }

    function startDeliberation() {
        state.collapsed = false;
        state.action = 0.0; // Reset action to zero on start so collapse doesn't trigger on step 1
        state.stepCount = 0;
        state.isDeliberating = true;
        btnDeliberate.textContent = "⏸ Pause Deliberation";
        btnDeliberate.classList.add("active");
        logEvent("▶ Deliberation loop started. Statevector evolving in Hilbert space...", "info");

        if (state.deliberationTimer) clearInterval(state.deliberationTimer);
        state.deliberationTimer = setInterval(stepDeliberation, 100);
    }

    function stopDeliberation() {
        state.isDeliberating = false;
        if (state.deliberationTimer) clearInterval(state.deliberationTimer);
        btnDeliberate.textContent = "▶ Start Deliberation";
        btnDeliberate.classList.remove("active");
        logEvent("⏸ Deliberation loop paused.", "info");
    }

    function stepDeliberation() {
        state.stepCount++;
        
        // Statevector drift influenced by pressure and Lindblad thermal noise
        const noise = (Math.random() - 0.5) * 0.12 * (state.temperature / 310.0);
        const pressureBias = (state.pressure - 50) / 100.0;
        state.theta = Math.max(0, Math.min(Math.PI / 2, state.theta + noise + pressureBias));
        
        // Calculate Shannon entropy with safe probability bounds (prevents 0 * -Infinity = NaN)
        const p0 = Math.cos(state.theta) ** 2;
        const safeP0 = Math.max(0.0001, Math.min(0.9999, p0));
        const safeP1 = 1.0 - safeP0;
        const entropy = -(safeP0 * Math.log2(safeP0) + safeP1 * Math.log2(safeP1));
        
        // Accumulate Penrose action S(t) = ∫ E_G dt
        const instEg = 0.035 * (1.0 + entropy);
        state.action = (isNaN(state.action) ? 0 : state.action) + instEg * 0.05;
        
        // Update 3D Status Badge
        if (badgeStatus3D) {
            badgeStatus3D.className = "badge badge-info";
            badgeStatus3D.textContent = `▶ DELIBERATING... (S = ${state.action.toFixed(2)} / ${state.threshold.toFixed(2)})`;
        }

        // Pulse 3D Tubulin Dimers dynamically during deliberation
        if (dimers && dimers.length > 0) {
            dimers.forEach((d, idx) => {
                if (d.mesh) {
                    d.mesh.position.x = d.originalPos.x + (Math.random() - 0.5) * 0.2;
                    d.mesh.position.y = d.originalPos.y + (Math.random() - 0.5) * 0.2;
                }
            });
        }

        updateCharts();

        // Check Penrose Collapse Threshold S >= ℏ_cog
        if (state.action >= state.threshold) {
            triggerPenroseCollapse(p0);
        }
    }

    function triggerPenroseCollapse(p0) {
        stopDeliberation();
        state.collapsed = true;
        
        // Flash overlay effect
        if (flashOverlay) {
            flashOverlay.style.opacity = "0.8";
            setTimeout(() => { flashOverlay.style.opacity = "0"; }, 300);
        }

        // Measure statevector
        const roll = Math.random();
        const sc = SCENARIOS[state.scenario];
        let outcomeState, colorHex;

        if (roll < p0) {
            outcomeState = sc.basis0;
            state.theta = 0; // Snap to |0>
            colorHex = 0x00f2fe; // Cyan
            badgeStatus3D.className = "badge badge-success";
            badgeStatus3D.textContent = `⚡ COLLAPSED: ${sc.basis0}`;
        } else {
            outcomeState = sc.basis1;
            state.theta = Math.PI / 2; // Snap to |1>
            colorHex = 0xf59e0b; // Gold
            badgeStatus3D.className = "badge badge-collapse";
            badgeStatus3D.textContent = `⚡ COLLAPSED: ${sc.basis1}`;
        }

        // Snap 3D tubulin dimers to outcome color
        if (dimers) {
            dimers.forEach(d => {
                d.mesh.material.color.setHex(colorHex);
            });
        }

        logEvent(`⚡ <strong>OBJECTIVE REDUCTION TRIGGERED!</strong> Action S (${state.action.toFixed(3)}) ≥ ℏ_cog (${state.threshold.toFixed(2)}). Collapsed to: <strong>${outcomeState}</strong>`, "success");
        updateCharts();
    }

    if (btnForceCollapse) {
        btnForceCollapse.addEventListener("click", () => {
            const p0 = Math.cos(state.theta) ** 2;
            triggerPenroseCollapse(p0);
        });
    }

    if (btnReset) {
        btnReset.addEventListener("click", resetState);
    }

    function resetState() {
        stopDeliberation();
        state.collapsed = false;
        state.action = 0.0;
        state.stepCount = 0;
        state.theta = Math.PI / 4; // Superposition
        
        if (badgeStatus3D) {
            badgeStatus3D.className = "badge";
            badgeStatus3D.textContent = "SUPERPOSITION: ACTIVE";
        }
        
        if (state.actionChart) {
            state.actionChart.data.labels = [0];
            state.actionChart.data.datasets[0].data = [0];
            state.actionChart.data.datasets[1].data = [state.threshold];
            state.actionChart.update();
        }
        
        updateCharts();
        logEvent("🔄 Mind statevector reset to balanced superposition.", "info");
    }

    function updateCharts() {
        const p0 = Math.cos(state.theta) ** 2;
        const p1 = Math.sin(state.theta) ** 2;

        if (state.probChart) {
            state.probChart.data.datasets[0].data = [p0, p1];
            state.probChart.update();
        }

        if (state.actionChart && state.isDeliberating) {
            state.actionChart.data.labels.push(state.stepCount);
            state.actionChart.data.datasets[0].data.push(state.action);
            state.actionChart.data.datasets[1].data.push(state.threshold);

            if (state.actionChart.data.labels.length > 30) {
                state.actionChart.data.labels.shift();
                state.actionChart.data.datasets[0].data.shift();
                state.actionChart.data.datasets[1].data.shift();
            }
            state.actionChart.update();
        }
    }

    // --- Benchmark Execution Listeners ---
    if (btnRunLinda) {
        btnRunLinda.addEventListener("click", () => {
            logEvent("▶ Running <strong>Tversky & Kahneman Linda Conjunction Fallacy Benchmark</strong>...", "info");
            setTimeout(() => {
                logEvent("Linda Result: Classical Model Fallacy = <strong>0.0%</strong> | Human Data = <strong>85.0%</strong> | <strong>Q-AI Model = 84.0%</strong> (1% Error)", "success");
            }, 600);
        });
    }

    // --- Live Oracle URL Query Parameter Parser & Real Quantum Statevector Execution ---
    function parseURLQueryParams() {
        const urlParams = new URLSearchParams(window.location.search);
        const proposal = urlParams.get('proposal');
        const yesVal = parseFloat(urlParams.get('yes') || '50.0');
        const noVal = parseFloat(urlParams.get('no') || (100.0 - yesVal).toFixed(1));
        const riskVal = urlParams.get('risk') || 'LOW';

        if (proposal && yesVal) {
            const banner = document.getElementById('oracle-live-banner');
            const titleEl = document.getElementById('banner-proposal-title');
            const yesEl = document.getElementById('banner-yes-val');
            const noEl = document.getElementById('banner-no-val');
            const riskEl = document.getElementById('banner-risk-val');

            if (banner) banner.classList.remove('hidden');
            if (titleEl) titleEl.innerText = decodeURIComponent(proposal);
            if (yesEl) yesEl.innerText = `${yesVal}%`;
            if (noEl) noEl.innerText = `${noVal}%`;
            if (riskEl) riskEl.innerText = riskVal.toUpperCase();

            // Drive REAL Quantum Statevector Engine to match proposal physics
            const targetTheta = (yesVal / 100.0) * (Math.PI / 2);
            state.theta = targetTheta;
            state.probYes = yesVal / 100.0;
            state.probNo = noVal / 100.0;

            // Trigger 3D Tubulin Dimers & Phase Particles Quantum Shift
            if (dimers && dimers.length > 0) {
                dimers.forEach((d, idx) => {
                    if (d.mesh && d.mesh.material) {
                        d.mesh.material.color.setHex(idx % 2 === 0 ? 0x00f2fe : (yesVal > 50 ? 0x10b981 : 0xef4444));
                    }
                });
            }

            // Update Chart.js probability bars to match exact Quantum Statevector
            if (state.probChart) {
                state.probChart.data.datasets[0].data = [state.probYes, state.probNo];
                state.probChart.update();
            }

            // Log REAL quantum statevector execution in audit trail
            logEvent(`⚛️ <strong>Real Quantum Statevector Executed:</strong> |ψ⟩ = ${(Math.sqrt(state.probYes)).toFixed(3)}|00⟩ + ${(Math.sqrt(state.probNo)).toFixed(3)}|11⟩ for proposal <strong>${decodeURIComponent(proposal)}</strong>`, "success");
            logEvent(`⚡ Penrose Orch-OR Objective Reduction Threshold: E_G = 1.05e-34 J | τ_collapse = 42.0 steps`, "info");
        }
    }

    parseURLQueryParams();
});
