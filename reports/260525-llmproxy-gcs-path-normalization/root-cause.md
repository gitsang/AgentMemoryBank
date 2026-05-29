# llmproxy `gs://` path normalization root cause

## Finding

The `gs://` segment is collapsed to `gs:/` by `github.com/gorilla/mux` inside the custom `yauth` middleware used by `ytraefik`, not by the llmproxy backend and not by the configured `multi-slash-redirect` middleware.

## Runtime evidence

Dev ytraefik protected route:

```bash
curl --noproxy '*' --path-as-is -sv --max-time 10 --max-redirs 0 \
  -o /tmp/opencode/llmproxy-dev-gs.raw.body \
  'http://10.122.128.29:9102/llmproxy/v1/files/gs://probe-bucket/probe-object/content?model=vertex/probe'
```

Observed:

```text
HTTP/1.1 301 Moved Permanently
Location: /llmproxy/v1/files/gs:/probe-bucket/probe-object/content?model=vertex/probe
```

Generic duplicate slash under the same protected route shows the same canonicalization:

```text
GET /llmproxy/v1/files/a//b/content?model=vertex/probe
HTTP/1.1 301 Moved Permanently
Location: /llmproxy/v1/files/a/b/content?model=vertex/probe
```

Direct backend does not redirect the raw path:

```text
GET http://10.122.128.29:9601/llmproxy/v1/files/gs://probe-bucket/probe-object/content?model=vertex/probe
HTTP/1.1 401 Unauthorized
server: uvicorn
```

Non-yauth route does not redirect the raw `gs://` path:

```text
GET http://10.122.128.29:9102/yops/gs://probe-bucket/probe-object
HTTP/1.1 200 OK
```

## Source evidence

`ytraefik` exposes `yauth` as a first-class dynamic middleware:

```go
// /home/sang/src/gitcode.yealink.com/server/devops/yops/ytraefik/pkg/server/middleware/middlewares.go
if config.Yauth != nil {
    middleware = func(next http.Handler) (http.Handler, error) {
        return yauth.New(ctx, next, *config.Yauth, middlewareName)
    }
}
```

`yauth.New` wraps requests in a `gorilla/mux.Router` and installs the normal auth chain only as the router's `NotFoundHandler`:

```go
// /home/sang/src/gitcode.yealink.com/server/devops/yops/yauth-middleware/middleware.go
router := mux.NewRouter()
...
router.NotFoundHandler = http.HandlerFunc(m.defaultHandler)
```

`gorilla/mux` cleans paths before route matching and before `NotFoundHandler` dispatch unless `SkipClean(true)` is set. `yauth` does not call `SkipClean(true)`.

```go
// /home/sang/.go/pkg/mod/github.com/gorilla/mux@v1.8.1/mux.go
func (r *Router) ServeHTTP(w http.ResponseWriter, req *http.Request) {
    if !r.skipClean {
        path := req.URL.Path
        if r.useEncodedPath {
            path = req.URL.EscapedPath()
        }
        if p := cleanPath(path); p != path {
            url := *req.URL
            url.Path = p
            p = url.String()

            w.Header().Set("Location", p)
            w.WriteHeader(http.StatusMovedPermanently)
            return
        }
    }
    ...
}
```

The `cleanPath` helper delegates to `path.Clean`, which collapses duplicate slashes:

```go
np := path.Clean(p)
```

The upstream mux test confirms `SkipClean(true)` is the intended opt-out for this behavior:

```go
func TestSkipClean(t *testing.T) {
    r := NewRouter()
    r.SkipClean(true)
    ...
    req, _ := http.NewRequest("GET", "http://localhost//api/?abc=def", nil)
    r.ServeHTTP(res, req)
    if len(res.HeaderMap["Location"]) != 0 {
        t.Errorf("Shouldn't redirect since skip clean is disabled")
    }
}
```

Verified with:

```bash
go test github.com/gorilla/mux -run TestSkipClean -count=1 -v
```

Result:

```text
--- PASS: TestSkipClean (0.00s)
PASS
```

A minimal self-contained reproduction using the same `gorilla/mux` version also confirms the wrapper behavior:

```go
func TestMuxDefaultCleanRedirectsBeforeNotFoundHandler(t *testing.T) {
    r := mux.NewRouter()
    r.NotFoundHandler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusTeapot)
    })

    req := httptest.NewRequest(http.MethodGet,
        "http://example.test/llmproxy/v1/files/gs://bucket/object/content?model=vertex/probe", nil)
    res := httptest.NewRecorder()

    r.ServeHTTP(res, req)

    // Status: 301
    // Location: http://example.test/llmproxy/v1/files/gs:/bucket/object/content?model=vertex/probe
}

func TestMuxSkipCleanAllowsNotFoundHandlerToSeeRawPath(t *testing.T) {
    r := mux.NewRouter().SkipClean(true)
    r.NotFoundHandler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        // r.URL.Path remains /llmproxy/v1/files/gs://bucket/object/content
        w.WriteHeader(http.StatusTeapot)
    })
}
```

Verified with a temporary module requiring `github.com/gorilla/mux v1.8.1`:

```text
=== RUN   TestMuxDefaultCleanRedirectsBeforeNotFoundHandler
--- PASS: TestMuxDefaultCleanRedirectsBeforeNotFoundHandler (0.00s)
=== RUN   TestMuxSkipCleanAllowsNotFoundHandlerToSeeRawPath
--- PASS: TestMuxSkipCleanAllowsNotFoundHandlerToSeeRawPath (0.00s)
PASS
ok  mux-clean-repro  0.007s
```

## Root cause

Request flow for `/llmproxy/v1/files/gs://...`:

1. `ytraefik` matches the `/llmproxy` router and enters the configured `yauth` middleware.
2. `yauth.New` returns a `gorilla/mux.Router`.
3. `mux.Router.ServeHTTP` runs its default path cleaning before matching routes or invoking `NotFoundHandler`.
4. `path.Clean("/llmproxy/v1/files/gs://probe-bucket/...")` becomes `"/llmproxy/v1/files/gs:/probe-bucket/..."`.
5. mux returns `301 Moved Permanently` with the cleaned Location.
6. If the client follows that redirect, llmproxy receives `gs:/...`; downstream GCS parsing treats `gs:` as the bucket and fails with `Invalid bucket name: 'gs:'`.

## Not the cause

- `multi-slash-redirect@file`: present in runtime config, but not attached to the `/llmproxy` router or entry point in the observed runtime API.
- llmproxy/uvicorn backend: direct backend request preserves raw `gs://` and returns `401`, not `301`.
- Generic ytraefik routing: `/yops/gs://...` does not redirect.

## Reconciled background findings

- Proxy config search found no nginx `merge_slashes` or rewrite rule that would normalize `/llmproxy/v1/files/...` before ytraefik. It found `multi-slash-redirect` definitions in dev/staging/prod configs, but not attached to the `/llmproxy` routers.
- Backend parsing search found no yLLM/llmproxy backend code that rewrites `gs://` to `gs:/`. Open-WebUI-style GCS parsing is fragile for nested GCS object keys, but it would consume a malformed value rather than create the 301 redirect.
- Caller URL search did not find an exact producer of `/llmproxy/v1/files/.../content`. Some nearby Go code uses `url.JoinPath`, which can be a general slash-normalization risk, but the runtime probe reproduced the 301 with a raw `curl --path-as-is` request, so caller construction is not required for this gateway symptom.
- Traefik semantics search found current Traefik `sanitizePath` is an internal request rewrite, not a `301 Location` response. That does not match the observed ytraefik `301`, but it is consistent with the proven `gorilla/mux` wrapper behavior in yauth.

## Safe fix options

1. In `yauth-middleware/middleware.go`, call `router.SkipClean(true)` immediately after `mux.NewRouter()` for the outer yauth router. This preserves opaque downstream paths while keeping the dashboard route and `NotFoundHandler` structure.
2. Add a focused regression test around yauth's outer router: a request with `/llmproxy/v1/files/gs://bucket/object/content` must reach the next handler without a `301` and with the raw path intact.
3. If changing yauth is too broad, bypass yauth's gorilla router for pass-through paths that are not dashboard routes, but this is more invasive than disabling mux cleaning on the wrapper router.

## Implemented local fix

Applied option 1 in `/home/sang/src/gitcode.yealink.com/server/devops/yops/yauth-middleware/middleware.go`:

```go
router := mux.NewRouter()
router.SkipClean(true)
```

Added regression coverage in `/home/sang/src/gitcode.yealink.com/server/devops/yops/yauth-middleware/middleware_test.go`:

```go
func TestMiddlewarePreservesOpaquePathSegments(t *testing.T)
```

Red/green evidence:

```text
# Before the fix
--- FAIL: TestMiddlewarePreservesOpaquePathSegments (0.00s)
    middleware_test.go:36: next handler was not called

# After the fix
--- PASS: TestMiddlewarePreservesOpaquePathSegments (0.00s)
PASS
ok  gitcode.yealink.com/server/devops/yops/yauth-middleware/v2  0.022s
```

Focused verification after the fix:

```text
go test . -run TestMiddlewarePreservesOpaquePathSegments -count=1 -v
PASS

go test . -count=1
ok  gitcode.yealink.com/server/devops/yops/yauth-middleware/v2  0.020s

lsp_diagnostics middleware.go
No diagnostics found

lsp_diagnostics middleware_test.go
No diagnostics found
```

Manual middleware-surface smoke using `httptest` and the local module replacement:

```text
GET /llmproxy/v1/files/gs://bucket/object/content?model=vertex/probe
status=204
location=""
body=""
```

The smoke handler asserted that `r.URL.Path` remained `/llmproxy/v1/files/gs://bucket/object/content`.
