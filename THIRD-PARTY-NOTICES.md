# Third-Party Notices

SEO Prism is licensed under **AGPL-3.0-only** (or under a commercial license, see [COMMERCIAL-LICENSE.md](COMMERCIAL-LICENSE.md)). It depends on third-party open-source components, which **remain under their own licenses**. This repository does not copy those libraries; they are installed from npm and PyPI.

Dependency audit date: 2026-10-07. Regenerate this file's tables when dependencies change.

## Summary

All direct and transitive dependencies use permissive licenses (MIT, BSD, Apache-2.0, ISC, PSF-2.0, MIT-CMU), with two points that need a notice, described below. No GPL, LGPL or AGPL dependencies were found. All of these licenses are compatible with AGPL-3.0.

## Font Awesome Free (attribution required)

The frontend uses `@fortawesome/free-solid-svg-icons`.

- Icons: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- Fonts: SIL OFL 1.1
- Code: MIT

Attribution: Font Awesome Free by @fontawesome, https://fontawesome.com. License: https://fontawesome.com/license/free

The icons stay under CC BY 4.0. They are not relicensed under the AGPL or the SEO Prism commercial license.

## lightningcss (MPL-2.0)

`lightningcss` is installed as part of the Tailwind CSS v4 build toolchain. It runs at build time and is not part of the code the browser receives. SEO Prism does not modify it. Its source code is available at https://github.com/parcel-bundler/lightningcss under the Mozilla Public License 2.0.

## Direct dependencies

### Backend (Python)

| Package | License |
|---|---|
| aiohttp | Apache-2.0 AND MIT |
| fastapi | MIT |
| uvicorn | BSD-3-Clause |
| beautifulsoup4 | MIT |
| click | BSD-3-Clause |
| mcp | MIT |
| python-pptx | MIT |
| reportlab | BSD |
| pytest (dev) | MIT |

### Frontend (npm)

| Package | License |
|---|---|
| react, react-dom | MIT |
| tailwindcss, @tailwindcss/vite | MIT |
| clsx, tailwind-merge | MIT |
| @fortawesome/fontawesome-svg-core, @fortawesome/react-fontawesome | MIT |
| @fortawesome/free-solid-svg-icons | CC-BY-4.0 AND MIT |
| vite, @vitejs/plugin-react (dev) | MIT |
| typescript (dev) | Apache-2.0 |
| @types/react, @types/react-dom (dev) | MIT |

Transitive dependencies are permissive (MIT, BSD, Apache-2.0, ISC, PSF-2.0, MIT-CMU), except `lightningcss` (MPL-2.0) noted above.

## How to regenerate

```bash
# Python
pip install pip-licenses && pip-licenses --format=markdown --order=license

# Frontend
npx license-checker-rseidelsohn --summary
```
