"""Load simple KEY=VALUE settings from Pi/settings.env."""

from pathlib import Path

DEFAULTS = {
    "DEVICE_NAME": "TRON-P1",
    "SERVICE_UUID": "12345678-1234-5678-1234-56789abcdef0",
    "INPUT_UUID": "12345678-1234-5678-1234-56789abcdef1",
}


def load_settings():
    settings = DEFAULTS.copy()
    env_path = Path(__file__).with_name("settings.env")
    try:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                key = key.strip()
                if key in settings:
                    settings[key] = value.strip().strip("\"'")
    except OSError:
        pass
    return settings


SETTINGS = load_settings()
