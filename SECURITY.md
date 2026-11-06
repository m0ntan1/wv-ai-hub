# Security policy

WV AI Watch is a static site: no server, no accounts, no stored visitor data. Its content is public JSON under `data/`.

## Report a problem

- **Security issue** (a way to inject script or links, a leaked credential, a workflow that can be abused): use GitHub's private reporting, **Security > Report a vulnerability**, on this repository. If that is not available, use the contact form at https://wvaihub.com/#/contact and say only that it is a security matter; do not post details publicly.
- **Wrong fact or broken source link:** that is not a security issue. Use the contact form's "correction" topic or open an issue.

## What is in scope

The site, the build and check tools in `tools/`, and the GitHub workflows in `.github/workflows/`.

## Secrets

No API keys or tokens are stored in this repository. `ELEVENLABS_API_KEY`, `ROOK_VOICE_ID`, and `SEC_USER_AGENT` live in the environment or repository secrets, never in files. If you find one in the history, please report it privately.
