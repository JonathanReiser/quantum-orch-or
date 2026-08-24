#!/usr/bin/env python3
"""
lottery_demo.py — End-to-end demo of quantum_orch_or/lottery.py.

Walks through a full commit-reveal + quantum-beacon draw with a handful
of entrants, publishes the result, verifies it independently, and then
shows verification catching two kinds of tampering (a swapped winner and
a forged reveal). Run it with:

    python3 lottery_demo.py
"""
import json

from quantum_orch_or.lottery import (
    Participant,
    generate_secret,
    run_lottery,
    verify_draw,
)


def main():
    entrant_names = ["alice", "bob", "carol", "dave", "erin"]

    # --- Commit phase -------------------------------------------------
    # Each participant generates a private secret and publishes only its
    # hash (the commitment) before anyone knows the quantum bitstring or
    # anyone else's secret.
    participants = [Participant(entry_id=name, secret=generate_secret()) for name in entrant_names]

    print("=" * 60)
    print("PHASE 1: Commitments published (secrets still private)")
    print("=" * 60)
    for p in participants:
        print(f"  {p.entry_id:8s} commitment = {p.commitment}")

    # --- Draw phase -----------------------------------------------------
    # Reveals + a fresh quantum entropy sample are combined into one seed.
    print("\n" + "=" * 60)
    print("PHASE 2: Reveals collected, quantum beacon sampled, draw run")
    print("=" * 60)
    result = run_lottery(participants, num_winners=2)

    print(f"  Quantum beacon bitstring : {result.quantum.bitstring} "
          f"({result.quantum.num_qubits} qubits, {result.quantum.backend_name})")
    print(f"  Combined seed (SHA-256)  : {result.seed}")
    print(f"  Winners                  : {result.winners}")

    # --- Publication ------------------------------------------------
    # This whole payload is what gets published; verification only needs it.
    transcript = {
        "entries": result.entries,
        "commitments": result.commitments,
        "reveals": result.reveals,
        "quantum": {
            "num_qubits": result.quantum.num_qubits,
            "bitstring": result.quantum.bitstring,
            "backend_name": result.quantum.backend_name,
            "job_id": result.quantum.job_id,
        },
        "seed": result.seed,
        "winners": result.winners,
    }
    print("\n" + "=" * 60)
    print("PHASE 3: Published transcript (this is all a verifier needs)")
    print("=" * 60)
    print(json.dumps(transcript, indent=2))

    # --- Independent verification ------------------------------------
    print("\n" + "=" * 60)
    print("PHASE 4: Independent verification")
    print("=" * 60)
    print(f"  verify_draw(result) -> {verify_draw(result)}  (expected: True)")

    # --- Tamper detection ----------------------------------------------
    print("\n" + "=" * 60)
    print("PHASE 5: Verification catches tampering")
    print("=" * 60)

    import copy

    swapped = copy.deepcopy(result)
    non_winner = next(e for e in swapped.entries if e not in swapped.winners)
    swapped.winners[0] = non_winner
    print(f"  Swapped announced winner to '{non_winner}':")
    print(f"    verify_draw(swapped) -> {verify_draw(swapped)}  (expected: False)")

    forged = copy.deepcopy(result)
    victim = forged.entries[0]
    forged.reveals[victim] = generate_secret().hex()  # forged reveal, doesn't match commitment
    print(f"  Forged reveal for '{victim}' (doesn't hash to their commitment):")
    print(f"    verify_draw(forged) -> {verify_draw(forged)}  (expected: False)")


if __name__ == "__main__":
    main()
