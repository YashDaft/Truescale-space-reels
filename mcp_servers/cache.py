"""A file cache for API answers, so the same question isn't sent twice.

Each answer is saved as one JSON file holding the URL it came from, the time
it was fetched and the data. That record is also what proves where a fact
came from and when it was checked.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


class Cache:
    def __init__(self, folder: Path, max_age_seconds: float):
        self.folder = Path(folder)
        self.max_age_seconds = max_age_seconds

    def get(self, url: str) -> dict | None:
        """The saved record for `url`, or None if there is none or it's too old."""
        path = self._path(url)
        if not path.exists():
            return None
        record = json.loads(path.read_text())
        age = datetime.now(timezone.utc) - datetime.fromisoformat(record["fetched_at"])
        if age.total_seconds() >= self.max_age_seconds:
            return None
        return record

    def put(self, url: str, data: dict) -> dict:
        """Saves `data` as the answer for `url` and returns the saved record."""
        record = {"url": url, "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "data": data}
        self.folder.mkdir(parents=True, exist_ok=True)
        self._path(url).write_text(json.dumps(record, indent=2))
        return record

    def _path(self, url: str) -> Path:
        # A URL can't be a file name, so the file is named after a hash of it
        return self.folder / f"{hashlib.sha256(url.encode()).hexdigest()[:24]}.json"
