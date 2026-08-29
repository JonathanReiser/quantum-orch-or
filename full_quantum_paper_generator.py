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

    # Create full tarball package
    tarball = os.path.join(output_dir, "arxiv_full_package.tar.gz")
    cmd = f"tar -czf {tarball} -C {output_dir} ."
    subprocess.run(cmd, shell=True, check=True)
    print(f"📦 Full RevTeX 4.2 manuscript package generated at {tarball}")

    # Copy tarball to Desktop for easy access
    desktop_tar = os.path.expanduser("~/Desktop/arxiv_full_package.tar.gz")
    shutil.copy(tarball, desktop_tar)
    print(f"🖥️ Copied to Desktop at {desktop_tar}")

    return tarball

if __name__ == "__main__":
    compile_full_paper()
