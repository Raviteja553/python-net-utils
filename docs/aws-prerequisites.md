# AWS Infrastructure Guardrails & Prerequisites

## 1. Cost Control & Budget Alerts
- **Monthly Budget Ceiling:** $10.00 USD (or $0.00 zero-spend alert).
- **Notification Trigger:** Automated email alert configured at 80% and 100% threshold utilization.
- **Account Identity:** Personal account with root MFA enabled and non-root admin IAM identity.

## 2. Mandatory Tagging Standard
All deployed AWS resources (EC2, VPCs, S3, IAM roles, security groups) MUST include the following three resource tags[cite: 4]:

| Tag Key   | Allowed Values / Format          | Description                                  |
|-----------|----------------------------------|----------------------------------------------|
| `project` | `cloud-lab`, `python-net-utils`  | Identifies the associated lab/project[cite: 4].     |
| `owner`   | `<raviteja>`                     | Identifies the creator of the resource[cite: 4].    |
| `ttl`     | `2h`, `4h`, `session`            | Maximum allowed lifespan before cleanup[cite: 4].  |

*Example AWS CLI / Terraform Tag Specification:*
```hcl
default_tags {
  tags = {
    project = "cloud-lab"
    owner   = "raviteja"
    ttl     = "session"
  }
}