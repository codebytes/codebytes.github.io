---
title: "MITRE ATT&CK for Developers: Beyond OWASP"
date: '2026-02-28'
draft: false
categories:
- Security
tags:
- Security
- MITRE
- ATT&CK
- OWASP
- Cybersecurity
- Application Security
image: images/14-attack-tactics.drawio.png
featureImage: images/14-attack-tactics.drawio.png
aliases:
- /security/mitre-attack-framework/
slug: mitre-attack-framework
---

Most developers know the OWASP Top 10, but fewer know MITRE ATT&CK. OWASP tells you what can break. ATT&CK tells you how attackers actually operate. Together, they give you a complete picture of application security.

> I'll be presenting this topic at [NDC Security 2026](https://ndcsecurity.com/) in Oslo, March 2-5. If you're attending, come check out my talk — **MITRE ATT&CK for Developers** — on Wednesday, March 4 at 10:20.

<!--more-->

## The Security Challenge

Modern applications have a massive attack surface — APIs, microservices, cloud resources — every one a potential entry point. Attackers chain multiple techniques across stages, adapting as they go. Traditional defenses focus on single points of failure, but sophisticated attacks slip through.

The uncomfortable truth: attackers iterate faster than our defenses.

## What is OWASP

[OWASP](https://owasp.org/) is a community-driven organization that publishes security standards for web applications. The **OWASP Top 10** catalogs the most critical risks:

| # | Category |
|---|---|
| A01 | Broken Access Control |
| A02 | Cryptographic Failures |
| A03 | Injection |
| A04 | Insecure Design |
| A05 | Security Misconfiguration |
| A06 | Vulnerable and Outdated Components |
| A07 | Identification and Authentication Failures |
| A08 | Software and Data Integrity Failures |
| A09 | Security Logging and Monitoring Failures |
| A10 | Server-Side Request Forgery (SSRF) |

OWASP's strength is **prevention** — it tells you what vulnerabilities exist and how to fix them.

## What is MITRE

[MITRE](https://www.mitre.org/) is a not-for-profit, vendor-neutral organization founded in 1958. They maintain an ecosystem of interlocking cybersecurity frameworks:

- **CVE** - catalogs specific vulnerabilities in software
- **CWE** - classifies underlying weakness types in code
- **CAPEC** - documents attack patterns
- **ATT&CK** - maps real-world adversary behavior
- **D3FEND** - catalogs defensive countermeasures
- **ATLAS** - covers AI and machine learning threats

{{< figure src="/images/mitre-ecosystem.drawio.png" alt="MITRE Cybersecurity Ecosystem" class="mx-auto" width="900" >}}

## What is MITRE ATT&CK

[MITRE ATT&CK](https://attack.mitre.org/) (Adversarial Tactics, Techniques, and Common Knowledge) is a knowledge base of adversary behavior based on real-world cyber attacks. Born from a 2013 experiment at Fort Meade, it catalogs what attackers actually do across the full attack lifecycle.

The Enterprise Matrix has **14 tactics**, over **200 techniques**, and **400+ sub-techniques**.

### How It Is Organized

- **Tactics** - the "why" (the adversary's goal)
- **Techniques** - the "how" (the method used)
- **Sub-techniques** - specific implementations
- **Procedures** - real-world examples from threat actors

### The 14 Tactics

| Phase | Tactics |
|-------|---------|
| **Pre-Attack** | Reconnaissance, Resource Development |
| **Get In** | Initial Access, Execution, Persistence, Privilege Escalation |
| **Stay In** | Defense Evasion, Credential Access, Discovery, Lateral Movement |
| **Act** | Collection, Command and Control, Exfiltration, Impact |

{{< figure src="/images/14-attack-tactics.drawio.png" alt="The 14 ATT&CK Tactics" class="mx-auto" width="900" >}}

## OWASP vs ATT&CK: Why You Need Both

These frameworks are **complementary, not competitive**:

| | OWASP | MITRE ATT&CK |
|---|---|---|
| **Focus** | Vulnerabilities | Adversary behavior |
| **Perspective** | What breaks | What attackers do |
| **Approach** | Prevention-first | Detection-oriented |
| **Scope** | Application layer | Full attack lifecycle |

{{< figure src="/images/owasp-attack-integration.drawio.png" alt="OWASP and ATT&CK Integration" class="mx-auto" width="900" >}}

> "OWASP prevents vulnerabilities. ATT&CK detects adversary behavior."

A single OWASP vulnerability can enable multiple ATT&CK techniques:

| OWASP Category | ATT&CK Techniques |
|---|---|
| Broken Access Control | T1078 (Valid Accounts), T1098 (Account Manipulation), T1068 (Privilege Escalation) |
| Injection | T1190 (Exploit Public-Facing App), T1059 (Command Injection) |
| Security Misconfiguration | T1552 (Unsecured Credentials), T1082 (System Info Discovery) |
| Cryptographic Failures | T1555 (Credentials from Password Stores), T1565 (Data Manipulation) |
| Authentication Failures | T1087 (Account Discovery), T1110 (Brute Force) |

## Why Developers Should Care

**You already use MITRE data.** Tools like Dependabot, Snyk, and Trivy report CVEs and CWEs under the hood. Understanding the ecosystem helps you make better decisions about what to fix and why.

**Shared vocabulary.** When your SOC team says "we detected T1190," you'll know they mean exploitation of a public-facing application and can reason about which services might be affected.

**Your code is the detection layer.** The logs and telemetry you emit feed directly into ATT&CK-based detection systems. Better observability means faster threat detection.

### Attack Chains Are Real

Attackers chain multiple techniques together. A supply chain attack might unfold like this:

1. Attacker publishes a typosquatted npm package
2. Post-install script executes a payload
3. Payload harvests credentials from environment variables
4. Stolen credentials provide production access
5. Attacker creates a backdoor IAM user for persistence
6. Customer data is exfiltrated

{{< figure src="/images/attack-chain-supply.drawio.png" alt="Supply Chain Attack Chain" class="mx-auto" width="900" >}}

Six techniques, six tactics, one continuous attack. Defend only at the perimeter and you miss five of six detection opportunities. Real attacks also loop and backtrack — ATT&CK captures this reality with a matrix rather than a linear chain.

## What You Can Do Today

Start with three high-impact techniques:

1. **T1078 - Valid Accounts** — monitor authentication patterns for credential stuffing
2. **T1539 - Steal Web Session Cookie** — secure session management with fingerprinting and short expiration
3. **T1213 - Data from Information Repositories** — behavioral analytics to detect unusual data access

Then build from there:

- **Map features to techniques** — identify which ATT&CK techniques each feature could enable
- **Tag logs with technique IDs** — so your SIEM can correlate events
- **Use the ATT&CK Navigator** — visualize coverage and gaps
- **Include ATT&CK in threat modeling** — consider how attackers would chain techniques
- **Review code for both** — OWASP vulnerabilities AND technique resistance

{{< figure src="/images/defense-in-depth.drawio.png" alt="Defense in Depth Architecture" class="mx-auto" width="900" >}}

## Resources

- [MITRE ATT&CK Enterprise Matrix](https://attack.mitre.org/matrices/enterprise/)
- [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Developer Guide](https://owasp.org/www-project-developer-guide/)
- [MITRE D3FEND](https://d3fend.mitre.org/)

## Conclusion

OWASP and ATT&CK are two sides of the same coin — prevent what you can, detect what you cannot. Understanding how attackers operate makes you a better developer. Start small, pick a few high-impact techniques, and build from there.
