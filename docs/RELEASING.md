# Releasing

Shard is published to PyPI as [`shrd`](https://pypi.org/project/shrd/). The Python import name is `shard`.

## Prerequisites

- PyPI trusted publishing configured for this repository (`workflow.yml`)
- All changes merged to `main`
- Version bumped in `pyproject.toml` and `shard/__init__.py`
- `CHANGELOG.md` updated

## Release steps

1. Ensure CI is green on `main`.
2. Commit version and changelog updates.
3. Tag the release:

   ```bash
   git tag v0.3.0
   git push origin v0.3.0
   ```

4. GitHub Actions workflow `.github/workflows/workflow.yml` builds and publishes to PyPI.
5. Verify:

   ```bash
   pip install shrd==0.3.0
   python -c "import shard; print(shard.__version__)"
   ```

## Manual publish (fallback)

```bash
pip install build twine
python -m build
twine check dist/*
twine upload dist/*
```

Use a PyPI API token if trusted publishing is unavailable.
