#!/usr/bin/env python3
"""Stdio-clean launcher for mcp-refchecker.

OpenClaw starts MCP servers over stdio, so stdout must contain only JSON-RPC
messages. Some mcp-refchecker / FastMCP logging paths emit INFO lines to
stdout, which can make OpenClaw report "MCP error -32000: Connection closed".
This wrapper keeps the upstream tool behavior unchanged while forcing logs to
stderr and suppressing INFO-level MCP request logs.
"""

from __future__ import annotations

import logging
import os
import sys


def _configure_logging() -> None:
    logging.basicConfig(
        level=os.environ.get("MCP_REFCHECKER_LOG_LEVEL", "WARNING"),
        stream=sys.stderr,
        force=True,
    )
    for name in ("mcp", "mcp.server", "mcp.server.lowlevel", "mcp.server.lowlevel.server"):
        logging.getLogger(name).setLevel(logging.WARNING)


def main() -> None:
    _configure_logging()
    from mcp_refchecker import server

    _configure_logging()
    server.main()


if __name__ == "__main__":
    main()
