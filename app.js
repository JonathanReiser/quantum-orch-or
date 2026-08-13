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
        }
    };

    // Constants
    const COGNITIVE_ENERGY_BASE = 0.08;
    const DRIFT_SPEED = 0.15;
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

    // Common Elements
    const logConsole = document.getElementById("log-console");
    const flashOverlay = document.getElementById("collapse-flash");

    // --- Canvas Setup (Mode 1) ---
    const canvas = document.getElementById("vector-canvas");
    const ctx = canvas.getContext("2d");
    
    function resizeCanvas() {
        const container = canvas.parentElement;
        if (container && canvas) {
            canvas.width = container.clientWidth;
            canvas.height = container.clientHeight;
            drawStateSpace();
        }
    }
    window.addEventListener("resize", resizeCanvas);

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
                resizeCanvas();
            } else {
                document.getElementById("game-controls").classList.add("active-content");
                document.getElementById("game-visuals").classList.add("active-content");
                logEvent("Switched to Mode 2: Quantum Game Theory Simulator.", "system");
                runQuantumGame();
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
        clearInterval(state.deliberationInterval);
        state.isDeliberating = false;
        btnDeliberate.textContent = "Toggle Deliberation";
        btnDeliberate.classList.remove("active");
        
        const p = getProbabilities();
        const roll = Math.random();
        
        let finalState;
        let logStyle;
        if (roll < p.ethics) {
            state.theta = Math.PI / 2;
            finalState = "|ETHICS> (Choose Fairness)";
            logStyle = "success";
        } else {
            state.theta = 0.0;
            finalState = "|PROFIT> (Choose Money)";
            logStyle = "collapse";
        }
        
        state.history.push(state.theta);
        
        flashOverlay.classList.add("active");
        setTimeout(() => { flashOverlay.classList.remove("active"); }, 100);
        
        logEvent("⚡ <b>OBJECTIVE REDUCTION TRIGGERED</b> ⚡", "collapse");
        logEvent(`Superposition collapsed! Agent resolved to: <b>${finalState}</b>`, logStyle);
        
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

    // Complex math helpers
    // Complex number structure: {re: float, im: float}
    function c_mult(z1, z2) {
        return {
            re: z1.re * z2.re - z1.im * z2.im,
            im: z1.re * z2.im + z1.im * z2.re
        };
    }

    function runQuantumGame() {
        const gamma = (parseFloat(sliderEntanglement.value) / 100) * (Math.PI / 2);
        
        // 1. Initial State |00> (CC)
        // psi represents the 4-dimensional statevector: index 0 (CC), 1 (DC), 2 (CD), 3 (DD)
        let psi = [
            {re: 1.0, im: 0.0},
            {re: 0.0, im: 0.0},
            {re: 0.0, im: 0.0},
            {re: 0.0, im: 0.0}
        ];
        
        // 2. Apply J(gamma)
        // J = cos(gamma/2) I + i * sin(gamma/2) X⊗X
        // Since initial state is |00>, J |00> = cos(gamma/2)|00> + i * sin(gamma/2)|11>
        const cos_g = Math.cos(gamma / 2);
        const sin_g = Math.sin(gamma / 2);
        
        psi[0] = { re: cos_g, im: 0.0 };
        psi[3] = { re: 0.0, im: sin_g }; // i * sin(gamma/2)

        // 3. Apply Player 1 Strategy U_1 on qubit 0 (least significant bit)
        // qubit 0 targets swaps between 0-1, and 2-3
        psi = applyQubitStrategy(psi, state.p1Strategy, 0);
        
        // 4. Apply Player 2 Strategy U_2 on qubit 1 (most significant bit)
        // qubit 1 targets swaps between 0-2, and 1-3
        psi = applyQubitStrategy(psi, state.p2Strategy, 1);
        
        // 5. Apply J(gamma)† (De-entangling operator)
        // J† = cos(gamma/2) I - i * sin(gamma/2) X⊗X
        // For each index k, psi_new[k] = cos_g * psi[k] - i * sin_g * psi[k ^ 3]
        let finalPsi = [ {re:0, im:0}, {re:0, im:0}, {re:0, im:0}, {re:0, im:0} ];
        for (let k = 0; k < 4; k++) {
            const target = k ^ 3; // swaps 0-3, 1-2 (flips both bits)
            // Complex term 1: cos_g * psi[k]
            const term1 = { re: cos_g * psi[k].re, im: cos_g * psi[k].im };
            // Complex term 2: -i * sin_g * psi[target]
            // -i * (a + bi) = b - ai
            const term2 = { re: sin_g * psi[target].im, im: -sin_g * psi[target].re };
            
            finalPsi[k] = {
                re: term1.re + term2.re,
                im: term1.im + term2.im
            };
        }
        
        // 6. Calculate state resolution probabilities
        const probs = finalPsi.map(z => z.re ** 2 + z.im ** 2);
        
        // Map probabilities:
        // probs[0] = CC
        // probs[1] = DC (Player 1 defect, Player 2 cooperate)
        // probs[2] = CD (Player 1 cooperate, Player 2 defect)
        // probs[3] = DD
        const p_CC = probs[0];
        const p_DC = probs[1];
        const p_CD = probs[2];
        const p_DD = probs[3];
        
        // 7. Calculate Expected Payoffs
        const payoff1 = 3 * p_CC + 5 * p_DC + 0 * p_CD + 1 * p_DD;
        const payoff2 = 3 * p_CC + 0 * p_DC + 5 * p_CD + 1 * p_DD;
        
        // Update state results
        state.gameResults.probs = [p_CC, p_DC, p_CD, p_DD];
        state.gameResults.payoffs = [payoff1, payoff2];
        
        // Update UI displays
        probCC.textContent = (p_CC * 100).toFixed(0) + "%";
        probDC.textContent = (p_DC * 100).toFixed(0) + "%";
        probCD.textContent = (p_CD * 100).toFixed(0) + "%";
        probDD.textContent = (p_DD * 100).toFixed(0) + "%";
        
        // Highlight active grid cell(s)
        // Remove active class
        [cellCC, cellDC, cellCD, cellDD].forEach(cell => cell.classList.remove("active-cell"));
        
        // Highlight cells with non-zero probability
        if (p_CC > 0.02) cellCC.classList.add("active-cell");
        if (p_DC > 0.02) cellDC.classList.add("active-cell");
        if (p_CD > 0.02) cellCD.classList.add("active-cell");
        if (p_DD > 0.02) cellDD.classList.add("active-cell");
        
        // Update Chart
        gameChart.data.datasets[0].data = [p_CC, p_DC, p_CD, p_DD];
        gameChart.update();
        
        // Update state indicator badge
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
        
        // Log results
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
            // Identity: do nothing
            for (let k = 0; k < 4; k++) nextPsi[k] = { ...psi[k] };
        } else if (strategy === "D") {
            // Bit flip swap along the target qubit
            for (let k = 0; k < 4; k++) {
                let target = k ^ (1 << qubit);
                nextPsi[target] = { ...psi[k] };
            }
        } else if (strategy === "Q") {
            // Quantum rotation strategy Q:
            // U_Q = |0><0| * i + |1><1| * -i
            // Multiplies by i if bit is 0, and by -i if bit is 1
            for (let k = 0; k < 4; k++) {
                let bitVal = (k >> qubit) & 1;
                if (bitVal === 0) {
                    // Multiply by i: re' = -im, im' = re
                    nextPsi[k] = { re: -psi[k].im, im: psi[k].re };
                } else {
                    // Multiply by -i: re' = im, im' = -re
                    nextPsi[k] = { re: psi[k].im, im: -psi[k].re };
                }
            }
        }
        return nextPsi;
    }

    // --- Mode 2 Controls Event Listeners ---
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
        // Trigger a visual mini-flash on the matrix panel to show calculation
        const matrixCard = document.querySelector(".matrix-container").parentElement;
        matrixCard.style.boxShadow = "0 0 30px rgba(0, 242, 254, 0.4)";
        setTimeout(() => {
            matrixCard.style.boxShadow = "";
        }, 300);
        
        logEvent("Executing quantum game circuit...", "info");
        runQuantumGame();
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

    btnExpEP.addEventListener("click", () => runQuestionOrderExperiment('ethics'));
    btnExpPE.addEventListener("click", () => runQuestionOrderExperiment('profit'));

    // --- Initialization ---
    resizeCanvas();
    resetMind("superposition");
});
