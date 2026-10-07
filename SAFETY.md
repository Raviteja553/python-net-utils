# Repository Safety & Compliance Guidelines

## 1. Absolute Prohibitions
- **No Credentials or Secrets:** Never commit passwords, API keys, tokens, SSH private keys, or certificates.
- **No Employer/Workplace Data:** Do not include internal hostnames, proprietary IP addresses, internal domain names, network diagrams, or employer-owned documentation.
- **No Real Infrastructure Artifacts:** Screenshots, logs, or configs must be strictly sanitised or generated in isolated lab environments.

## 2. Lab-Only & Demonstration Standards
- Use RFC 1918 private address space for lab examples (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`).
- Use RFC 5737 documentation IP ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`).
- Use generic placeholders (`example.com`, `lab-router-01`) for all configuration snippets.

## 3. Automated Verification
- Secret detection hooks must pass locally prior to merging pull requests into the `master` branch.
