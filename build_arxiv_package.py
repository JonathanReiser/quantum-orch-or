"""
build_arxiv_package.py — Re-compiles fresh arXiv submission bundles (arxiv_submission.tar.gz and arxiv_full_package.tar.gz).
"""

import os
import tarfile
import shutil

def build_arxiv_bundles():
    bundle_files = [
        "full_quantum_governance_paper.tex",
        "references.bib"
    ]

    # Include optional BST/CLS if present
    for extra in ["apsrev4-2.bst", "revtex4-2.cls"]:
        if os.path.exists(extra):
            bundle_files.append(extra)

    # Include math images if present
    if os.path.exists("math_images"):
        for img in os.listdir("math_images"):
            if img.endswith(".png"):
                bundle_files.append(os.path.join("math_images", img))

    for tar_name in ["arxiv_submission.tar.gz", "arxiv_full_package.tar.gz"]:
        with tarfile.open(tar_name, "w:gz") as tar:
            for f in bundle_files:
                if os.path.exists(f):
                    tar.add(f)
        print(f"📦 Successfully created fresh arXiv bundle: {tar_name}")

        desktop_path = os.path.expanduser(f"~/Desktop/{tar_name}")
        shutil.copy(tar_name, desktop_path)
        print(f"🖥️ Copied {tar_name} to Mac Desktop: {desktop_path}")

if __name__ == "__main__":
    build_arxiv_bundles()
