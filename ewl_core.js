/* Pure EWL probability engine shared by the participant pilot and Node checks. */
(function exposeEWLCore(root, factory) {
    const api = factory();
    if (typeof module !== "undefined" && module.exports) module.exports = api;
    if (root) root.EWLCore = api;
}(typeof globalThis !== "undefined" ? globalThis : this, function createEWLCore() {
    "use strict";

    const OUTCOMES = ["CC", "CD", "DC", "DD"];
    const STRATEGIES = {
        C: [[[1, 0], [0, 0]], [[0, 0], [1, 0]]],
        D: [[[0, 0], [1, 0]], [[1, 0], [0, 0]]],
        Q: [[[0, 1], [0, 0]], [[0, 0], [0, -1]]]
    };

    function add(a, b) {
        return [a[0] + b[0], a[1] + b[1]];
    }

    function multiply(a, b) {
        return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
    }

    function scale(value, scalar) {
        return [value[0] * scalar, value[1] * scalar];
    }

    function magnitudeSquared(value) {
        return value[0] * value[0] + value[1] * value[1];
    }

    function assertStrategy(strategy) {
        if (!Object.prototype.hasOwnProperty.call(STRATEGIES, strategy)) {
            throw new Error("Strategy must be C, D, or Q.");
        }
    }

    function distribution(playerOne, playerTwo, gamma) {
        assertStrategy(playerOne);
        assertStrategy(playerTwo);
        if (!Number.isFinite(gamma) || gamma < 0 || gamma > Math.PI / 2) {
            throw new Error("Gamma must be between 0 and pi/2.");
        }

        const cosine = Math.cos(gamma / 2);
        const sine = Math.sin(gamma / 2);
        const initial = [[cosine, 0], [0, 0], [0, 0], [0, sine]];
        const afterStrategies = [[0, 0], [0, 0], [0, 0], [0, 0]];

        for (let outTwo = 0; outTwo < 2; outTwo += 1) {
            for (let outOne = 0; outOne < 2; outOne += 1) {
                const outIndex = outTwo * 2 + outOne;
                for (let inTwo = 0; inTwo < 2; inTwo += 1) {
                    for (let inOne = 0; inOne < 2; inOne += 1) {
                        const inIndex = inTwo * 2 + inOne;
                        const local = multiply(
                            STRATEGIES[playerTwo][outTwo][inTwo],
                            STRATEGIES[playerOne][outOne][inOne]
                        );
                        afterStrategies[outIndex] = add(
                            afterStrategies[outIndex],
                            multiply(local, initial[inIndex])
                        );
                    }
                }
            }
        }

        // J dagger = cos(gamma/2) I - i sin(gamma/2) X tensor X.
        const finalState = afterStrategies.map((value, index) => {
            const flipped = afterStrategies[index ^ 3];
            const minusITimesFlipped = [flipped[1], -flipped[0]];
            return add(scale(value, cosine), scale(minusITimesFlipped, sine));
        });
        const basis = finalState.map(magnitudeSquared);
        const publicOrder = [basis[0], basis[2], basis[1], basis[3]];
        const total = publicOrder.reduce((sum, probability) => sum + probability, 0);
        const result = {};
        OUTCOMES.forEach((outcome, index) => {
            const normalized = publicOrder[index] / total;
            result[outcome] = Math.abs(normalized) < 1e-12 ? 0 : normalized;
        });
        return result;
    }

    function mulberry32(seed) {
        let value = seed >>> 0;
        return function nextRandom() {
            value += 0x6D2B79F5;
            let output = value;
            output = Math.imul(output ^ (output >>> 15), output | 1);
            output ^= output + Math.imul(output ^ (output >>> 7), output | 61);
            return ((output ^ (output >>> 14)) >>> 0) / 4294967296;
        };
    }

    function sample(probabilities, randomValue) {
        let cumulative = 0;
        for (const outcome of OUTCOMES) {
            cumulative += probabilities[outcome];
            if (randomValue < cumulative + 1e-12) return outcome;
        }
        return "DD";
    }

    return { OUTCOMES, distribution, mulberry32, sample };
}));
