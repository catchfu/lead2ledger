# Test Strategy

## Test Layers
- Unit: domain logic, mapping, validators
- Integration: SAP connector contract tests
- E2E: lead -> quote -> order -> invoice lifecycle
- Non-functional: performance, resilience, security

## Quality Gates
- Unit coverage >= 80% for domain services
- Zero critical vulnerabilities
- Sync retry + DLQ scenarios validated
- Smoke E2E must pass before release
