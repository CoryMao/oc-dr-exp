#!/usr/bin/env python3
"""Safer arxiv-mcp-server launcher for OpenClaw experiments.

This wrapper keeps the upstream MCP tool names intact, but avoids two failure
paths that make long OpenClaw runs unstable on restricted networks:

- download_paper no longer launches best-effort semantic indexing after a
  successful download.
- PDF fallback downloads https://arxiv.org/pdf/<id> directly and converts it
  with pdftotext, avoiding export.arxiv.org metadata calls.
- search_papers uses a short raw export.arxiv.org probe and returns a warning
  payload instead of keeping the MCP call open until OpenClaw kills the server.
"""

from __future__ import annotations

import asyncio
import gc
import html
import json
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import httpx
import mcp.types as types


logger = logging.getLogger("openclaw-arxiv-mcp-safe")


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def _strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _extract_meta(page: str, name: str) -> list[str]:
    pattern = (
        r'<meta\s+name=["\']'
        + re.escape(name)
        + r'["\']\s+content=["\'](.*?)["\']\s*/?>'
    )
    return [html.unescape(match).strip() for match in re.findall(pattern, page, re.I | re.S)]


def _patch_server() -> Any:
    import arxiv
    import arxiv_mcp_server.server as server_module
    from arxiv_mcp_server import config as config_module
    from arxiv_mcp_server.tools import download as download_module
    from arxiv_mcp_server.tools import get_abstract as abstract_module
    from arxiv_mcp_server.tools import read_paper as read_module
    from arxiv_mcp_server.tools import search as search_module

    def get_arxiv_client(page_size: int = 100):
        return arxiv.Client(
            page_size=page_size,
            delay_seconds=_env_float("ARXIV_MCP_DELAY_SECONDS", 6.0),
            num_retries=_env_int("ARXIV_MCP_NUM_RETRIES", 0),
        )

    config_module.get_arxiv_client = get_arxiv_client
    search_module.get_arxiv_client = get_arxiv_client
    download_module.get_arxiv_client = get_arxiv_client

    async def _noop_index(*_args: Any, **_kwargs: Any) -> None:
        return None

    download_module._semantic_search_available = False
    download_module._run_index_by_id = _noop_index
    download_module._run_index_from_result = _noop_index

    pdftotext = shutil.which("pdftotext") or "/opt/homebrew/bin/pdftotext"
    if Path(pdftotext).exists():
        download_module._pdf_available = True

        def _fetch_pdf_content_direct(paper_id: str):
            pdf_path = download_module.get_paper_path(paper_id, ".pdf")
            url = f"https://arxiv.org/pdf/{paper_id}"
            response = httpx.get(
                url,
                timeout=_env_float("ARXIV_MCP_PDF_TIMEOUT", 60.0),
                follow_redirects=True,
            )
            if response.status_code == 404:
                raise download_module.PaperNotFoundError(
                    f"Paper {paper_id} not found on arXiv"
                )
            response.raise_for_status()
            pdf_path.write_bytes(response.content)

            proc = subprocess.run(
                [pdftotext, "-layout", str(pdf_path), "-"],
                check=True,
                capture_output=True,
                text=True,
            )
            markdown = proc.stdout
            gc.collect()
            try:
                pdf_path.unlink()
            except OSError:
                pass

            return markdown, SimpleNamespace(paper_id=paper_id)

        download_module._fetch_pdf_content = _fetch_pdf_content_direct

    def _truncate_tool_result(result: list[types.TextContent]) -> list[types.TextContent]:
        limit = _env_int("ARXIV_MCP_CONTENT_CHAR_LIMIT", 35000)
        if limit <= 0:
            return result

        truncated: list[types.TextContent] = []
        for item in result:
            if item.type != "text":
                truncated.append(item)
                continue
            try:
                payload = json.loads(item.text)
            except json.JSONDecodeError:
                truncated.append(item)
                continue

            content = payload.get("content")
            if isinstance(content, str) and len(content) > limit:
                original_chars = len(content)
                payload["content"] = (
                    content[:limit]
                    + "\n\n[CONTENT_TRUNCATED: tool response capped at "
                    + f"{limit} characters from {original_chars}. "
                    + "The full paper remains cached; ask for narrower evidence "
                    + "instead of rereading the entire paper.]"
                )
                payload["content_truncated"] = True
                payload["content_original_chars"] = original_chars
                if isinstance(payload.get("message"), str):
                    payload["message"] += " Response content was truncated."
                else:
                    payload["message"] = "Response content was truncated."

            truncated.append(
                types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False))
            )
        return truncated

    original_handle_download = download_module.handle_download
    original_handle_read_paper = read_module.handle_read_paper

    async def safe_download(arguments: dict[str, Any]) -> list[types.TextContent]:
        return _truncate_tool_result(await original_handle_download(arguments))

    async def safe_read_paper(arguments: dict[str, Any]) -> list[types.TextContent]:
        return _truncate_tool_result(await original_handle_read_paper(arguments))

    async def safe_search(arguments: dict[str, Any]) -> list[types.TextContent]:
        max_results = min(int(arguments.get("max_results", 10)), 50)
        query = (arguments.get("query") or "").strip()
        categories = arguments.get("categories") or []
        date_from = arguments.get("date_from")
        date_to = arguments.get("date_to")
        sort_by = arguments.get("sort_by", "relevance")

        query_parts: list[str] = []
        if query:
            query_parts.append(f"({query})")
        if categories:
            query_parts.append("(" + " OR ".join(f"cat:{cat}" for cat in categories) + ")")
        if date_from or date_to:
            from datetime import datetime

            start = (date_from or "1991-07-01").replace("-", "") + "0000"
            end = (date_to or datetime.now().strftime("%Y-%m-%d")).replace("-", "") + "2359"
            query_parts.append(f"submittedDate:[{start}+TO+{end}]")

        if not query_parts:
            payload = {
                "total_results": 0,
                "papers": [],
                "warning": "No arXiv search criteria provided.",
            }
            return [types.TextContent(type="text", text=json.dumps(payload, indent=2))]

        final_query = " AND ".join(query_parts)
        encoded_query = (
            final_query.replace(" AND ", "+AND+")
            .replace(" OR ", "+OR+")
            .replace(" ", "+")
        )
        sort_map = {"relevance": "relevance", "date": "submittedDate"}
        url = (
            f"{search_module.ARXIV_API_URL}?search_query={encoded_query}"
            f"&max_results={max_results}"
            f"&sortBy={sort_map.get(sort_by, 'relevance')}"
            "&sortOrder=descending"
        )

        timeout = _env_float("ARXIV_MCP_EXPORT_TIMEOUT", 10.0)
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=search_module.ARXIV_HEADERS)
            if response.status_code in (429, 503):
                payload = {
                    "total_results": 0,
                    "papers": [],
                    "warning": (
                        f"arXiv export API unavailable: HTTP {response.status_code}. "
                        "Use web_search/web_fetch fallback and retry later."
                    ),
                }
            else:
                response.raise_for_status()
                papers = search_module._parse_arxiv_atom_response(response.text)
                payload = {"total_results": len(papers), "papers": papers}
        except Exception as exc:
            payload = {
                "total_results": 0,
                "papers": [],
                "warning": (
                    f"arXiv export API unavailable within {timeout:g}s: "
                    f"{type(exc).__name__}: {exc}. Use web_search/web_fetch fallback."
                ),
            }

        return [types.TextContent(type="text", text=json.dumps(payload, indent=2))]

    async def safe_get_abstract(arguments: dict[str, Any]) -> list[types.TextContent]:
        paper_id = (arguments.get("paper_id") or "").strip()
        if not paper_id:
            payload = {"status": "error", "message": "paper_id is required"}
            return [types.TextContent(type="text", text=json.dumps(payload))]

        timeout = _env_float("ARXIV_MCP_ABS_TIMEOUT", 15.0)
        url = f"https://arxiv.org/abs/{paper_id}"
        try:
            response = httpx.get(url, timeout=timeout, follow_redirects=True)
            response.raise_for_status()
            page = response.text
            abstract_match = re.search(
                r'<blockquote[^>]*class=["\']abstract[^"\']*["\'][^>]*>(.*?)</blockquote>',
                page,
                re.I | re.S,
            )
            abstract = _strip_tags(abstract_match.group(1)) if abstract_match else ""
            abstract = re.sub(r"^Abstract:\s*", "", abstract, flags=re.I)
            payload = {
                "status": "success",
                "paper_id": paper_id,
                "title": (_extract_meta(page, "citation_title") or [""])[0],
                "authors": _extract_meta(page, "citation_author"),
                "abstract": "[EXTERNAL CONTENT] " + abstract,
                "categories": [],
                "published": (_extract_meta(page, "citation_date") or [""])[0],
                "pdf_url": f"https://arxiv.org/pdf/{paper_id}",
                "source": "arxiv_abs_page",
            }
        except Exception as exc:
            payload = {
                "status": "error",
                "message": (
                    f"Could not fetch abs page within {timeout:g}s: "
                    f"{type(exc).__name__}: {exc}"
                ),
            }

        return [types.TextContent(type="text", text=json.dumps(payload, indent=2))]

    search_module.handle_search = safe_search
    abstract_module.handle_get_abstract = safe_get_abstract
    download_module.handle_download = safe_download
    read_module.handle_read_paper = safe_read_paper
    server_module.handle_search = safe_search
    server_module.handle_get_abstract = safe_get_abstract
    server_module.handle_download = safe_download
    server_module.handle_read_paper = safe_read_paper
    return server_module


def main() -> None:
    logging.basicConfig(
        level=os.environ.get("ARXIV_MCP_LOG_LEVEL", "WARNING"),
        stream=sys.stderr,
        force=True,
    )
    server_module = _patch_server()
    logging.basicConfig(
        level=os.environ.get("ARXIV_MCP_LOG_LEVEL", "WARNING"),
        stream=sys.stderr,
        force=True,
    )
    asyncio.run(server_module.main())


if __name__ == "__main__":
    main()
