# Poetry to UV Migration Analysis for cognite-sdk-python

## Executive Summary

The migration from Poetry to uv for the cognite-sdk-python project is both feasible and beneficial. uv offers significantly faster dependency resolution, better alignment with Python packaging standards, and simpler environment management. This document outlines the current state, migration path, and benefits of transitioning from Poetry to uv.

## Current Poetry Usage Analysis

### Files and Locations Using Poetry

Based on my analysis, Poetry is currently used in the following locations:

**Core Configuration Files:**
- `pyproject.toml` - Main Poetry configuration with dependencies and metadata
- `poetry.lock` - Lock file with exact dependency versions (172KB, 2669 lines)

**Documentation and Setup:**
- `README.md` - Installation instructions using Poetry
- `CONTRIBUTING.md` - Development setup instructions
- `docs/source/extensions_and_optional_dependencies.rst` - Usage examples

**GitHub Workflows (CI/CD):**
- `.github/workflows/build.yml` - Main build workflow
- `.github/workflows/release.yaml` - Release workflow  
- `.github/workflows/verify-jupyter.yml` - Jupyter verification
- `.github/workflows/verify-streamlit.yml` - Streamlit verification
- `.github/actions/setup/action.yml` - Reusable setup action

**Development Environment:**
- `.pre-commit-config.yaml` - Pre-commit hooks using Poetry
- `.devcontainer/` - Development container configuration
- `.readthedocs.yaml` - Documentation building

**Configuration Files:**
- `renovate.json` - Dependency update automation

### Current Poetry Configuration

The project currently uses:
- Poetry for dependency management
- poetry-core as build backend
- Development dependencies in separate groups
- Optional dependencies (extras) for pandas, numpy, geo, sympy, functions, yaml, pyodide

## Migration Strategy

### Recommended Approach

Based on current best practices, I recommend using the `migrate-to-uv` tool which provides the most comprehensive and reliable migration path:

```bash
# Basic migration
uvx migrate-to-uv

# With options for this project
uvx migrate-to-uv --dependency-groups-strategy set-default-groups
```

### Alternative Migration Methods

If the automated tool doesn't meet all requirements, manual migration using PDM import is possible:

```bash
# Use PDM to convert Poetry format to PEP 621
uvx pdm import pyproject.toml

# Manual cleanup required after PDM import
```

## Step-by-Step Migration Plan

### Phase 1: Preparation
1. **Backup current configuration**
   ```bash
   cp pyproject.toml pyproject.toml.backup
   cp poetry.lock poetry.lock.backup
   ```

2. **Install uv** (if not already available)
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Test current Poetry setup**
   ```bash
   poetry install
   poetry run pytest  # Verify current functionality
   ```

### Phase 2: Core Migration
1. **Run migration tool**
   ```bash
   uvx migrate-to-uv --dependency-groups-strategy set-default-groups --dry-run
   # Review changes, then run without --dry-run
   uvx migrate-to-uv --dependency-groups-strategy set-default-groups
   ```

2. **Verify pyproject.toml conversion**
   - Check that all dependencies are correctly converted
   - Verify optional dependencies are preserved
   - Ensure build system is properly configured

3. **Test uv functionality**
   ```bash
   uv sync
   uv run pytest
   ```

### Phase 3: Update Supporting Files

1. **Update GitHub Workflows**
   - Replace Poetry installation and caching with uv equivalents
   - Update setup action to use uv
   - Modify build commands to use `uv build` instead of `poetry build`

2. **Update pre-commit configuration**
   - Replace Poetry hooks with uv equivalents
   - Use uv pre-commit hooks for dependency management

3. **Update documentation**
   - Modify README.md installation instructions
   - Update CONTRIBUTING.md development setup
   - Update documentation build configuration

4. **Update development environment**
   - Modify `.devcontainer/` configuration
   - Update `.readthedocs.yaml` for documentation building

### Phase 4: Cleanup and Validation
1. **Remove Poetry artifacts**
   ```bash
   rm poetry.lock
   # Remove Poetry configuration from pyproject.toml (if using migrate-to-uv tool)
   ```

2. **Update dependency automation**
   - Modify `renovate.json` to work with uv
   - Test automated dependency updates

3. **Comprehensive testing**
   - Run full test suite with uv
   - Test documentation building
   - Validate CI/CD workflows

## Files Requiring Updates

### High Priority (Critical for functionality)
1. `pyproject.toml` - Core dependency configuration
2. `.github/actions/setup/action.yml` - CI/CD setup action
3. `.github/workflows/*.yml` - All workflow files
4. `README.md` - User-facing installation instructions
5. `CONTRIBUTING.md` - Developer setup instructions

### Medium Priority (User experience)
1. `.pre-commit-config.yaml` - Development workflow
2. `.readthedocs.yaml` - Documentation building
3. `docs/source/extensions_and_optional_dependencies.rst` - Documentation
4. `.devcontainer/` - Development environment

### Low Priority (Automation)
1. `renovate.json` - Dependency updates
2. Version check scripts in `scripts/custom_checks/`

## Expected Benefits

### Performance Improvements
- **Dependency resolution**: 10-100x faster than Poetry
- **Environment creation**: Significantly faster virtual environment setup
- **CI/CD**: Reduced workflow execution time

### Maintenance Benefits
- **Standards compliance**: Better alignment with PEP 621 and modern Python packaging
- **Tooling ecosystem**: Growing ecosystem support for uv
- **Simplified configuration**: Cleaner, more standardized configuration format

### Developer Experience
- **Faster feedback**: Quicker dependency changes and testing
- **Better tooling**: Integration with modern Python development tools
- **Future-proofing**: Investment in the direction Python packaging is moving

## Migration Risks and Mitigation

### Potential Risks
1. **Dependency resolution differences**: uv might resolve dependencies differently than Poetry
2. **Build compatibility**: Potential issues with package building
3. **CI/CD disruption**: Temporary workflow failures during migration
4. **Developer workflow**: Team needs to learn new commands

### Mitigation Strategies
1. **Thorough testing**: Complete test suite execution before and after migration
2. **Gradual rollout**: Use feature branches and staged deployment
3. **Documentation**: Update all developer documentation simultaneously
4. **Rollback plan**: Keep Poetry configuration as backup during initial phase

## Post-Migration Maintenance

### New Developer Workflow
```bash
# Instead of: poetry install
uv sync

# Instead of: poetry run pytest
uv run pytest

# Instead of: poetry add package
uv add package

# Instead of: poetry add --group dev package
uv add --dev package
```

### CI/CD Changes
- Faster builds due to uv's performance
- Simplified caching strategies
- Better reproducibility with lock files

## Conclusion

The migration from Poetry to uv is recommended for the cognite-sdk-python project. The benefits significantly outweigh the migration costs, and the process can be completed with minimal disruption using modern migration tools. The faster dependency resolution and better standards compliance will improve both developer experience and CI/CD performance.

## Next Steps

1. **Schedule migration window**: Plan for a focused effort to complete migration
2. **Team communication**: Inform all developers about the upcoming change
3. **Create migration branch**: Use a feature branch for the migration work
4. **Execute migration**: Follow the step-by-step plan outlined above
5. **Team training**: Ensure all developers understand the new workflow

The migration should be straightforward given the maturity of the available migration tools and the comprehensive documentation in the uv ecosystem.