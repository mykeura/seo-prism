# Security Policy

## Supported versions

Security fixes are only released for the latest published version of SEO Prism.
Before reporting, upgrade to the newest release (currently **1.26.0**) and check
whether the issue still reproduces.

| Version | Supported |
|---|---|
| 1.26.0 | ✅ |
| earlier releases | ❌ (upgrade first) |

## Reporting a vulnerability

Do **not** open a public GitHub issue for security problems.

Report privately to **mykeura@hotmail.com** (the contact listed in
[COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)). If private vulnerability
reporting is enabled on the GitHub repository, a GitHub security advisory is
also welcome.

Please include:

- A description of the issue and its impact.
- The version or commit hash you tested against.
- Step-by-step instructions or a proof of concept to reproduce it.
- Any known mitigations.

## Response commitment

- **Acknowledgement:** within 5 business days of your report.
- **Triage decision:** within 10 business days you will receive an assessment
  (accepted / not a vulnerability / more information needed).
- **Fix target:** critical and high severity issues are patched within 90 days
  of acceptance; lower severity issues may be scheduled for the next release.
- You will be kept informed of the progress at every stage.

## Disclosure policy

This project follows coordinated disclosure:

1. The report is handled privately until a fix is available.
2. A patched release is published first.
3. The advisory is published afterwards (GitHub advisory and release notes),
   crediting the reporter by name or handle, unless anonymity is requested.

Please give the maintainer a reasonable window (90 days from the report,
extendable by agreement) before publishing technical details of a
vulnerability.

Good-faith research against your own instance of SEO Prism is welcome and will
not be met with legal action. Out of scope: volumetric scanning or denial of
service, social engineering, and attacks against third-party websites that are
merely crawled by the tool rather than against SEO Prism itself.
