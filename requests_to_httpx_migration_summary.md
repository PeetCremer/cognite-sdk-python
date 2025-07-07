# Requests to HTTPX Migration Summary

## Overview
This document outlines the migration of the Cognite Python SDK from using the `requests` library to `httpx` for HTTP operations. This migration aims to improve performance, provide better async support, and leverage modern HTTP features.

## Current State Analysis

### Key Files Using Requests
1. **Core HTTP Client**: `cognite/client/_http_client.py`
   - Main session management
   - Exception handling and retries
   - Connection pooling configuration

2. **API Client**: `cognite/client/_api_client.py` 
   - Request/response processing
   - Header management using `requests.utils.default_headers()`
   - CaseInsensitiveDict usage

3. **Dependencies**: `pyproject.toml`
   - `requests = "^2.27"`
   - `requests_oauthlib = "^1"`

4. **Exception Handling**:
   - Maps requests exceptions to Cognite custom exceptions
   - Handles timeout, connection, and JSON decode errors

5. **Testing**:
   - Uses `responses` library for HTTP mocking
   - Multiple test files import requests types

### Requests Features Currently Used
- Session management with connection pooling
- HTTP adapters for connection configuration
- Exception hierarchy (ReadTimeout, ConnectionError, etc.)
- Header utilities (default_headers, CaseInsensitiveDict)
- JSON decoding error handling
- Cookie policy management
- SSL/TLS configuration
- Proxy support
- Request streaming

## Migration Plan

### Phase 1: Dependencies and Core Infrastructure
- [ ] Update `pyproject.toml` dependencies
- [ ] Replace `requests` imports with `httpx` equivalents
- [ ] Update session creation and configuration
- [ ] Map exception handling from requests to httpx

### Phase 2: HTTP Client Implementation
- [ ] Migrate `get_global_requests_session()` to httpx client
- [ ] Update `HTTPClient` class to use httpx
- [ ] Handle differences in timeout and retry configuration
- [ ] Ensure connection pooling works correctly

### Phase 3: API Client Updates
- [ ] Update header management in `_api_client.py`
- [ ] Replace `requests.utils.default_headers()` usage
- [ ] Handle response object differences
- [ ] Update JSON handling and error processing

### Phase 4: Authentication and OAuth
- [ ] Migrate `requests_oauthlib` to `httpx_oauth` or equivalent
- [ ] Ensure OAuth flows continue to work
- [ ] Test token refresh mechanisms

### Phase 5: Testing Infrastructure
- [ ] Replace `responses` with `httpx` compatible mocking
- [ ] Update test imports and assertions
- [ ] Ensure test coverage remains complete

### Phase 6: Special Cases
- [ ] Handle Pyodide browser compatibility
- [ ] Update any streaming request handling
- [ ] Verify proxy and SSL configuration works

## Key Differences Between Requests and HTTPX

### API Differences
| Requests | HTTPX | Notes |
|----------|-------|-------|
| `requests.Session()` | `httpx.Client()` | Different class name |
| `session.request()` | `client.request()` | Same method signature |
| `requests.utils.default_headers()` | Custom implementation needed | HTTPX doesn't provide this utility |
| `requests.structures.CaseInsensitiveDict` | `httpx.Headers` | HTTPX headers are case-insensitive by default |
| `requests.exceptions.*` | `httpx.*Error` | Different exception hierarchy |

### Exception Mapping
| Requests Exception | HTTPX Exception | Cognite Exception |
|-------------------|-----------------|-------------------|
| `requests.exceptions.ReadTimeout` | `httpx.ReadTimeout` | `CogniteReadTimeout` |
| `requests.exceptions.ConnectionError` | `httpx.ConnectError` | `CogniteConnectionError` |
| `requests.exceptions.JSONDecodeError` | `json.JSONDecodeError` | (handled in _json module) |

### Configuration Differences
- HTTPX uses different timeout configuration (separate connect/read timeouts)
- Connection pooling configuration differs
- Retry mechanisms need custom implementation in HTTPX
- SSL/TLS configuration has different parameter names

## Implementation Status

### ✅ Completed
- Analysis of current requests usage
- Migration plan documentation
- Updated `pyproject.toml` dependencies (requests → httpx, requests_oauthlib → authlib)
- Migrated core HTTP client (`_http_client.py`) to use httpx
- Updated session creation and configuration for httpx
- Mapped httpx exceptions to Cognite exceptions

### 🔄 In Progress  
- API client updates (`_api_client.py`) - partially migrated but needs completion
- Header management migration (started but needs refinement)

### ⏳ Pending
- Complete API client migration (fix remaining Response type annotations)
- OAuth migration (migrate from requests_oauthlib to authlib)
- Update imports across all modules using requests
- Update Pyodide compatibility layer
- Test infrastructure updates (replace responses with httpx-compatible mocking)
- Update exception handling in utility modules
- Update version checker module
- Documentation updates

### ⚠️ Known Issues to Fix
- Some type annotations still reference `requests.Response` instead of `httpx.Response`
- Header management needs refinement for httpx compatibility
- Stream handling may need adjustments for httpx differences
- OAuth integration needs to be migrated to authlib

## Testing Strategy
1. **Unit Tests**: Ensure all existing unit tests pass with httpx
2. **Integration Tests**: Verify API calls work correctly
3. **Performance Tests**: Compare performance between requests and httpx
4. **Compatibility Tests**: Ensure OAuth and authentication flows work
5. **Browser Tests**: Verify Pyodide compatibility

## Rollback Plan
- Keep migration behind feature flags initially
- Maintain parallel implementation during transition
- Comprehensive testing before removing requests dependency
- Clear rollback procedures documented

## Benefits Expected
- **Performance**: HTTPX generally has better performance characteristics
- **Modern Features**: Better HTTP/2 support, more modern API design
- **Async Support**: Better foundation for potential async SDK features
- **Maintenance**: More actively maintained library
- **Standards Compliance**: Better HTTP standards compliance

## Risk Mitigation
- Extensive testing at each phase
- Gradual migration approach
- Maintain backward compatibility where possible
- Monitor performance and error rates during transition
- Have rollback plan ready

## Timeline
- **Week 1-2**: Dependencies and core infrastructure
- **Week 3-4**: HTTP client implementation and testing
- **Week 5-6**: API client updates and OAuth migration
- **Week 7-8**: Testing infrastructure and special cases
- **Week 9-10**: Integration testing and performance validation
- **Week 11-12**: Documentation and final testing

---

*This document will be updated as the migration progresses.*