"""
q-ai-governance: Quantum-Cognitive AI Policy Agent & Governance Engine
"""

try:
    from q_ai_governance.quantum_agent import QuantumOrchORAgent, QuantumPrisonerDilemmaEnv
    from q_ai_governance.dao_budget_allocator import DAOBudgetAllocator, Proposal
    from q_ai_governance.benchmark_real_dao_data import RealDAOBenchmarkRunner
    from q_ai_governance.quantum_economics import QuantumMarketSentimentModel, QuantumFinancialOrderEffect, QuantumLiquidityContagion
    from q_ai_governance.q_ai_bot import QAIGovernanceBot
    from quantum_orch_or.open_quantum_system import LindbladMasterEquationSolver
except ImportError:
    from quantum_agent import QuantumOrchORAgent, QuantumPrisonerDilemmaEnv
    from dao_budget_allocator import DAOBudgetAllocator, Proposal
    from benchmark_real_dao_data import RealDAOBenchmarkRunner
    from quantum_economics import QuantumMarketSentimentModel, QuantumFinancialOrderEffect, QuantumLiquidityContagion
    from q_ai_bot import QAIGovernanceBot
    from quantum_orch_or.open_quantum_system import LindbladMasterEquationSolver

__version__ = "1.0.0"
__all__ = [
    "QuantumOrchORAgent",
    "QuantumPrisonerDilemmaEnv",
    "DAOBudgetAllocator",
    "Proposal",
    "RealDAOBenchmarkRunner",
    "QuantumMarketSentimentModel",
    "QuantumFinancialOrderEffect",
    "QuantumLiquidityContagion",
    "QAIGovernanceBot",
    "LindbladMasterEquationSolver"
]
