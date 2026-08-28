// Quantum Cognitive & Game Simulator - app.js

document.addEventListener("DOMContentLoaded", () => {
    // --- Application State ---
    let state = {
        // Mode 1: Cognitive Agent State
        theta: Math.PI / 4, 
        history: [],        
        action: 0.0,        
        threshold: 0.5,     
        dt: 0.02,           
        isDeliberating: false,
        deliberationInterval: null,
        experimentActive: false,
        chartData: {
            labels: [],
            actionVals: [],
            thresholdVals: []
        },

        // Mode 2: Game Theory State
        p1Strategy: "C",
        p2Strategy: "C",
        entanglementPercent: 100, // Slider value [0, 100]
        gameResults: {
            probs: [0, 0, 0, 0], // CC, DC, CD, DD
            payoffs: [0, 0]      // P1, P2
        },

        // Mode 3: Spinozist State
        spinozaThetaA: Math.PI / 4, // Deliberation angle of Mind A [0, pi/2]
        spinozaCollapsed: false,
        spinozaCollapsedStates: [Math.PI / 4, Math.PI / 4] // Mind A, Mind B angles
    };

    // Constants
    const COGNITIVE_ENERGY_BASE = 0.35;
    const DRIFT_SPEED = 0.25;
    const HBAR = 1.0545718e-34; // Cognitive scale maps to values directly

    // --- DOM Elements ---
    
    // Tabs Navigation
    const tabButtons = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");

    // Mode 1: Cognitive Agent Controls
    const selectInitialState = document.getElementById("initial-state");
    const sliderThreshold = document.getElementById("collapse-threshold");
    const valThreshold = document.getElementById("threshold-val");
    const sliderSpeed = document.getElementById("deliberation-speed");
    const valSpeed = document.getElementById("speed-val");
    
    const btnEthicsArg = document.getElementById("btn-ethics-arg");
    const btnProfitArg = document.getElementById("btn-profit-arg");
    const btnDeliberate = document.getElementById("btn-deliberate");
    const btnForceCollapse = document.getElementById("btn-force-collapse");
    const btnReset = document.getElementById("btn-reset");
    
    const btnExpEP = document.getElementById("btn-exp-ep");
    const btnExpPE = document.getElementById("btn-exp-pe");
    const txtExp = document.getElementById("exp-text");
    
    const badgeState = document.getElementById("purity-indicator");
    const badgeAction = document.getElementById("action-indicator");

    // Mode 2: Game Theory Controls
    const selectP1Strategy = document.getElementById("p1-strategy");
    const selectP2Strategy = document.getElementById("p2-strategy");
    const sliderEntanglement = document.getElementById("game-entanglement");
    const valEntanglement = document.getElementById("entanglement-val");
    const btnPlayGame = document.getElementById("btn-play-game");

    const badgeGameState = document.getElementById("game-state-indicator");
    const cellCC = document.getElementById("cell-CC");
    const cellCD = document.getElementById("cell-CD");
    const cellDC = document.getElementById("cell-DC");
    const cellDD = document.getElementById("cell-DD");
    const probCC = document.getElementById("prob-CC");
    const probCD = document.getElementById("prob-CD");
    const probDC = document.getElementById("prob-DC");
    const probDD = document.getElementById("prob-DD");

    // Mode 3: Spinozist Controls
    const sliderSpinozaTheta = document.getElementById("spinoza-theta");
    const valSpinozaTheta = document.getElementById("spinoza-theta-val");
    const btnSpinozaEthics = document.getElementById("btn-spinoza-ethics");
    const btnSpinozaProfit = document.getElementById("btn-spinoza-profit");
    const btnSpinozaCollapse = document.getElementById("btn-spinoza-collapse");
    const badgeSpinozaState = document.getElementById("spinoza-state-indicator");
    
    const harmonyAgreeVal = document.getElementById("harmony-agreement-val");
    const harmonyDisagreeVal = document.getElementById("harmony-disagree-val");
    const harmonyBarAgree = document.getElementById("harmony-bar-agree");
    const harmonyBarDisagree = document.getElementById("harmony-bar-disagree");

    // Common Elements
    const logConsole = document.getElementById("log-console");
    const flashOverlay = document.getElementById("collapse-flash");

    // --- Canvas Setup (Mode 1 & Mode 3) ---
    const canvas = document.getElementById("vector-canvas");
    const ctx = canvas.getContext("2d");
    
    const canvasSpinozaA = document.getElementById("spinoza-canvas-a");
    const ctxSpinozaA = canvasSpinozaA.getContext("2d");
    const canvasSpinozaB = document.getElementById("spinoza-canvas-b");
    const ctxSpinozaB = canvasSpinozaB.getContext("2d");
    
    function resizeCanvases() {
        // Mode 1 Canvas
        const container = canvas.parentElement;
        if (container && canvas) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            drawStateSpace();
        }
        
        // Mode 3 Canvases
        const wrapA = canvasSpinozaA.parentElement;
        if (wrapA && canvasSpinozaA && canvasSpinozaB) {
            canvasSpinozaA.width = wrapA.clientWidth;
            canvasSpinozaA.height = wrapA.clientHeight;
            canvasSpinozaB.width = wrapA.clientWidth;
            canvasSpinozaB.height = wrapA.clientHeight;
            drawSpinozaCanvases();
        }
    }
    window.addEventListener("resize", resizeCanvases);

    // --- Tab Switching Logic ---
    tabButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            // Remove active classes
            tabButtons.forEach(b => b.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active-content"));
            
            // Add active classes
            btn.classList.add("active");
            
            const target = btn.getAttribute("data-target");
            if (target === "agent-tab") {
                document.getElementById("agent-controls").classList.add("active-content");
                document.getElementById("agent-visuals").classList.add("active-content");
                logEvent("Switched to Mode 1: Cognitive Agent Simulator.", "system");
                resizeCanvases();
            } else if (target === "game-tab") {
                document.getElementById("game-controls").classList.add("active-content");
                document.getElementById("game-visuals").classList.add("active-content");
                logEvent("Switched to Mode 2: Quantum Game Theory Simulator.", "system");
                runQuantumGame();
            } else if (target === "spinoza-tab") {
                document.getElementById("spinoza-controls").classList.add("active-content");
                document.getElementById("spinoza-visuals").classList.add("active-content");
                logEvent("Switched to Mode 3: Spinozist Entangled Intellect.", "system");
                state.spinozaCollapsed = false;
                updateSpinozaUI();
                resizeCanvases();
            }
        });
    });

    // --- Chart.js Setup ---
    
    // Mode 1: Action Chart
    const chartCtx = document.getElementById("action-chart").getContext("2d");
    let actionChart = new Chart(chartCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Accumulated Action',
                    data: [],
                    borderColor: '#00f2fe',
                    backgroundColor: 'rgba(0, 242, 254, 0.05)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.1,
                    pointRadius: 0
                },
                {
                    label: 'Collapse Threshold',
                    data: [],
                    borderColor: '#ff0844',
                    borderWidth: 1.5,
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { color: 'rgba(255, 255, 255, 0.03)' }, ticks: { display: false } },
                y: { grid: { color: 'rgba(255, 255, 255, 0.03)' }, ticks: { color: '#9ca3af', font: { size: 9 } }, min: 0, max: 1.6 }
            }
        }
    });

    // Mode 2: Game Outcome Chart
    const gameChartCtx = document.getElementById("game-chart").getContext("2d");
    let gameChart = new Chart(gameChartCtx, {
        type: 'bar',
        data: {
            labels: ['|CC> (Cooperate)', '|DC> (P1 Defect)', '|CD> (P2 Defect)', '|DD> (Defect)'],
            datasets: [{
                label: 'Eigenstate Resolution Probability',
                data: [0.25, 0.25, 0.25, 0.25],
                backgroundColor: [
                    '#10b981', // CC green
                    '#00f2fe', // DC cyan
                    '#a855f7', // CD purple
                    '#ff0844'  // DD red
                ],
                borderWidth: 0,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false }, ticks: { color: '#9ca3af', font: { size: 10 } } },
                y: { grid: { color: 'rgba(255, 255, 255, 0.03)' }, ticks: { color: '#9ca3af', font: { size: 9 } }, min: 0, max: 1.0 }
            }
        }
    });

    // --- Logging Utility ---
    function logEvent(message, type = "info") {
        const entry = document.createElement("div");
        entry.className = `log-entry ${type}`;
        entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
        logConsole.appendChild(entry);
        logConsole.scrollTop = logConsole.scrollHeight;
    }

    // --- MODE 1: COGNITIVE AGENT MATHEMATICS ---
    function getAmplitudes() {
        return {
            ethics: Math.sin(state.theta),
            profit: Math.cos(state.theta)
        };
    }

    function getProbabilities() {
        const amps = getAmplitudes();
        return {
            ethics: amps.ethics ** 2,
            profit: amps.profit ** 2
        };
    }

    function calculateCognitiveEntropy() {
        const p = getProbabilities();
        if (p.ethics < 1e-6 || p.profit < 1e-6) return 0.0;
        return - (p.ethics * Math.log2(p.ethics) + p.profit * Math.log2(p.profit));
    }

    // Render Canvas
    function drawStateSpace() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const radius = Math.min(canvas.width, canvas.height) * 0.35;
        
        // Grid
        ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(centerX - radius * 1.2, centerY);
        ctx.lineTo(centerX + radius * 1.2, centerY);
        ctx.moveTo(centerX, centerY - radius * 1.2);
        ctx.lineTo(centerX, centerY + radius * 1.2);
        ctx.stroke();
        
        // Circle
        ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Trajectory
        if (state.history.length > 1) {
            ctx.strokeStyle = "rgba(0, 242, 254, 0.15)";
            ctx.lineWidth = 2;
            ctx.beginPath();
            const firstAngle = state.history[0];
            ctx.moveTo(centerX + radius * Math.cos(firstAngle), centerY - radius * Math.sin(firstAngle));
            for (let i = 1; i < state.history.length; i++) {
                const ang = state.history[i];
                ctx.lineTo(centerX + radius * Math.cos(ang), centerY - radius * Math.sin(ang));
            }
            ctx.stroke();
        }
        
        // Vector
        const vectorX = centerX + radius * Math.cos(state.theta);
        const vectorY = centerY - radius * Math.sin(state.theta);
        
        ctx.shadowBlur = 15;
        ctx.shadowColor = "#00f2fe";
        ctx.strokeStyle = "#00f2fe";
        ctx.lineWidth = 4.5;
        ctx.lineCap = "round";
        
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(vectorX, vectorY);
        ctx.stroke();
        
        ctx.shadowBlur = 0;
        
        ctx.fillStyle = "#ffffff";
        ctx.beginPath();
        ctx.arc(vectorX, vectorY, 5, 0, 2 * Math.PI);
        ctx.fill();
    }

    function updateStateUI() {
        valThreshold.textContent = state.threshold.toFixed(2);
        valSpeed.textContent = state.dt.toFixed(3) + "s";
        
        badgeAction.textContent = `Action: ${state.action.toFixed(3)} / ${state.threshold.toFixed(2)}`;
        
        const entropy = calculateCognitiveEntropy();
        if (entropy < 0.15) {
            badgeState.className = "badge badge-success";
            badgeState.textContent = "State: Near Collapsed";
        } else {
            badgeState.className = "badge";
            badgeState.style.color = "#a855f7";
            badgeState.style.background = "rgba(168, 85, 247, 0.08)";
            badgeState.textContent = `State: Coherent (Tension: ${(entropy * 100).toFixed(0)}%)`;
        }
    }

    function resetMind(initialType = null) {
        const type = initialType || selectInitialState.value;
        
        if (type === "superposition") {
            state.theta = Math.PI / 4;
        } else if (type === "ethical") {
            state.theta = Math.PI / 2 - 0.1;
        } else if (type === "profit") {
            state.theta = 0.1;
        }
        
        state.action = 0.0;
        state.history = [state.theta];
        
        state.chartData.labels = [0];
        state.chartData.actionVals = [0.0];
        state.chartData.thresholdVals = [state.threshold];
        
        actionChart.data.labels = state.chartData.labels;
        actionChart.data.datasets[0].data = state.chartData.actionVals;
        actionChart.data.datasets[1].data = state.chartData.thresholdVals;
        actionChart.update();
        
        if (state.isDeliberating) {
            toggleDeliberation();
        }
        
        updateStateUI();
        drawStateSpace();
        state.experimentActive = false;
        
        logEvent(`Mind state reset to: <b>${type.toUpperCase()}</b>`, "system");
    }

    function rotateMind(deltaAngle) {
        state.theta = (state.theta + deltaAngle) % (2 * Math.PI);
        if (state.theta < 0) state.theta = 0;
        if (state.theta > Math.PI / 2) state.theta = Math.PI / 2;
        
        state.history.push(state.theta);
        if (state.history.length > 200) state.history.shift();
        
        drawStateSpace();
        updateStateUI();
    }

    function toggleDeliberation() {
        if (state.isDeliberating) {
            clearInterval(state.deliberationInterval);
            state.isDeliberating = false;
            btnDeliberate.textContent = "Toggle Deliberation";
            btnDeliberate.classList.remove("active");
            logEvent("Deliberation paused.", "system");
        } else {
            state.isDeliberating = true;
            btnDeliberate.textContent = "Deliberating...";
            btnDeliberate.classList.add("active");
            logEvent("Deliberation started. Mind-vector drifting...", "info");
            state.deliberationInterval = setInterval(deliberateStep, 50);
        }
    }

    function deliberateStep() {
        const noise = (Math.random() - 0.5) * DRIFT_SPEED * state.dt;
        state.theta = (state.theta + noise) % (2 * Math.PI);
        if (state.theta < 0) state.theta = 0;
        if (state.theta > Math.PI / 2) state.theta = Math.PI / 2;
        
        state.history.push(state.theta);
        if (state.history.length > 200) state.history.shift();
        
        const entropy = calculateCognitiveEntropy();
        const instEnergy = entropy * COGNITIVE_ENERGY_BASE;
        state.action += instEnergy * state.dt;
        
        const nextIdx = state.chartData.labels.length;
        state.chartData.labels.push(nextIdx);
        state.chartData.actionVals.push(state.action);
        state.chartData.thresholdVals.push(state.threshold);
        
        if (state.chartData.labels.length > 100) {
            state.chartData.labels.shift();
            state.chartData.actionVals.shift();
            state.chartData.thresholdVals.shift();
        }
        
        actionChart.update('none');
        updateStateUI();
        drawStateSpace();
        
        if (state.action >= state.threshold) {
            triggerObjectiveReduction();
        }
    }

    function triggerObjectiveReduction() {
        if (state.isDeliberating) {
            clearInterval(state.deliberationInterval);
            state.isDeliberating = false;
            btnDeliberate.textContent = "Toggle Deliberation";
            btnDeliberate.classList.remove("active");
        }
        
        const p = getProbabilities();
        const roll = Math.random();
        
        let finalState;
        let logStyle;
        let collapseColorHex;

        if (roll < p.ethics) {
            state.theta = Math.PI / 2;
            finalState = "|ETHICS> (Choose Fairness)";
            logStyle = "success";
            collapseColorHex = 0x00f2fe; // Cyan
        } else {
            state.theta = 0.0;
            finalState = "|PROFIT> (Choose Money)";
            logStyle = "collapse";
            collapseColorHex = 0xf59e0b; // Gold
        }
        
        state.history.push(state.theta);
        
        // 1. Flash Screen Overlay
        flashOverlay.classList.add("active");
        setTimeout(() => { flashOverlay.classList.remove("active"); }, 120);
        
        // 2. Animate 3D Microtubule Collapse
        const statusBadge3D = document.getElementById("microtubule-3d-status");
        if (statusBadge3D) {
            statusBadge3D.className = "badge badge-success";
            statusBadge3D.style.background = "rgba(239, 68, 68, 0.2)";
            statusBadge3D.style.color = "#ef4444";
            statusBadge3D.textContent = `⚡ COLLAPSED: ${finalState.split(" ")[0]}`;
        }

        if (tubulinDimers && tubulinDimers.length > 0) {
            tubulinDimers.forEach(d => {
                d.mesh.material.color.setHex(collapseColorHex);
                d.mesh.material.emissive.setHex(collapseColorHex);
            });
        }

        logEvent("⚡ <b>OBJECTIVE REDUCTION TRIGGERED (S >= &hbar;<sub>cog</sub>)</b> ⚡", "collapse");
        logEvent(`Spontaneous Penrose Collapse! State vector resolved to: <b>${finalState}</b>`, logStyle);
        
        state.action = 0.0;
        updateStateUI();
        drawStateSpace();
    }

    // Order of Questions Experiments
    function runQuestionOrderExperiment(firstQuestion) {
        if (state.isDeliberating) toggleDeliberation();
        state.experimentActive = true;
        
        state.theta = Math.PI / 4;
        state.history = [state.theta];
        state.action = 0.0;
        logEvent(`--- Commencing Question-Order Experiment ---`, "system");
        logEvent(`Initial state: <b>Balanced Superposition</b>`, "info");
        
        if (firstQuestion === 'ethics') {
            txtExp.innerHTML = "<b>Sequence: Ethics &rarr; Profit</b><br>1. Ask 'Is it Ethical?'<br>2. Ask 'Is it Profitable?'";
            
            setTimeout(() => {
                const p = getProbabilities();
                const roll = Math.random();
                const choiceEthics = roll < p.ethics;
                state.theta = choiceEthics ? Math.PI / 2 : -Math.PI / 2;
                state.history.push(state.theta);
                drawStateSpace();
                logEvent(`Question 1 ('Is it Ethical?') asked. State collapsed to: <b>${choiceEthics ? '|ETHICS>' : '|-ETHICS>'}</b>`, "info");
                
                setTimeout(() => {
                    const roll2 = Math.random();
                    const choiceProfit = roll2 < 0.5;
                    state.theta = choiceProfit ? 0.0 : Math.PI;
                    state.history.push(state.theta);
                    drawStateSpace();
                    logEvent(`Question 2 ('Is it Profitable?') asked. State collapsed to: <b>${choiceProfit ? '|PROFIT>' : '|-PROFIT>'}</b>`, "success");
                    logEvent(`Experiment complete! Final state is classical.`, "system");
                }, 1200);
            }, 800);
            
        } else {
            txtExp.innerHTML = "<b>Sequence: Profit &rarr; Ethics</b><br>1. Ask 'Is it Profitable?'<br>2. Ask 'Is it Ethical?'";
            
            setTimeout(() => {
                const p = getProbabilities();
                const roll = Math.random();
                const choiceProfit = roll < p.profit;
                state.theta = choiceProfit ? 0.0 : Math.PI;
                state.history.push(state.theta);
                drawStateSpace();
                logEvent(`Question 1 ('Is it Profitable?') asked. State collapsed to: <b>${choiceProfit ? '|PROFIT>' : '|-PROFIT>'}</b>`, "info");
                
                setTimeout(() => {
                    const roll2 = Math.random();
                    const choiceEthics = roll2 < 0.5;
                    state.theta = choiceEthics ? Math.PI / 2 : -Math.PI / 2;
                    state.history.push(state.theta);
                    drawStateSpace();
                    logEvent(`Question 2 ('Is it Ethical?') asked. State collapsed to: <b>${choiceEthics ? '|ETHICS>' : '|-ETHICS>'}</b>`, "success");
                    logEvent(`Experiment complete! Final state is classical.`, "system");
                }, 1200);
            }, 800);
        }
    }


    // --- MODE 2: QUANTUM GAME THEORY (EWL SCHEME) ---

    function runQuantumGame() {
        const gamma = (parseFloat(sliderEntanglement.value) / 100) * (Math.PI / 2);
        
        let psi = [
            {re: 1.0, im: 0.0},
            {re: 0.0, im: 0.0},
            {re: 0.0, im: 0.0},
            {re: 0.0, im: 0.0}
        ];
        
        const cos_g = Math.cos(gamma / 2);
        const sin_g = Math.sin(gamma / 2);
        
        psi[0] = { re: cos_g, im: 0.0 };
        psi[3] = { re: 0.0, im: sin_g }; 

        psi = applyQubitStrategy(psi, state.p1Strategy, 0);
        psi = applyQubitStrategy(psi, state.p2Strategy, 1);
        
        let finalPsi = [ {re:0, im:0}, {re:0, im:0}, {re:0, im:0}, {re:0, im:0} ];
        for (let k = 0; k < 4; k++) {
            const target = k ^ 3; 
            const term1 = { re: cos_g * psi[k].re, im: cos_g * psi[k].im };
            const term2 = { re: sin_g * psi[target].im, im: -sin_g * psi[target].re };
            
            finalPsi[k] = {
                re: term1.re + term2.re,
                im: term1.im + term2.im
            };
        }
        
        const probs = finalPsi.map(z => z.re ** 2 + z.im ** 2);
        
        const p_CC = probs[0];
        const p_DC = probs[1];
        const p_CD = probs[2];
        const p_DD = probs[3];
        
        const payoff1 = 3 * p_CC + 5 * p_DC + 0 * p_CD + 1 * p_DD;
        const payoff2 = 3 * p_CC + 0 * p_DC + 5 * p_CD + 1 * p_DD;
        
        state.gameResults.probs = [p_CC, p_DC, p_CD, p_DD];
        state.gameResults.payoffs = [payoff1, payoff2];
        
        probCC.textContent = (p_CC * 100).toFixed(0) + "%";
        probDC.textContent = (p_DC * 100).toFixed(0) + "%";
        probCD.textContent = (p_CD * 100).toFixed(0) + "%";
        probDD.textContent = (p_DD * 100).toFixed(0) + "%";
        
        [cellCC, cellDC, cellCD, cellDD].forEach(cell => cell.classList.remove("active-cell"));
        
        if (p_CC > 0.02) cellCC.classList.add("active-cell");
        if (p_DC > 0.02) cellDC.classList.add("active-cell");
        if (p_CD > 0.02) cellCD.classList.add("active-cell");
        if (p_DD > 0.02) cellDD.classList.add("active-cell");
        
        gameChart.data.datasets[0].data = [p_CC, p_DC, p_CD, p_DD];
        gameChart.update();
        
        if (state.entanglementPercent === 0) {
            badgeGameState.className = "badge";
            badgeGameState.style.color = "#ff0844";
            badgeGameState.style.background = "rgba(255, 8, 68, 0.08)";
            badgeGameState.textContent = "State: Classical Game (No Entanglement)";
        } else if (state.entanglementPercent === 100) {
            badgeGameState.className = "badge badge-success";
            badgeGameState.textContent = "State: Maximally Entangled Qubits";
        } else {
            badgeGameState.className = "badge";
            badgeGameState.style.color = "#00f2fe";
            badgeGameState.style.background = "rgba(0, 242, 254, 0.08)";
            badgeGameState.textContent = `State: Entangled (&gamma; = ${state.entanglementPercent}%)`;
        }
        
        logEvent(`Game simulation run. Expected Payoffs: <b>P1 = ${payoff1.toFixed(2)}</b>, <b>P2 = ${payoff2.toFixed(2)}</b>`, "success");
        if (state.p1Strategy === "Q" && state.p2Strategy === "Q" && state.entanglementPercent === 100) {
            logEvent("💫 <b>Quantum Nash Equilibrium reached!</b> Cooperative strategy (Q, Q) resolves the Prisoner's Dilemma.", "success");
        } else if (state.p1Strategy === "Q" && state.p2Strategy === "D" && state.entanglementPercent === 100) {
            logEvent("⚠️ Player 1 (Quantum) completely exploited Player 2 (Classical Defector). Payoff: (5.00, 0.00).", "info");
        }
    }

    function applyQubitStrategy(psi, strategy, qubit) {
        let nextPsi = [ {re:0, im:0}, {re:0, im:0}, {re:0, im:0}, {re:0, im:0} ];
        
        if (strategy === "C") {
            for (let k = 0; k < 4; k++) nextPsi[k] = { ...psi[k] };
        } else if (strategy === "D") {
            for (let k = 0; k < 4; k++) {
                let target = k ^ (1 << qubit);
                nextPsi[target] = { ...psi[k] };
            }
        } else if (strategy === "Q") {
            for (let k = 0; k < 4; k++) {
                let bitVal = (k >> qubit) & 1;
                if (bitVal === 0) {
                    nextPsi[k] = { re: -psi[k].im, im: psi[k].re };
                } else {
                    nextPsi[k] = { re: psi[k].im, im: -psi[k].re };
                }
            }
        }
        return nextPsi;
    }

    // --- Mode 2 Event Listeners ---
    selectP1Strategy.addEventListener("change", (e) => {
        state.p1Strategy = e.target.value;
        logEvent(`Player 1 selected strategy: <b>${state.p1Strategy}</b>`, "system");
        runQuantumGame();
    });
    
    selectP2Strategy.addEventListener("change", (e) => {
        state.p2Strategy = e.target.value;
        logEvent(`Player 2 selected strategy: <b>${state.p2Strategy}</b>`, "system");
        runQuantumGame();
    });
    
    sliderEntanglement.addEventListener("input", (e) => {
        state.entanglementPercent = parseInt(e.target.value);
        valEntanglement.textContent = `${state.entanglementPercent}%` + 
            (state.entanglementPercent === 100 ? " (Maximum)" : state.entanglementPercent === 0 ? " (Classical)" : "");
        runQuantumGame();
    });

    btnPlayGame.addEventListener("click", () => {
        const matrixCard = document.querySelector(".matrix-container").parentElement;
        matrixCard.style.boxShadow = "0 0 30px rgba(0, 242, 254, 0.4)";
        setTimeout(() => {
            matrixCard.style.boxShadow = "";
        }, 300);
        logEvent("Executing quantum game circuit...", "info");
        runQuantumGame();
    });


    // --- MODE 3: SPINOZIST ENTANGLED INTELLECT ---

    function drawSpinozaCanvases() {
        drawSingleSpinozaCanvas(canvasSpinozaA, ctxSpinozaA, state.spinozaCollapsed ? state.spinozaCollapsedStates[0] : state.spinozaThetaA, "A");
        drawSingleSpinozaCanvas(canvasSpinozaB, ctxSpinozaB, state.spinozaCollapsed ? state.spinozaCollapsedStates[1] : state.spinozaThetaA, "B", true);
    }

    function drawSingleSpinozaCanvas(canv, c_ctx, theta, label, isFaded = false) {
        c_ctx.clearRect(0, 0, canv.width, canv.height);
        
        const centerX = canv.width / 2;
        const centerY = canv.height / 2;
        const radius = Math.min(canv.width, canv.height) * 0.32;
        
        // Grid lines
        c_ctx.strokeStyle = "rgba(255, 255, 255, 0.04)";
        c_ctx.lineWidth = 1;
        c_ctx.beginPath();
        c_ctx.moveTo(centerX - radius * 1.2, centerY);
        c_ctx.lineTo(centerX + radius * 1.2, centerY);
        c_ctx.moveTo(centerX, centerY - radius * 1.2);
        c_ctx.lineTo(centerX, centerY + radius * 1.2);
        c_ctx.stroke();
        
        // Circle border
        c_ctx.strokeStyle = isFaded ? "rgba(255, 255, 255, 0.04)" : "rgba(255, 255, 255, 0.08)";
        c_ctx.lineWidth = 2;
        c_ctx.beginPath();
        c_ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI);
        c_ctx.stroke();
        
        // Vector coordinates
        const vectorX = centerX + radius * Math.cos(theta);
        const vectorY = centerY - radius * Math.sin(theta);
        
        // Vector styling
        c_ctx.shadowBlur = isFaded ? 5 : 12;
        c_ctx.shadowColor = isFaded ? "rgba(168, 85, 247, 0.5)" : "#00f2fe";
        c_ctx.strokeStyle = isFaded ? "rgba(168, 85, 247, 0.7)" : "#00f2fe";
        c_ctx.lineWidth = 3.5;
        
        if (isFaded && !state.spinozaCollapsed) {
            c_ctx.setLineDash([4, 4]); // Dashed line to show it is an entangled projection
        } else {
            c_ctx.setLineDash([]);
        }
        
        c_ctx.beginPath();
        c_ctx.moveTo(centerX, centerY);
        c_ctx.lineTo(vectorX, vectorY);
        c_ctx.stroke();
        
        c_ctx.setLineDash([]);
        c_ctx.shadowBlur = 0;
        
        // Vector endpoint
        c_ctx.fillStyle = "#ffffff";
        c_ctx.beginPath();
        c_ctx.arc(vectorX, vectorY, 4, 0, 2 * Math.PI);
        c_ctx.fill();
    }

    function updateSpinozaUI() {
        const thetaDegrees = (state.spinozaThetaA * 180 / Math.PI).toFixed(1);
        valSpinozaTheta.textContent = `${thetaDegrees}° (theta A)`;
        
        if (state.spinozaCollapsed) {
            badgeSpinozaState.className = "badge badge-collapse";
            badgeSpinozaState.textContent = "State: Collapsed (Resolved)";
            badgeSpinozaState.style.animation = "flash-badge 1s infinite";
        } else {
            badgeSpinozaState.className = "badge badge-success";
            badgeSpinozaState.textContent = "State: Entangled Bell State";
            badgeSpinozaState.style.animation = "none";
        }

        // Metaphysical Harmony Calculations
        // P(Agreement) = cos^2(thetaA/2)
        // P(Disagreement) = sin^2(thetaA/2)
        const pAgree = Math.cos(state.spinozaThetaA / 2) ** 2;
        const pDisagree = Math.sin(state.spinozaThetaA / 2) ** 2;
        
        const agreePercent = Math.round(pAgree * 100);
        const disagreePercent = Math.round(pDisagree * 100);
        
        harmonyAgreeVal.textContent = agreePercent + "%";
        harmonyDisagreeVal.textContent = disagreePercent + "%";
        harmonyBarAgree.style.width = agreePercent + "%";
        harmonyBarDisagree.style.width = disagreePercent + "%";
    }

    function runSpinozaCollapse() {
        state.spinozaCollapsed = true;
        
        const pAgree = Math.cos(state.spinozaThetaA / 2) ** 2;
        const roll = Math.random();
        
        let decisionA, decisionB;
        if (roll < pAgree) {
            // Minds agree! Roll 50/50 for both choosing Ethics (pi/2) or both choosing Profit (0)
            const bothEthics = Math.random() < 0.5;
            decisionA = bothEthics ? Math.PI / 2 : 0;
            decisionB = decisionA; // Perfect correlation
            logEvent("💫 <b>METAPHYSICAL HARMONY:</b> Both minds resolved in complete agreement!", "success");
        } else {
            // Minds disagree! Roll 50/50 for which is which
            const aEthics = Math.random() < 0.5;
            decisionA = aEthics ? Math.PI / 2 : 0;
            decisionB = aEthics ? 0 : Math.PI / 2; // Anti-correlated
            logEvent("⚠️ <b>ATTRIBUTE SEPARATION:</b> The dual modes collapsed into disagreement.", "info");
        }
        
        state.spinozaCollapsedStates = [decisionA, decisionB];
        
        // Trigger visual flash
        flashOverlay.classList.add("active");
        setTimeout(() => { flashOverlay.classList.remove("active"); }, 100);
        
        logEvent(`⚡ <b>Spinozist Collapse Triggered</b> ⚡`, "collapse");
        logEvent(`Mind A resolved to: <b>${decisionA === Math.PI/2 ? '|ETHICS>' : '|PROFIT>'}</b>`, "info");
        logEvent(`Mind B resolved to: <b>${decisionB === Math.PI/2 ? '|ETHICS>' : '|PROFIT>'}</b>`, "info");
        
        updateSpinozaUI();
        drawSpinozaCanvases();
    }

    // --- Mode 3 Event Listeners ---
    sliderSpinozaTheta.addEventListener("input", (e) => {
        state.spinozaCollapsed = false;
        state.spinozaThetaA = parseFloat(e.target.value);
        logEvent(`Applied sensory input to Mind A: <b>&theta;<sub>A</sub> = ${(state.spinozaThetaA * 180 / Math.PI).toFixed(0)}°</b>`, "system");
        updateSpinozaUI();
        drawSpinozaCanvases();
    });

    btnSpinozaEthics.addEventListener("click", () => {
        state.spinozaCollapsed = false;
        state.spinozaThetaA = Math.PI / 2;
        sliderSpinozaTheta.value = state.spinozaThetaA;
        logEvent("Mind A sensory input rotated to pure <b>|Ethics></b> (90°).", "info");
        updateSpinozaUI();
        drawSpinozaCanvases();
    });

    btnSpinozaProfit.addEventListener("click", () => {
        state.spinozaCollapsed = false;
        state.spinozaThetaA = 0.0;
        sliderSpinozaTheta.value = state.spinozaThetaA;
        logEvent("Mind A sensory input rotated to pure <b>|Profit></b> (0°).", "info");
        updateSpinozaUI();
        drawSpinozaCanvases();
    });

    btnSpinozaCollapse.addEventListener("click", () => {
        runSpinozaCollapse();
    });


    // --- Mode 1 Controls Event Listeners ---
    selectInitialState.addEventListener("change", () => resetMind());
    
    sliderThreshold.addEventListener("input", (e) => {
        state.threshold = parseFloat(e.target.value);
        updateStateUI();
    });
    
    sliderSpeed.addEventListener("input", (e) => {
        state.dt = parseFloat(e.target.value);
        updateStateUI();
    });

    btnReset.addEventListener("click", () => resetMind());
    
    btnEthicsArg.addEventListener("click", () => {
        logEvent("Ethical arguments presented. Vector rotated toward <b>|Ethics></b> (+0.12 rad).", "info");
        rotateMind(0.12);
    });
    
    btnProfitArg.addEventListener("click", () => {
        logEvent("Profitability statistics presented. Vector rotated toward <b>|Profit></b> (-0.12 rad).", "info");
        rotateMind(-0.12);
    });

    btnDeliberate.addEventListener("click", toggleDeliberation);
    if (btnForceCollapse) btnForceCollapse.addEventListener("click", triggerObjectiveReduction);

    btnExpEP.addEventListener("click", () => runQuestionOrderExperiment('ethics'));
    btnExpPE.addEventListener("click", () => runQuestionOrderExperiment('profit'));

    // --- Three.js 3D Microtubule Lattice Engine ---
    let scene3D, camera3D, renderer3D, microtubuleGroup;
    let tubulinDimers = [];
    let phaseTime = 0;

    function init3DMicrotubule() {
        const container = document.getElementById("microtubule-3d-canvas");
        if (!container || typeof THREE === "undefined") return;

        scene3D = new THREE.Scene();
        camera3D = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
        camera3D.position.set(0, 0, 24);

        renderer3D = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer3D.setSize(container.clientWidth, container.clientHeight);
        renderer3D.setPixelRatio(window.devicePixelRatio);
        container.innerHTML = "";
        container.appendChild(renderer3D.domElement);

        // Ambient & Directional Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene3D.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0x00f2fe, 1.2);
        dirLight.position.set(10, 20, 15);
        scene3D.add(dirLight);

        const pointLight = new THREE.PointLight(0xa855f7, 1.5, 50);
        pointLight.position.set(-10, -10, 10);
        scene3D.add(pointLight);

        // 13-protofilament cylindrical microtubule geometry
        microtubuleGroup = new THREE.Group();
        tubulinDimers = [];

        const protofilaments = 13;
        const rings = 10;
        const radius = 5.5;
        const heightStep = 1.2;

        const sphereGeo = new THREE.SphereGeometry(0.45, 16, 16);

        for (let ring = 0; ring < rings; ring++) {
            const y = (ring - rings / 2) * heightStep;
            const ringPhaseShift = (ring * 1.5 * Math.PI) / protofilaments; // Helical skew

            for (let pf = 0; pf < protofilaments; pf++) {
                const angle = (pf * 2 * Math.PI) / protofilaments + ringPhaseShift;
                const x = radius * Math.cos(angle);
                const z = radius * Math.sin(angle);

                const mat = new THREE.MeshStandardMaterial({
                    color: 0x00f2fe,
                    emissive: 0x003344,
                    roughness: 0.3,
                    metalness: 0.5
                });

                const dimer = new THREE.Mesh(sphereGeo, mat);
                dimer.position.set(x, y, z);
                microtubuleGroup.add(dimer);

                tubulinDimers.push({
                    mesh: dimer,
                    angle: angle,
                    ring: ring,
                    pf: pf
                });
            }
        }

        scene3D.add(microtubuleGroup);

        // Animation Loop
        function animate3D() {
            requestAnimationFrame(animate3D);

            if (microtubuleGroup) {
                microtubuleGroup.rotation.y += 0.005;
                microtubuleGroup.rotation.x = Math.sin(Date.now() * 0.0005) * 0.15;
            }

            // Phase Wave propagation during deliberation
            phaseTime += 0.03;
            tubulinDimers.forEach((d, idx) => {
                const wave = Math.sin(phaseTime + d.ring * 0.4 + d.pf * 0.3);
                if (state.isDeliberating) {
                    const r = 0.5 + 0.5 * wave;
                    const g = 0.2 + 0.3 * Math.cos(phaseTime + idx);
                    const b = 0.9;
                    d.mesh.material.color.setRGB(r, g, b);
                    d.mesh.material.emissive.setRGB(r * 0.3, g * 0.1, b * 0.3);
                }
            });

            renderer3D.render(scene3D, camera3D);
        }

        animate3D();
    }

    // --- Initialization ---
    resizeCanvases();
    resetMind("superposition");
    init3DMicrotubule();
});
