# MCP Server — Active Directory & Infrastructure Troubleshooting

A Model Context Protocol (MCP) server that enables natural-language querying of enterprise infrastructure systems — Active Directory, DNS, Group Policy, and LogicMonitor — built as a home lab project to explore the future of AIOps and intelligent infrastructure management.

## What This Does

Traditional AD troubleshooting means switching between multiple tools and dashboards. This MCP server connects Claude (AI) directly to infrastructure data sources, allowing plain-English queries like:

- _"Which domain controllers are showing replication errors?"_
- _"What GPOs are linked to this OU?"_
- _"Show me recent account lockouts for this user"_
- _"Which devices have open critical alerts in LogicMonitor?"_

And getting answers in seconds — without leaving your workflow.

## Architecture

```
Claude (AI) <──> MCP Server <──> Active Directory / DNS / Group Policy
                             <──> LogicMonitor API
```

- **Protocol:** Model Context Protocol (MCP)
- **Language:** Python 3.11
- **Auth:** Bearer token (LogicMonitor), Windows integrated auth (AD)
- **Transport:** stdio (local) / SSE (remote)

## Features

- Natural-language queries against live Active Directory data
- Domain controller replication health checks
- GPO enumeration and OU linking
- Account lockout investigation
- LogicMonitor alert triage and device status queries
- DNS record lookups
- Incident context aggregation across monitoring platforms

## Why I Built This

I wanted to understand where enterprise AIOps is actually heading — not from a vendor demo, but by building it myself. This project explores how AI can reduce the cognitive overhead of infrastructure troubleshooting by sitting between the engineer and the data.

This is a home lab project built for learning, experimentation, and career development.

## Tech Stack

- Python 3.11
- [MCP SDK](https://github.com/anthropics/mcp)
- LogicMonitor REST API v3
- Active Directory (via PowerShell / LDAP)
- Claude (Anthropic) as the AI layer

## Setup

```bash
# Clone the repo
git clone https://github.com/bhrugesh-max/mcp-ad-infrastructure.git
cd mcp-ad-infrastructure

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cp .env.example .env
# Edit .env with your LogicMonitor credentials and AD details

# Run the MCP server
python lm_mcp_server.py
```

## Status

🔧 **Active development** — home lab environment, continuously expanding capabilities.

Planned additions:
- Azure / Entra ID integration
- Group Policy change tracking
- Automated incident correlation
- Natural-language runbook execution

## Author

**Bhrugesh Mehta** — Senior Infrastructure & Cloud Engineer  
[LinkedIn](https://www.linkedin.com/in/bhrugeshmehta) | Fort Mill, SC

---

*Built for learning. Inspired by the belief that the best engineers build the tools they wish existed.*
