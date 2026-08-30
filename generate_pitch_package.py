"""
generate_pitch_package.py — Exporter for Web3 VC Pitch Deck & Uniswap Grant Proposal.
"""

import os
import shutil

def export_pitch_package(output_dir="pitch_package"):
    """Copy the pitch and grant documents to an explicit local directory."""
    print("==================================================")
    print("  EXPORTING WEB3 QUANTUM AI PITCH & GRANT PACKAGE  ")
    print("==================================================")

    pitch_src = "WEB3_QUANTUM_AI_PROTOCOL_PITCH.md"
    grant_src = "uniswap_grant_proposal.md"

    if not os.path.exists(pitch_src) or not os.path.exists(grant_src):
        raise FileNotFoundError("Pitch or grant proposal file missing.")

    os.makedirs(output_dir, exist_ok=True)
    shutil.copy(pitch_src, os.path.join(output_dir, pitch_src))
    shutil.copy(grant_src, os.path.join(output_dir, grant_src))

    print(f"📦 Copied {pitch_src} to {output_dir}!")
    print(f"📦 Copied {grant_src} to {output_dir}!")

    return True

if __name__ == "__main__":
    export_pitch_package()
