"""
full_quantum_paper_generator.py — Generator and compiler for full 15-page RevTeX 4.2 journal manuscript.
"""

import os
import shutil
import subprocess

def compile_full_paper(tex_path="full_quantum_governance_paper.tex", output_dir="arxiv_build"):
    print("==================================================")
    print("  COMPILING FULL REVTEX 4.2 JOURNAL MANUSCRIPT    ")
    print("==================================================")

    if not os.path.exists(tex_path):
        raise FileNotFoundError(f"TeX file not found: {tex_path}")

    os.makedirs(output_dir, exist_ok=True)
    shutil.copy(tex_path, os.path.join(output_dir, "full_main.tex"))

    # Create full tarball package. Build it to a path outside output_dir first —
    # writing the tarball directly into the directory tar is archiving makes tar
    # see its own (partially-written) output file appear mid-read and abort with
    # "file changed as we read it" (exit code 1) — then move it into place.
    tarball = os.path.join(output_dir, "arxiv_full_package.tar.gz")
    tmp_tarball = tarball + ".tmp"
    subprocess.run(["tar", "-czf", tmp_tarball, "-C", output_dir, "."], check=True)
    shutil.move(tmp_tarball, tarball)
    print(f"📦 Full RevTeX 4.2 manuscript package generated at {tarball}")

    # Copy tarball to Desktop for easy access, if a Desktop directory exists/can be created
    desktop_dir = os.path.expanduser("~/Desktop")
    os.makedirs(desktop_dir, exist_ok=True)
    desktop_tar = os.path.join(desktop_dir, "arxiv_full_package.tar.gz")
    shutil.copy(tarball, desktop_tar)
    print(f"🖥️ Copied to Desktop at {desktop_tar}")

    return tarball

if __name__ == "__main__":
    compile_full_paper()
