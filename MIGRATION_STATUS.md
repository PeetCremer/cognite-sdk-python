# Requests to HTTPX Migration - Current Status

## ✅ What's Been Completed

### 1. Dependencies Updated
- `pyproject.toml` updated to use `httpx ^0.28.0` instead of `requests ^2.27`
- Added `authlib ^1.3.0` for OAuth functionality (replacing `requests_oauthlib`)

### 2. Core HTTP Client Migrated
- **File**: `cognite/client/_http_client.py`
- ✅ Replaced `requests.Session` with `httpx.Client`
- ✅ Updated connection pooling configuration for httpx
- ✅ Mapped timeout configuration to httpx format
- ✅ Updated exception handling to map httpx exceptions to Cognite exceptions
- ✅ Updated proxy configuration for httpx compatibility
- ✅ Added backward compatibility alias `get_global_requests_session` → `get_global_httpx_client`

### 3. API Client Partially Migrated
- **File**: `cognite/client/_api_client.py`
- ✅ Updated imports to use httpx instead of requests
- ✅ Replaced `requests.utils.default_headers()` with custom implementation
- ✅ Updated header management to use `httpx.Headers`
- ✅ Most HTTP method signatures updated to return `httpx.Response`

## 🔄 What Needs Completion

### 1. Finish API Client Migration
- Fix remaining `Response` type annotations in `_api_client.py`
- Complete header management refinements
- Test and validate all HTTP operations work correctly

### 2. Update Additional Modules
- `cognite/client/_cognite_client.py` - Update imports and response handling
- `cognite/client/utils/_version_checker.py` - Migrate from requests to httpx
- `cognite/client/utils/_pyodide_helpers.py` - Update browser compatibility layer
- `cognite/client/credentials.py` - Migrate OAuth from requests_oauthlib to authlib

### 3. Update Test Infrastructure
- Replace `responses` library with httpx-compatible mocking
- Update test imports across the test suite
- Ensure all existing tests pass with httpx

### 4. Documentation and Final Cleanup
- Update any documentation references to requests
- Clean up any remaining requests imports
- Performance testing and validation

## 🚨 Known Issues

1. **Type Annotations**: Some methods still reference `requests.Response` instead of `httpx.Response`
2. **Header Handling**: httpx handles headers differently than requests in some edge cases
3. **Stream Handling**: May need adjustments for httpx streaming differences
4. **OAuth**: Need to fully migrate authentication to use authlib instead of requests_oauthlib

## ⚡ Next Steps

1. **Complete API Client**: Fix the remaining type annotations and test basic functionality
2. **OAuth Migration**: Update OAuth flows to use authlib with httpx
3. **Test Coverage**: Ensure all existing functionality works with httpx
4. **Performance Testing**: Validate that httpx provides expected performance benefits

## 📋 Testing Plan

To test the migration:

1. Install dependencies: `pip install httpx authlib`
2. Run basic import tests to ensure no syntax errors
3. Run unit tests to validate functionality
4. Run integration tests with real API calls
5. Performance benchmarking against original requests implementation

## 🎯 Success Criteria

- [ ] All existing tests pass
- [ ] No performance regression (preferably improvement)
- [ ] All HTTP functionality works identically to requests version
- [ ] OAuth flows work correctly with authlib
- [ ] Documentation is updated

---

**Migration Progress**: ~60% complete
**Estimated Remaining Work**: 1-2 weeks for a dedicated developer
**Risk Level**: Medium (breaking changes possible, extensive testing required)