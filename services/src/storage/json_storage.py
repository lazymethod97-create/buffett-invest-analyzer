"""JSON persistence implementation for score snapshots."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import List, Optional, Union

from .models import ScoreSnapshot


class JsonScoreStorage:
    """Persist ScoreSnapshot records as JSON files.

    The storage implementation is deliberately independent from Streamlit,
    analysis_bundle, overall_eval, and the UI.

    One file is maintained per ticker:
        <base_dir>/<normalized-ticker>.json
    """

    def __init__(self, base_dir: Union[str, Path]) -> None:
        self.base_dir = Path(base_dir)

    def _ticker_key(self, ticker: str) -> str:
        value = str(ticker).strip()

        if not value:
            raise ValueError("ticker must not be empty")

        safe = "".join(
            character
            if character.isalnum() or character in ("-", "_", ".")
            else "_"
            for character in value
        )

        safe = safe.strip("._")

        if not safe:
            raise ValueError("ticker contains no usable characters")

        return safe.upper()

    def _path_for(self, ticker: str) -> Path:
        return self.base_dir / f"{self._ticker_key(ticker)}.json"

    def _ensure_directory(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _read(self, path: Path) -> List[ScoreSnapshot]:
        if not path.exists():
            return []

        try:
            with path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON storage file: {path}") from exc

        if not isinstance(payload, list):
            raise ValueError(f"storage file must contain a list: {path}")

        return [ScoreSnapshot.from_dict(item) for item in payload]

    def _write(self, path: Path, snapshots: List[ScoreSnapshot]) -> None:
        self._ensure_directory()

        payload = [snapshot.to_dict() for snapshot in snapshots]

        fd, temporary_name = tempfile.mkstemp(
            prefix=f"{path.stem}_",
            suffix=".tmp",
            dir=str(self.base_dir),
            text=True,
        )

        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as file:
                json.dump(
                    payload,
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
                file.write("\n")

            os.replace(temporary_name, path)

        except Exception:
            try:
                os.unlink(temporary_name)
            except FileNotFoundError:
                pass
            raise

    def save(self, snapshot: ScoreSnapshot) -> ScoreSnapshot:
        """Append one snapshot and persist it atomically."""

        if not isinstance(snapshot, ScoreSnapshot):
            raise TypeError("snapshot must be a ScoreSnapshot")

        path = self._path_for(snapshot.ticker)

        snapshots = self._read(path)
        snapshots.append(snapshot)

        self._write(path, snapshots)

        return snapshot

    def load_history(self, ticker: str) -> List[ScoreSnapshot]:
        """Load all snapshots for one ticker in stored order."""

        path = self._path_for(ticker)
        return self._read(path)

    def delete_history(self, ticker: str) -> None:
        """Delete the local history file for one ticker."""

        path = self._path_for(ticker)

        if path.exists():
            path.unlink()

    def exists(self, ticker: str) -> bool:
        """Return whether a history file exists for the ticker."""

        return self._path_for(ticker).exists()