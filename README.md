# TaskqourAI

## Dependency Management

`pyproject.toml` and `uv.lock` are the dependency sources of truth.
`requirements.txt` is generated for compatibility and must not be edited manually.

Regenerate it after updating the lock file:

```powershell
uv export --format requirements-txt > requirements.txt
```
