import pytest

from q_ai_governance.experiment_lab import list_experiments, run_experiment


def test_experiment_catalogue_has_runnable_and_external_entries():
    records = {record["experiment_id"]: record for record in list_experiments()}

    assert records["snapshot-temporal-baseline"]["status"] == "runnable"
    assert records["dao-vote-sequences"]["status"] == "external companion"
    assert "baseline" in records["collective-valuation"]


def test_snapshot_experiment_uses_real_dataset():
    result = run_experiment(
        "snapshot-temporal-baseline", data_path="data/snapshot_dao_dataset.json"
    )

    assert result["split"]["n_total"] == 905
    assert "constant_train_median" in result["results"]


def test_external_experiment_explains_where_to_run():
    with pytest.raises(ValueError, match="dao-governance-research"):
        run_experiment("dao-vote-sequences")
