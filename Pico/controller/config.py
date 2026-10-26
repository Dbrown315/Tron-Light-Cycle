"""Load simple KEY=VALUE settings from settings.env on the Pico."""

DEFAULTS = {
    "DEVICE_NAME": "TRON-P1",
    "SERVICE_UUID": "12345678-1234-5678-1234-56789abcdef0",
    "INPUT_UUID": "12345678-1234-5678-1234-56789abcdef1",
    "GPIO_UP": "0",
    "GPIO_DOWN": "1",
    "GPIO_LEFT": "2",
    "GPIO_RIGHT": "3",
}


def load_settings():
    settings = DEFAULTS.copy()
    try:
        with open("settings.env") as env_file:
            for line in env_file:
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
