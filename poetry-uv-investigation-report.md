# Poetry and uv Compatibility Investigation Report

## Problem Summary

The Cognite SDK Python project has compatibility issues between Poetry and uv due to outdated configuration patterns that don't align with modern Python packaging standards.

## Current State

### Poetry Configuration Issues
The project is using Poetry 2.1.3 with deprecated configuration patterns that generate multiple warnings:

```
Warning: [tool.poetry.name] is deprecated. Use [project.name] instead.
Warning: [tool.poetry.version] is set but 'version' is not in [project.dynamic].
Warning: [tool.poetry.description] is deprecated. Use [project.description] instead.
Warning: [tool.poetry.readme] is set but 'readme' is not in [project.dynamic].
Warning: [tool.poetry.license] is deprecated. Use [project.license] instead.
Warning: [tool.poetry.authors] is deprecated. Use [project.authors] instead.
Warning: [tool.poetry.documentation] is deprecated. Use [project.urls] instead.
Warning: [tool.poetry.extras] is deprecated. Use [project.optional-dependencies] instead.
```

### uv Compatibility Issues
uv (version 0.7.19) cannot process the project because it expects PEP 621 compliant configuration:

```
error: No `project` table found in: `/workspace/pyproject.toml`
```

## Root Cause Analysis

1. **Outdated Poetry Configuration**: The project uses the legacy `[tool.poetry]` format instead of the standardized `[project]` table defined in PEP 621.

2. **Missing PEP 621 Compliance**: Modern Python packaging tools like uv require a `[project]` table for metadata, which this project lacks.

3. **Migration Gap**: The project hasn't been updated to use Poetry's newer features that support both legacy and modern formats.

## Impact

- **Cannot use uv**: The project cannot take advantage of uv's faster dependency resolution and installation
- **Deprecation warnings**: Multiple warnings during Poetry operations indicate future compatibility issues
- **Developer experience**: Contributors may face issues when trying to use modern Python tooling
- **CI/CD concerns**: Future Poetry versions may not support the current configuration

## Solutions

### Option 1: Update Poetry Configuration (Recommended)
Modernize the `pyproject.toml` to include both Poetry and PEP 621 sections:

```toml
[project]
name = "cognite-sdk"
version = "7.76.0"
description = "Cognite Python SDK"
readme = "README.md"
license = {text = "Apache-2.0"}
authors = [
    {name = "Erlend Vollset", email = "erlend.vollset@cognite.com"},
    {name = "Håkon Treider", email = "hakon.treider@cognite.com"},
    {name = "Anders Albert", email = "anders.albert@cognite.com"}
]
requires-python = "^3.10"
dependencies = [
    "requests>=2.27",
    "requests_oauthlib>=1",
    "msal>=1.31",
    "protobuf>=4",
    "packaging>=20",
    "pip>=20.0.0",
    "typing_extensions>=4",
    "tzdata>=2024.1; platform_system == 'Windows' or platform_system == 'Emscripten'",
]

[project.optional-dependencies]
pandas = ["pandas>=2.1"]
numpy = ["numpy>=1.25"]
geo = ["geopandas>=0.14", "shapely>=1.7.0"]
sympy = ["sympy"]
functions = ["pip"]
yaml = ["PyYAML>=6.0"]
pyodide = ["pyodide-http>=0.2.1", "tzdata>=2024.1"]
all = ["numpy>=1.25", "pandas>=2.1", "geopandas>=0.14", "shapely>=1.7.0", "sympy", "pip", "PyYAML>=6.0"]

[project.urls]
Documentation = "https://cognite-sdk-python.readthedocs-hosted.com"

[tool.poetry]
# Keep Poetry sections for backward compatibility during transition
```

### Option 2: Migrate to uv
Use the automated migration tool:

```bash
uvx migrate-to-uv
```

This will:
- Convert Poetry configuration to uv format
- Create `uv.lock` file
- Maintain dependency versions
- Preserve dependency groups

### Option 3: Hybrid Approach
Keep Poetry but ensure uv compatibility by adding minimal PEP 621 sections.

## Recommendations

1. **Immediate**: Add PEP 621 `[project]` table to enable uv compatibility while keeping Poetry
2. **Short-term**: Update CI/CD to suppress Poetry deprecation warnings
3. **Long-term**: Consider migrating to uv for improved performance and modern tooling

## Benefits of Migration

- **Performance**: uv is significantly faster than Poetry for dependency resolution
- **Standards compliance**: Aligns with PEP 621 and modern Python packaging
- **Single binary**: uv is distributed as a single binary, reducing installation complexity
- **Python version management**: uv can install and manage Python versions
- **Future-proofing**: Positions the project for long-term compatibility

## Testing Strategy

Before implementing changes:
1. Test in a branch first
2. Verify all CI/CD pipelines work
3. Ensure all optional dependencies install correctly
4. Validate build process continues to work
5. Test documentation generation

## Related Issues

- Poetry team is working on PEP 621 support improvements
- uv is rapidly adding features to match Poetry's functionality
- Industry trend is moving toward standardized packaging formats

## Migration Tool Issues

Automated migration using `uvx migrate-to-uv --dry-run` fails with:

```
thread 'main' panicked at src/converters/poetry/version.rs:33:45:
called `Result::unwrap()` on an `Err` value: VersionParseError { kind: UnexpectedEnd { version: "0", remaining: ", <0.25.5" } }
```

This indicates the migration tool cannot parse complex version constraints in the current Poetry configuration, specifically the `responses = "^0, <0.25.5"` dependency on line 61 of `pyproject.toml`. The `^0` constraint is unusual and represents "any version starting from 0.0.0" combined with an upper bound.

**Problematic dependency:**
```toml
responses = "^0, <0.25.5"  # Line 61 - causes migration tool crash
```

**Suggested fix:**
```toml
responses = ">=0.1.0, <0.25.5"  # More standard version constraint
```

## Timeline Considerations

- Poetry 2.x already supports PEP 621 format
- Future Poetry versions may deprecate legacy format entirely
- uv ecosystem is mature enough for production use
- Automatic migration tools have limitations with complex configurations
- Manual migration may be required for projects with complex dependency constraints
- This change should be prioritized to avoid technical debt

## Conclusion

The Cognite SDK project faces significant compatibility issues between Poetry and uv due to:

1. **Legacy configuration format** that doesn't support modern tooling
2. **Complex version constraints** that break migration tools
3. **Missing PEP 621 compliance** required by uv

**Immediate action required**: Manual update to add PEP 621 sections while maintaining Poetry compatibility, followed by gradual migration to uv for improved development experience and future-proofing.