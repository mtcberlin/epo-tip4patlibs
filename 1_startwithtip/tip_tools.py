"""Shared helpers for the TIP4PATLIBS course notebooks.

Currently one job: open a self-contained HTML artifact so that it actually *works*
inside EPO TIP.

Why this is needed
------------------
JupyterLab serves files under `/files/` with

    Content-Security-Policy: frame-ancestors 'none'; sandbox allow-scripts

`frame-ancestors 'none'` makes embedding via `IFrame` impossible, and opening such a
file directly renders an empty page — our report HTMLs build their entire body from
JavaScript, so nothing at all appears. Serving the same file through
`jupyter-server-proxy` avoids this: that route sends no CSP header, which is the same
condition as opening the downloaded file in your own browser.

Usage
-----
    from tip_tools import open_html
    open_html("output_.../chart.html", "the technology network")

To import it from any course notebook, regardless of folder depth::

    import sys
    from pathlib import Path
    root = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "CLAUDE.md").exists())
    sys.path.insert(0, str(root / "1_startwithtip"))
"""

from __future__ import annotations

import importlib.util
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

from IPython.display import HTML, display

__all__ = ["repo_root", "open_html", "server_base"]

_STATE: dict[str, str] = {}
_ACCENT = "#be0f05"


def repo_root(start: Path | None = None) -> Path:
    """The repository root — the nearest ancestor holding CLAUDE.md."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "CLAUDE.md").exists():
            return candidate
    return here


def _wait_until_serving(port: int, timeout: float = 10.0) -> bool:
    """Poll until the port accepts connections. Beats guessing with sleep()."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        with socket.socket() as probe:
            probe.settimeout(0.25)
            if probe.connect_ex(("127.0.0.1", port)) == 0:
                return True
        time.sleep(0.1)
    return False


def server_base() -> str | None:
    """Serve the repo root through jupyter-server-proxy; return its URL prefix.

    One server per kernel, covering the whole repo, so artifacts in different module
    folders all resolve. Returns None when jupyter-server-proxy is unavailable.
    """
    if "base" in _STATE:
        return _STATE["base"]
    if importlib.util.find_spec("jupyter_server_proxy") is None:
        return None

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]

    subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=str(repo_root()),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if not _wait_until_serving(port):
        return None

    prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/").rstrip("/")
    _STATE["base"] = f"{prefix}/proxy/{port}/"
    return _STATE["base"]


def _files_url(target: Path) -> str | None:
    """A /files/ download URL, as the fallback route.

    TIP symlinks /home/<user> to /home/jovyan, so Path.home() and Path.cwd() disagree
    as *strings* and relative_to() would raise. Resolve both, and prefer Jupyter's own
    JUPYTER_SERVER_ROOT.
    """
    root = Path(os.environ.get("JUPYTER_SERVER_ROOT") or Path.home()).resolve()
    try:
        rel = "/".join(target.resolve().relative_to(root).parts)
    except ValueError:
        return None
    prefix = os.environ.get("JUPYTERHUB_SERVICE_PREFIX", "/").rstrip("/")
    return f"{prefix}/files/{rel}?download=1"


def open_html(path: str | Path, title: str | None = None) -> None:
    """Display a one-click link that opens an HTML artifact interactively inside TIP.

    `path` may be relative to the notebook or to the repo root. A download link is
    always offered alongside, because a file opened from your own filesystem runs
    without any of Jupyter's restrictions.
    """
    target = Path(path)
    if not target.is_absolute():
        for candidate in (Path.cwd() / target, repo_root() / target):
            if candidate.exists():
                target = candidate
                break
    label = title or Path(path).name

    if not target.exists():
        display(HTML(
            f'<div style="font-family:system-ui,sans-serif;color:#b91c1c;font-size:13px;">'
            f'Not found: <code>{path}</code></div>'))
        return

    links, notes = [], []
    base = server_base()
    if base:
        try:
            rel = "/".join(target.resolve().relative_to(repo_root()).parts)
        except ValueError:
            rel = None
        if rel:
            links.append(
                f'<a href="{base}{rel}" target="_blank" style="display:inline-block;'
                f'background:{_ACCENT};color:#fff;padding:10px 18px;border-radius:8px;'
                f'text-decoration:none;font-weight:600;">&#9654; Open {label}</a>')
    else:
        notes.append("jupyter-server-proxy is unavailable here, so the file cannot be "
                     "served inside TIP &mdash; download it and open it in your browser.")

    download = _files_url(target)
    if download:
        links.append(
            f'<a href="{download}" target="_blank" style="margin-left:12px;color:#64748b;'
            f'font-size:13px;">&#128229; or download it</a>')
    elif not links:
        notes.append(f"It is on disk at <code>{target}</code>.")

    size = target.stat().st_size / 1e6
    notes.append(f"{size:.1f}&nbsp;MB &middot; self-contained, no internet needed.")

    display(HTML(
        '<div style="font-family:system-ui,sans-serif;padding:8px 0;">'
        + "".join(links)
        + '<div style="margin-top:8px;font-size:12px;color:#94a3b8;">'
        + " ".join(notes) + "</div></div>"))
