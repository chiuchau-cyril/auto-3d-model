"""Export an ezdxf Drawing to DWG R2000 bytes via ODA File Converter.

Uses ezdxf's odafc add-on, which writes a temporary DXF, invokes the locally
installed ODA File Converter, then reads back the DWG bytes.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import ezdxf
from ezdxf.addons import odafc

if TYPE_CHECKING:
    from ezdxf.document import Drawing


class OdaConverterNotInstalled(RuntimeError):
    """Raised when ODA File Converter cannot be invoked."""


_MACOS_DEFAULT = "/Applications/ODAFileConverter.app/Contents/MacOS/ODAFileConverter"


def _configure_oda_path() -> None:
    """Tell ezdxf's odafc add-on where the ODA File Converter binary lives."""
    explicit = os.environ.get("ODAFC_EXEC_PATH")
    target: str | None = None
    if explicit and Path(explicit).is_file():
        target = explicit
    elif Path(_MACOS_DEFAULT).is_file():
        target = _MACOS_DEFAULT

    if target is not None:
        ezdxf.options.set("odafc-addon", "unix_exec_path", target)
        ezdxf.options.set("odafc-addon", "win_exec_path", target)


_BENIGN_MACOS_STDERR = "IMKCFRunLoopWakeUpReliable"


def export_dwg(doc: "Drawing") -> bytes:
    _configure_oda_path()

    if not odafc.is_installed():
        raise OdaConverterNotInstalled(
            "ODA File Converter not found. Set ODAFC_EXEC_PATH to the executable path."
        )

    with tempfile.TemporaryDirectory(prefix="flange_") as tmpdir:
        dwg_path = Path(tmpdir) / "flange.dwg"
        try:
            odafc.export_dwg(doc, str(dwg_path), version="R2000")
        except odafc.UnknownODAFCError as exc:
            # macOS prints a benign IMK warning to stderr; ezdxf treats any
            # stderr as failure. Verify the file actually exists before re-raising.
            if _BENIGN_MACOS_STDERR in str(exc) and dwg_path.is_file():
                pass
            else:
                raise
        return dwg_path.read_bytes()
