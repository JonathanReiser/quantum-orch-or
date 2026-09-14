"""
generate_pitch_package.py — Exporter for Web3 VC Pitch Deck & Uniswap Grant Proposal.
"""

import os
import shutil

def export_pitch_package(output_dir=None):
    print("==================================================")
    print("  EXPORTING WEB3 QUANTUM AI PITCH & GRANT PACKAGE  ")
    print("==================================================")

    pitch_src = "archive/historical-publications/WEB3_QUANTUM_AI_PROTOCOL_PITCH.md"
    grant_src = "archive/historical-publications/uniswap_grant_proposal.md"

    if not os.path.exists(pitch_src) or not os.path.exists(grant_src):
        raise FileNotFoundError("Pitch or grant proposal file missing.")

    destination = output_dir or os.path.expanduser("~/Desktop")
    os.makedirs(destination, exist_ok=True)
    shutil.copy(pitch_src, os.path.join(destination, os.path.basename(pitch_src)))
    shutil.copy(grant_src, os.path.join(destination, os.path.basename(grant_src)))

    print(f"Copied archived pitch material to {destination}")

    return True

if __name__ == "__main__":
    export_pitch_package()
