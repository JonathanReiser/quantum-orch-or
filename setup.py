from setuptools import setup, find_packages

setup(
    name="q-ai-governance",
    version="1.0.0",
    description="Quantum-Cognitive AI (Q-AI) Policy Agent & Real DAO Governance Decision Engine",
    author="Jonathan Reiser",
    packages=find_packages(),
    install_requires=[
        "qiskit>=1.0",
        "qiskit-aer>=0.14",
        "numpy>=1.22",
        "matplotlib>=3.5",
        "scipy>=1.8"
    ],
    entry_points={
        "console_scripts": [
            "q-ai-gov=q_ai_governance.cli:main",
        ],
    },
    python_requires=">=3.9",
)
