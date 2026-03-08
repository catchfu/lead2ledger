# CRM + SAP Production Scaffold

## Structure
- `apps/api`: FastAPI service
- `apps/web`: Web UI placeholder
- `infra`: Docker Compose and env templates
- `docs`: Product and engineering documentation
- `tests`: API and integration test placeholders

## Quick Start
```bash
cp infra/.env.example infra/.env
# install python deps for API, then:
python apps/api/main.py
```
