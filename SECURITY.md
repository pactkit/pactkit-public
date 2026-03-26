# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.4.x   | :white_check_mark: |
| < 1.4   | :x:                |

We only provide security fixes for the latest minor release. Users on older versions should upgrade.

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, use [GitHub Security Advisories](https://github.com/pactkit/pactkit/security/advisories/new) to report vulnerabilities privately. This ensures the issue is handled confidentially until a fix is available.

When reporting, please include:

- A description of the vulnerability
- Steps to reproduce the issue
- The potential impact
- Any suggested fixes (if applicable)

You should receive an initial response within **72 hours**. We will keep you informed of our progress toward a fix and release.

## Scope

PactKit is a CLI tool that generates and deploys prompt templates for AI coding assistants. The following areas are in scope for security reports:

| Area | Examples |
|------|----------|
| **Supply chain** | Compromised dependencies, malicious packages |
| **Prompt injection** | Template content that could cause unintended AI behavior |
| **File system safety** | Path traversal in deployer, unsafe file writes |
| **Configuration security** | Secrets leaking through generated config files |
| **Code execution** | Command injection via user-supplied arguments |

The following are **out of scope**:

- Vulnerabilities in Claude Code itself (report to [Anthropic](https://www.anthropic.com/responsible-disclosure))
- Vulnerabilities in third-party MCP servers
- Issues in user-generated Spec or test content

## Disclosure Policy

1. **Report received** — We acknowledge within 72 hours
2. **Triage** — We assess severity and impact within 7 days
3. **Fix development** — We develop and test a fix
4. **Release** — We publish a patched version and a GitHub Security Advisory
5. **Public disclosure** — The advisory is made public 30 days after the fix is released, or immediately if the vulnerability is already publicly known

We follow [coordinated vulnerability disclosure](https://en.wikipedia.org/wiki/Coordinated_vulnerability_disclosure) principles. We ask that you do not publicly disclose the vulnerability until we have had a chance to address it.
