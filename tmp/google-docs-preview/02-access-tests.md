# Developer Preview access tests

Live tests on 25 August 2026 show that Google gates the Docs preview by the OAuth
client's Cloud project. Holding the Google account and document constant while
changing projects changed the response from HTTP 200 to HTTP 400.

## Result

| Google account | OAuth client project | Registration state | Preview-only read |
| --- | ---: | --- | --- |
| `alejandro.acelas-contractor@80000hours.org` | `122477011422` (`agent-cli-tools-alejandro`) | Registered | HTTP 200; `commentsViewMode: COMMENTS_VIEW_MODE_INCLUDED`; one comment and one suggestion returned |
| `alejandro.acelas-contractor@80000hours.org` | `856825977485` (`agent-cli-tools-504004`) | Not registered | HTTP 400; `comments_view_mode` rejected as an unknown field |
| `alejandro.acelas-contractor@80000hours.org` | `1009200210134` (`mac-air-2020`) | Added through the member form on 19 August | HTTP 200; same comment and suggestion returned |
| `alejoacelas@gmail.com` | `1009200210134` (`mac-air-2020`) | Project registered; consumer account could not join the program | HTTP 200; `commentsViewMode` was applied to a personal test document |

The first two rows isolate project enrollment: account, scopes, document, request, and
time were the same. The last row is evidence against a separate runtime allowlist for
every end user. Google's FAQ says access is provided through registered Cloud projects;
the live result matches that wording.

The practical rule is:

> Register every OAuth-client project that must use preview fields. Users still need
> ordinary OAuth and document permissions, but the preview parser is selected by the
> client project.

The Developer Preview application itself requires a Workspace account. That appears to
control who can register projects, not which Google identities can later authorize a
registered client. This is an inference from the tests, not an explicit Google promise.

## Projects and local clients

- Registered organization project: `122477011422`. Local `gog` client name: `80k`.
- Unregistered organization control: `856825977485`. Local `gog` client name:
  `80k-control`.
- Registered personal project: `1009200210134`. Existing `gdoc` tokens use this client.

The `80k-control` credential was already present in Downloads and the Docs, Drive, and
Sheets APIs were already enabled. This session stored its client under the `gog` name
`80k-control` and authorized only Docs, Drive, identity, and email scopes for
`alejandro.acelas-contractor@80000hours.org`.

No client secret, refresh token, or access token is recorded here or in Git. Temporary
token exports and API response files were removed immediately after the test.

## Test documents

- Work-account fixture:
  [Quick test docs](https://docs.google.com/document/d/1svOKVIWdXdX0oanqPevZPH2lznrxHaV8GQLLHkgaJkI/edit)
- Personal-account fixture:
  [Developer Preview personal comment test](https://docs.google.com/document/d/1C-pwMFAbE7MvKhoJg6bqvG6d4FsYVvhe5hzG2Y1hc-U/edit)

The work fixture already contained suggestion `suggest.rtf1xd7d5kkt` and anchored
comment `AAACFyBdz8k`, created in the earlier August test. This session made read-only
API calls and created no new document content, comments, or suggestions.

## Exact probe

Each client refreshed an access token locally, then sent the same request:

```http
GET https://docs.googleapis.com/v1/documents/DOCUMENT_ID
  ?includeTabsContent=true
  &suggestionsViewMode=SUGGESTIONS_INLINE
  &commentsViewMode=COMMENTS_VIEW_MODE_INCLUDED
Authorization: Bearer ACCESS_TOKEN
```

`commentsViewMode` is the decisive preview-only field. A normal document read or
`suggestionsViewMode` alone does not test enrollment.

The registered response contained:

```json
{
  "commentsViewMode": "COMMENTS_VIEW_MODE_INCLUDED",
  "comments": [{"commentId": "AAACFyBdz8k"}],
  "suggestions": [{"suggestionId": "suggest.rtf1xd7d5kkt"}]
}
```

The unregistered project returned:

```json
{
  "error": {
    "code": 400,
    "status": "INVALID_ARGUMENT",
    "message": "Invalid JSON payload received. Unknown name \"comments_view_mode\" ..."
  }
}
```

## Reproduce or extend the matrix

Check the clients without exposing tokens:

```bash
gog auth list --json
gog auth credentials list --json
gcloud services list --enabled --project=agent-cli-tools-504004
```

For another project-level control:

1. Use an existing Desktop OAuth client from an unregistered project with Docs and
   Drive enabled.
2. Authorize the same Google account and scopes under a distinct local client name.
3. Call the preview-only `documents.get` above against the same document.
4. Record HTTP status and whether `commentsViewMode` was applied. Do not print tokens.
5. If a write test is still necessary, try `insertComment` first: rejection is
   non-mutating. Do not use `writeMode: SUGGEST` as an enrollment probe because an
   unenrolled backend has previously treated it as a direct edit.

For an account-level control, authorize another 80,000 Hours user through the already
registered `122477011422` client and make the same read against a document shared with
that user. The personal-account result already makes per-user runtime gating unlikely,
but this would verify it inside the Workspace domain.

## Earlier work recovered

The prior session lives at
`/Users/alejo/best/work/once/2026-08-google-docs-preview/`. Its construction record
documents:

- the successful suggestion and anchored-comment writes through `122477011422`;
- the failed pre-registration calls through `1009200210134`;
- submission of `1009200210134` through Google's add-project form on 19 August; and
- the warning that an unenrolled project once ignored suggest mode and made a direct
  edit.

Today's HTTP 200 through `1009200210134` closes that record's “waiting for Google”
state: the project has now acquired preview access.

See [the API inventory](01-preview-api.md) and
[the implementation design](03-cli-design.md).
