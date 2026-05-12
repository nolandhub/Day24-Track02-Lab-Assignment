# ABOUTME: OPA Rego policy for medical data access control
# ABOUTME: Complements Casbin RBAC with fine-grained attribute-based rules

package medviet.data_access

import future.keywords.if
import future.keywords.in

# Default: deny all access
default allow := false

# Rule 1: Admin can perform any action
allow if {
    input.user.role == "admin"
}

# Rule 2: ML Engineer can read training data and model artifacts
allow if {
    input.user.role == "ml_engineer"
    input.resource in {"training_data", "model_artifacts"}
    input.action in {"read", "write"}
}

# Rule 3: ML Engineer cannot delete production data
deny if {
    input.user.role == "ml_engineer"
    input.resource == "patient_data"
    input.action == "delete"
}

# Rule 4: Data Analyst can read aggregated metrics and write reports
allow if {
    input.user.role == "data_analyst"
    input.resource in {"aggregated_metrics", "reports"}
    input.action in {"read", "write"}
}

# Rule 5: Data Analyst cannot read raw PII
deny if {
    input.user.role == "data_analyst"
    input.resource == "patient_data"
    input.action == "read"
}

# Rule 6: Intern restricted to sandbox environment
allow if {
    input.user.role == "intern"
    input.resource == "sandbox_data"
    input.action in {"read", "write"}
}

# Rule 7: Intern cannot access production
deny if {
    input.user.role == "intern"
    input.resource in {"patient_data", "training_data", "model_artifacts", "production_data"}
}

# Rule 8: No data export outside Vietnam
deny if {
    input.data_classification == "restricted"
    input.destination_country != "VN"
}

# Rule 9: Audit logging required for sensitive operations
audit_required if {
    input.resource == "patient_data"
    input.action in {"delete", "export"}
}
