# tests/test_rbac.py
import pytest
from src.access.rbac import RBACEnforcer

class TestRBACEnforcement:
    """Test Casbin RBAC enforcement."""

    @pytest.fixture
    def enforcer(self):
        return RBACEnforcer("src/access/model.conf", "src/access/policy.csv")

    def test_admin_can_read_patient_data(self, enforcer):
        """Admin has read permission on patient_data."""
        assert enforcer.enforce("user_alice", "patient_data", "read")

    def test_admin_can_delete_patient_data(self, enforcer):
        """Admin has delete permission on patient_data."""
        assert enforcer.enforce("user_alice", "patient_data", "delete")

    def test_ml_engineer_can_read_training_data(self, enforcer):
        """ML Engineer has read permission on training_data."""
        assert enforcer.enforce("user_bob", "training_data", "read")

    def test_ml_engineer_cannot_delete_patient_data(self, enforcer):
        """ML Engineer cannot delete patient_data."""
        assert not enforcer.enforce("user_bob", "patient_data", "delete")

    def test_data_analyst_can_read_metrics(self, enforcer):
        """Data Analyst can read aggregated_metrics."""
        assert enforcer.enforce("user_carol", "aggregated_metrics", "read")

    def test_data_analyst_cannot_write_model_artifacts(self, enforcer):
        """Data Analyst cannot write model_artifacts."""
        assert not enforcer.enforce("user_carol", "model_artifacts", "write")

    def test_intern_limited_to_sandbox(self, enforcer):
        """Intern only has sandbox_data access."""
        assert enforcer.enforce("user_dave", "sandbox_data", "read")
        assert not enforcer.enforce("user_dave", "patient_data", "read")
