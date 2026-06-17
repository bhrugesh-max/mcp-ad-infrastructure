#!/usr/bin/env python3
"""
LogicMonitor MCP Server for Claude Desktop — Bearer Token Auth
Gives Claude native access to your LogicMonitor environment.

Setup:
  1. pip install mcp
  2. Create lm_creds.json in the same folder:
     {
       "account": "flowcontrolgroup",
       "bearer_token": "lmb_NWV5NHlK...your full token..."
     }
  3. Add to Claude Desktop config (see bottom of this file)
  4. Restart Claude Desktop
"""

import json
import os
import asyncio
import urllib.request
import urllib.error
import ssl

# ── Load credentials from lm_creds.json ─────────────────────────────────────
CREDS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lm_creds.json")

def load_creds():
    with open(CREDS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

CREDS = load_creds()
ACCOUNT      = CREDS["account"]
BEARER_TOKEN = CREDS["bearer_token"]

# ── LM API helper ─────────────────────────────────────────────────────────────
def lm_request(method: str, path: str, params: str = "size=250&offset=0") -> dict:
    url = f"https://{ACCOUNT}.logicmonitor.com/santaba/rest{path}?{params}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json",
            "X-version": "3",
        },
        method=method,
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}", "detail": e.read().decode()}
    except Exception as e:
        return {"error": str(e)}


# ── MCP Server ────────────────────────────────────────────────────────────────
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
except ImportError:
    print("ERROR: Run 'pip install mcp' first.")
    raise

app = Server("logicmonitor")


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="lm_get_alert_rules",
            description=(
                "Fetch all LogicMonitor alert rules. "
                "Returns name, priority, datasource, escalation chain, active status, "
                "and suppression settings. Use to find missing escalations, duplicate "
                "rules, noisy thresholds, or inactive rules."
            ),
            inputSchema={"type": "object", "properties": {
                "size": {"type": "integer", "default": 250}
            }},
        ),
        types.Tool(
            name="lm_get_devices",
            description=(
                "Fetch monitored devices/resources. Returns display name, hostname, "
                "collector, device type, group membership, and last data time. "
                "Use to find orphaned devices, stale devices, or misconfigured ones."
            ),
            inputSchema={"type": "object", "properties": {
                "size": {"type": "integer", "default": 250},
                "filter": {"type": "string", "description": "LM filter e.g. 'displayName~prod'"}
            }},
        ),
        types.Tool(
            name="lm_get_datasources",
            description=(
                "Fetch all datasources (monitoring templates). With 2370 datasources "
                "this is the most important endpoint to analyse for clutter. Returns "
                "name, type, version, applied device count. Use to find unused, "
                "duplicate, or outdated datasources."
            ),
            inputSchema={"type": "object", "properties": {
                "size": {"type": "integer", "default": 250},
                "offset": {"type": "integer", "default": 0}
            }},
        ),
        types.Tool(
            name="lm_get_escalation_chains",
            description=(
                "Fetch all escalation chains — who gets notified and in what order. "
                "Returns name, destinations, throttling. Use to find unused chains, "
                "chains with no recipients, or duplicate chains."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="lm_get_dashboards",
            description=(
                "Fetch all dashboards. With 110 dashboards there is likely clutter. "
                "Returns name, owner, group, widget count, last modified. "
                "Use to find unused, duplicate, or orphaned dashboards."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="lm_get_recipient_groups",
            description="Fetch all alert recipient groups and their members.",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="lm_get_active_alerts",
            description=(
                "Fetch currently active/firing alerts. Returns device, datapoint, "
                "severity, start time, and acknowledgement status. Use to identify "
                "noisy alert rules or chronic problem devices."
            ),
            inputSchema={"type": "object", "properties": {
                "size": {"type": "integer", "default": 50},
                "filter": {"type": "string", "description": "e.g. 'severity>3'"}
            }},
        ),
        types.Tool(
            name="lm_get_sdts",
            description=(
                "Fetch Scheduled Down Times (maintenance windows). "
                "Use to find expired, overlapping, or unnecessary SDTs."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="lm_get_device_groups",
            description=(
                "Fetch device group hierarchy. Use to find empty groups, "
                "misnamed groups, or groups with no alert rules applied."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="lm_get_collectors",
            description=(
                "Fetch all collectors. Use to find offline collectors, "
                "overloaded collectors, or collectors with no devices assigned."
            ),
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="lm_search",
            description="Search any LM REST endpoint with a custom path and filter.",
            inputSchema={"type": "object", "properties": {
                "endpoint": {"type": "string", "description": "API path e.g. /setting/alert/rules"},
                "filter":   {"type": "string", "description": "LM filter string"},
                "size":     {"type": "integer", "default": 100},
                "offset":   {"type": "integer", "default": 0},
            }, "required": ["endpoint"]},
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    def respond(data) -> list[types.TextContent]:
        return [types.TextContent(type="text", text=json.dumps(data, indent=2))]

    if name == "lm_get_alert_rules":
        size = arguments.get("size", 250)
        return respond(lm_request("GET", "/setting/alert/rules", f"size={size}&offset=0"))

    elif name == "lm_get_devices":
        size = arguments.get("size", 250)
        f    = arguments.get("filter", "")
        params = f"size={size}&offset=0" + (f"&filter={f}" if f else "")
        return respond(lm_request("GET", "/device/devices", params))

    elif name == "lm_get_datasources":
        size   = arguments.get("size", 250)
        offset = arguments.get("offset", 0)
        return respond(lm_request("GET", "/setting/datasources", f"size={size}&offset={offset}"))

    elif name == "lm_get_escalation_chains":
        return respond(lm_request("GET", "/setting/alert/chains", "size=250&offset=0"))

    elif name == "lm_get_dashboards":
        return respond(lm_request("GET", "/dashboard/dashboards", "size=250&offset=0"))

    elif name == "lm_get_recipient_groups":
        return respond(lm_request("GET", "/setting/recipientgroups", "size=250&offset=0"))

    elif name == "lm_get_active_alerts":
        size = arguments.get("size", 50)
        f    = arguments.get("filter", "")
        params = f"size={size}&offset=0" + (f"&filter={f}" if f else "")
        return respond(lm_request("GET", "/alert/alerts", params))

    elif name == "lm_get_sdts":
        return respond(lm_request("GET", "/sdt/sdts", "size=250&offset=0"))

    elif name == "lm_get_device_groups":
        return respond(lm_request("GET", "/device/groups", "size=250&offset=0"))

    elif name == "lm_get_collectors":
        return respond(lm_request("GET", "/setting/collector/collectors", "size=250&offset=0"))

    elif name == "lm_search":
        endpoint = arguments["endpoint"]
        size     = arguments.get("size", 100)
        offset   = arguments.get("offset", 0)
        f        = arguments.get("filter", "")
        params   = f"size={size}&offset={offset}" + (f"&filter={f}" if f else "")
        return respond(lm_request("GET", endpoint, params))

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Entry point ───────────────────────────────────────────────────────────────
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())