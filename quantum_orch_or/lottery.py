"""
lottery.py — A verifiable, commit-reveal quantum lottery.

"Can't be cheated" is really three separate properties, and none of them
comes for free just because a quantum computer is involved:

  1. Unpredictability  — no party (including the organizer) can know or
     steer the outcome in advance.
  2. Verifiability      — anyone holding the public transcript can
     recompute the result themselves, without trusting whoever ran the
     draw.
  3. Non-manipulability — no participant can bias the result by choosing
     *when* to reveal their input once other inputs are visible.

This module gets there with three ingredients:

  - **Commit-reveal** (`make_commitment` / `Participant`): every
    participant locks in a secret behind a public hash *before* the
    draw, so nobody can pick a favorable value after seeing everyone
    else's.
  - **A quantum entropy beacon** (`draw_quantum_entropy`): a superposition
    of qubits measured on a simulator (or real IBM hardware — see
    `main.py --hw-circuit` / the QiskitRuntimeService example in the
    README) contributes entropy no participant supplied and nobody
    can precompute, using the exact same H-then-measure primitive
    already driving the OR collapse in `simulation.py`.
  - **Unbiased, re-computable winner selection** (`_unbiased_index`):
    every public input is folded into one seed with SHA-256, and
    winners are chosen from it via rejection sampling (never modulo
    bias) so the same transcript always reproduces the same winners.

`verify_draw` is the actual cheat-proofing: it recomputes the entire
draw from nothing but the published transcript in a `LotteryResult`,
and returns False if anything — a reveal, the quantum bitstring, the
entry list, or the winners — was tampered with after the fact.

Note on trust boundaries: this makes the *draw* itself trustless and
auditable. It does not, by itself, guarantee that `entries` was an
honest list of who was actually eligible to enter, or that the quantum
beacon was really sourced from a real QPU rather than a simulator that
someone claims is a QPU — those are attestation problems one layer up
(e.g. publishing the IBM job ID and letting anyone look it up), not
randomness problems.
"""

import hashlib
import secrets
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator


# ---------------------------------------------------------------------------
# Commit-reveal
# ---------------------------------------------------------------------------

def make_commitment(secret: bytes) -> str:
    """Hash a participant's secret into a public commitment (SHA-256 hex)."""
    return hashlib.sha256(secret).hexdigest()


def generate_secret() -> bytes:
    """32 bytes of CSPRNG entropy for a participant's commit-reveal secret."""
    return secrets.token_bytes(32)


@dataclass
class Participant:
    """
    A lottery participant. `secret` is only known to the participant
    until reveal time; `commitment` is what gets published up front.
    """
    entry_id: str
    secret: bytes = field(repr=False)

    @property
    def commitment(self) -> str:
        return make_commitment(self.secret)


# ---------------------------------------------------------------------------
# Quantum entropy beacon
# ---------------------------------------------------------------------------

@dataclass
class QuantumBeaconResult:
    num_qubits: int
    bitstring: str                 # measured basis state, e.g. "0110"
    backend_name: str
    job_id: Optional[str] = None   # populated when run on real IBM hardware


def draw_quantum_entropy(num_qubits: int = 16, simulator: Optional[AerSimulator] = None) -> QuantumBeaconResult:
    """
    Puts `num_qubits` qubits into an equal superposition (Hadamard on
    each) and measures them, producing a uniformly random bitstring.
    This is the same H-then-measure primitive already used to sample
    the OR collapse in simulation.py, exposed here as a standalone
    entropy beacon rather than buried in the physics loop.

    Swap `simulator` for a real backend (see the QiskitRuntimeService
    example in the README) to source entropy from actual hardware, and
    record the returned job_id in the public transcript so the
    measurement can be independently looked up against IBM's job
    history — that's what turns "we used a QPU" into something
    verifiable rather than an unfalsifiable claim.
    """
    sim = simulator or AerSimulator()
    qc = QuantumCircuit(num_qubits, num_qubits)
    qc.h(range(num_qubits))
    qc.measure(range(num_qubits), range(num_qubits))

    t_qc = transpile(qc, sim)
    result = sim.run(t_qc, shots=1).result()
    counts = result.get_counts(t_qc)
    bitstring = next(iter(counts))  # single shot -> single outcome

    return QuantumBeaconResult(
        num_qubits=num_qubits,
        bitstring=bitstring,
        backend_name=sim.__class__.__name__,
    )


# ---------------------------------------------------------------------------
# Deterministic, unbiased selection from a combined seed
# ---------------------------------------------------------------------------

def _combine_seed(reveals: Dict[str, bytes], quantum_bitstring: str, entries: Sequence[str]) -> bytes:
    """
    Deterministically folds every public input into one seed:
      - every participant's revealed secret, sorted by entry_id so the
        order they happen to be published in can't be used to bias
        the result
      - the quantum beacon's measured bitstring
      - the exact entry list, so a roster changed after the fact
        changes the seed and fails verification
    """
    hasher = hashlib.sha256()
    for entry_id in sorted(reveals):
        hasher.update(entry_id.encode("utf-8"))
        hasher.update(reveals[entry_id])
    hasher.update(quantum_bitstring.encode("utf-8"))
    hasher.update("|".join(entries).encode("utf-8"))
    return hasher.digest()


def _unbiased_index(seed: bytes, upper: int, salt: int) -> int:
    """
    Rejection-sampled index in [0, upper) derived from `seed`, avoiding
    the small bias a plain `hash(...) % upper` would introduce. `salt`
    lets repeated draws (picking N winners without replacement) derive
    independent-looking indices from the same seed.
    """
    if upper <= 0:
        raise ValueError("upper must be positive")
    num_bytes = max(1, (upper.bit_length() + 7) // 8) + 1  # headroom keeps rejection rate low
    limit = (256 ** num_bytes // upper) * upper
    counter = 0
    while True:
        digest = hashlib.sha256(seed + salt.to_bytes(4, "big") + counter.to_bytes(4, "big")).digest()
        candidate = int.from_bytes(digest[:num_bytes], "big")
        if candidate < limit:
            return candidate % upper
        counter += 1


# ---------------------------------------------------------------------------
# Public result + verification
# ---------------------------------------------------------------------------

@dataclass
class LotteryResult:
    entries: List[str]
    commitments: Dict[str, str]    # published before reveal
    reveals: Dict[str, str]        # hex-encoded secrets, published at reveal
    quantum: QuantumBeaconResult
    seed: str                      # hex digest, published with the result
    winners: List[str]


def run_lottery(participants: List[Participant], num_winners: int = 1,
                 num_qubits: int = 16, simulator: Optional[AerSimulator] = None) -> LotteryResult:
    """
    Runs a full draw: pulls a fresh quantum entropy sample, folds it
    together with every participant's revealed secret and the entry
    list into one seed, and picks `num_winners` distinct entries from
    it via unbiased rejection sampling.

    The organizer publishes the returned `LotteryResult` in full;
    anyone can then call `verify_draw` on it to confirm the winners
    really were derived from the published transcript.
    """
    entries = [p.entry_id for p in participants]
    if len(set(entries)) != len(entries):
        raise ValueError("duplicate entry_id in participant list")
    if not (1 <= num_winners <= len(entries)):
        raise ValueError("num_winners must be between 1 and the number of entries")

    commitments = {p.entry_id: p.commitment for p in participants}
    reveals_bytes = {p.entry_id: p.secret for p in participants}

    quantum = draw_quantum_entropy(num_qubits=num_qubits, simulator=simulator)
    seed = _combine_seed(reveals_bytes, quantum.bitstring, entries)

    pool = list(entries)
    winners = []
    for i in range(num_winners):
        idx = _unbiased_index(seed, len(pool), salt=i)
        winners.append(pool.pop(idx))

    return LotteryResult(
        entries=entries,
        commitments=commitments,
        reveals={k: v.hex() for k, v in reveals_bytes.items()},
        quantum=quantum,
        seed=seed.hex(),
        winners=winners,
    )


def verify_draw(result: LotteryResult) -> bool:
    """
    Recomputes the entire draw from nothing but the public transcript
    in `result` and checks it reproduces the published winners. This
    is the actual cheat-proofing: anyone holding the commitments,
    reveals, quantum bitstring, and entry list can run this themselves
    — they don't need to trust whoever called `run_lottery`.
    """
    # 1. Every reveal must match its published commitment.
    for entry_id, reveal_hex in result.reveals.items():
        if entry_id not in result.commitments:
            return False
        if make_commitment(bytes.fromhex(reveal_hex)) != result.commitments[entry_id]:
            return False

    # 2. Recompute the seed from the public transcript.
    reveals_bytes = {k: bytes.fromhex(v) for k, v in result.reveals.items()}
    seed = _combine_seed(reveals_bytes, result.quantum.bitstring, result.entries)
    if seed.hex() != result.seed:
        return False

    # 3. Recompute winner selection and compare.
    pool = list(result.entries)
    recomputed_winners = []
    for i in range(len(result.winners)):
        idx = _unbiased_index(seed, len(pool), salt=i)
        recomputed_winners.append(pool.pop(idx))

    return recomputed_winners == result.winners
