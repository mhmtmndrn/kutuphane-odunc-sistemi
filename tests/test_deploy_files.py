"""Consistency tests for the deployment files and user documents (G19, ADR-0066).

The files under ``deploy/`` repeat the environment variable names, paths and
service settings of ``library_site/settings`` and architecture §6.4. These
tests parse them and compare them with each other, so that a renamed or newly
added variable cannot drift unnoticed until installation (phase 6). Whether
Caddy actually loads the Caddyfile is checked by hand with ``caddy validate``.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPLOY = REPO_ROOT / "deploy"
DOCS = REPO_ROOT / "docs"

CADDY_ONLY_VARS = {"LIBRARY_HOST", "LIBRARY_BIND"}
SECRET_VARS = {"LIBRARY_SECRET_KEY", "LIBRARY_EMAIL_USER", "LIBRARY_EMAIL_PASSWORD"}
PLACEHOLDER = "__DOLDUR__"
APP_COMMAND = "--listen=127.0.0.1:8000 --threads=8 library_site.wsgi:application"
CADDY_VERSION = "2.11.7"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def architecture_vars() -> set[str]:
    """The variable list of architecture §6.4 (the line naming them all)."""
    text = read(DOCS / "architecture.md")
    section = text[text.index("### 6.4") : text.index("## 7.")]
    line = next(ln for ln in section.splitlines() if ln.startswith("`DJANGO_SETTINGS_MODULE`"))
    return set(re.findall(r"`([A-Z_]+)`", line))


def settings_vars() -> set[str]:
    """Every ``env("…")`` name the settings read, plus Django's own variable."""
    names: set[str] = {"DJANGO_SETTINGS_MODULE"}
    for path in (REPO_ROOT / "library_site" / "settings").glob("*.py"):
        names |= set(re.findall(r'\benv\(\s*"([A-Z_]+)"', read(path)))
    return names


def env_file() -> list[str]:
    return read(DEPLOY / "library.env.example").splitlines()


def env_file_values() -> dict[str, str]:
    values: dict[str, str] = {}
    for line in env_file():
        if line and not line.startswith("#"):
            name, _, value = line.partition("=")
            assert name not in values, f"tekrarlanan değişken: {name}"
            values[name] = value
    return values


def winsw(name: str) -> ET.Element:
    return ET.parse(DEPLOY / "winsw" / name).getroot()


def winsw_env(root: ET.Element) -> dict[str, str]:
    values: dict[str, str] = {}
    for element in root.findall("env"):
        name = element.get("name")
        assert name not in values, f"tekrarlanan <env>: {name}"
        values[name] = element.get("value")
    return values


def caddyfile_lines() -> list[str]:
    """Caddyfile lines without comments and surrounding whitespace."""
    lines = []
    for raw in read(DEPLOY / "Caddyfile").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            lines.append(line)
    return lines


def unit(name: str) -> dict[str, list[str]]:
    """A systemd unit as ``key -> [values]`` (sections are not needed here)."""
    entries: dict[str, list[str]] = {}
    for raw in read(DEPLOY / "systemd" / name).splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";", "[")):
            continue
        key, _, value = line.partition("=")
        entries.setdefault(key.strip(), []).append(value.strip())
    return entries


def unit_paths(values: list[str]) -> set[str]:
    """Paths of ``ReadWritePaths=`` lines; a leading ``-`` means "may be missing"."""
    return {path.lstrip("-") for value in values for path in value.split()}


def unit_environment(entries: dict[str, list[str]]) -> dict[str, str]:
    values: dict[str, str] = {}
    for value in entries.get("Environment", []):
        for pair in value.split():
            name, _, val = pair.partition("=")
            values[name] = val
    return values


# --- TC-359 -----------------------------------------------------------------


def test_tc359_settings_read_exactly_the_architecture_variables():
    assert settings_vars() == architecture_vars()
    assert not CADDY_ONLY_VARS & architecture_vars()


# --- TC-360 -----------------------------------------------------------------


def test_tc360_env_example_names_match_architecture_and_caddy_vars():
    assert set(env_file_values()) == architecture_vars() | CADDY_ONLY_VARS


def test_tc360_env_example_every_variable_has_a_comment_line_above():
    lines = env_file()
    for index, line in enumerate(lines):
        if not line or line.startswith("#"):
            continue
        assert re.fullmatch(r"[A-Z_]+=\S*", line), f"geçersiz satır: {line!r}"
        assert index > 0 and lines[index - 1].startswith("# "), f"açıklamasız: {line}"


def test_tc360_env_example_secrets_empty_and_fixed_values():
    values = env_file_values()
    for name in SECRET_VARS:
        assert values[name] == "", name
    assert values["LIBRARY_SCHEDULER_ENABLED"] == "1"
    assert values["DJANGO_SETTINGS_MODULE"] == "library_site.settings.prod"
    # ADR-0061: the address staff type, the bind address and the allowed host
    # are the same static IP.
    assert values["LIBRARY_HOST"] == values["LIBRARY_BIND"] == values["LIBRARY_ALLOWED_HOSTS"]


# --- TC-361 -----------------------------------------------------------------


def assert_common_winsw(root: ET.Element) -> None:
    account = root.find("serviceaccount")
    assert account is not None
    assert account.findtext("user") == "library-svc"
    assert account.findtext("password") == PLACEHOLDER
    assert account.findtext("allowservicelogon") == "true"

    failures = root.findall("onfailure")
    assert [(f.get("action"), f.get("delay")) for f in failures] == [("restart", "10 sec")] * 3
    assert root.findtext("resetfailure") == "1 day"

    log = root.find("log")
    assert log is not None and log.get("mode") == "roll-by-size"
    assert log.findtext("sizeThreshold") == "10240"  # KB, 10 MB
    assert log.findtext("keepFiles") == "8"


def test_tc361_app_service_xml():
    root = winsw("library-app.xml")
    assert root.tag == "service"
    assert root.findtext("id") == "library-app"
    assert root.findtext("executable") == r"C:\Kutuphane\venv\Scripts\waitress-serve.exe"
    assert root.findtext("arguments") == APP_COMMAND
    assert root.findtext("workingdirectory") == r"C:\Kutuphane\app"
    assert_common_winsw(root)
    assert root.find("depend") is None


def test_tc361_app_service_env_names_and_values():
    env = winsw_env(winsw("library-app.xml"))
    assert set(env) == architecture_vars()
    assert env["LIBRARY_SCHEDULER_ENABLED"] == "1"
    assert env["DJANGO_SETTINGS_MODULE"] == "library_site.settings.prod"
    for name in SECRET_VARS | {"LIBRARY_ALLOWED_HOSTS"}:
        assert env[name] == PLACEHOLDER, name


# --- TC-362 -----------------------------------------------------------------


def test_tc362_caddy_service_xml():
    root = winsw("library-caddy.xml")
    assert root.findtext("id") == "library-caddy"
    assert root.findtext("executable") == r"C:\Kutuphane\caddy\caddy.exe"
    assert root.findtext("arguments") == (
        r"run --config C:\Kutuphane\app\deploy\Caddyfile --adapter caddyfile"
    )
    assert_common_winsw(root)
    assert [d.text for d in root.findall("depend")] == ["library-app"]


def test_tc362_caddy_service_env_matches_caddyfile_placeholders():
    env = winsw_env(winsw("library-caddy.xml"))
    placeholders = set(re.findall(r"\{\$([A-Z_]+)\}", read(DEPLOY / "Caddyfile")))
    library_vars = {name for name in env if name.startswith("LIBRARY_")}
    assert library_vars == placeholders == CADDY_ONLY_VARS | {"LIBRARY_STATIC_ROOT"}
    app_env = winsw_env(winsw("library-app.xml"))
    assert env["LIBRARY_STATIC_ROOT"] == app_env["LIBRARY_STATIC_ROOT"]
    # Caddy's data (the local CA key) stays in a fixed folder (ADR-0062).
    assert env["XDG_DATA_HOME"] == r"C:\Kutuphane\caddy"


# --- TC-363 -----------------------------------------------------------------


def test_tc363_caddyfile_required_lines():
    lines = caddyfile_lines()
    assert "{$LIBRARY_HOST} {" in lines
    for required in (
        "bind {$LIBRARY_BIND}",
        "tls internal",
        "handle_path /static/* {",
        "root * {$LIBRARY_STATIC_ROOT}",
        "file_server",
        "reverse_proxy 127.0.0.1:8000",
    ):
        assert required in lines, required


def test_tc363_caddyfile_has_no_log_directive():
    # ADR-0065: no access log, search queries carry member data.
    assert not [line for line in caddyfile_lines() if line.split()[0] == "log"]


# --- TC-364 -----------------------------------------------------------------


@pytest.mark.parametrize("name", ["library-app.service", "library-caddy.service"])
def test_tc364_units_common_lines(name):
    entries = unit(name)
    for key, value in (
        ("User", "library"),
        ("Group", "library"),
        ("EnvironmentFile", "/etc/library/library.env"),
        ("Restart", "on-failure"),
        ("RestartSec", "5"),
        ("NoNewPrivileges", "yes"),
        ("PrivateTmp", "yes"),
        ("ProtectSystem", "strict"),
    ):
        assert entries.get(key) == [value], key


def test_tc364_app_unit():
    entries = unit("library-app.service")
    assert entries["ExecStart"] == [f"/opt/library/venv/bin/waitress-serve {APP_COMMAND}"]
    assert entries["WorkingDirectory"] == ["/opt/library/app"]
    values = env_file_values()
    expected = {
        str(PurePosixPath(values["LIBRARY_DB_PATH"]).parent),
        values["LIBRARY_BACKUP_DIR"],
        values["LIBRARY_EXPORT_DIR"],
    }
    assert unit_paths(entries["ReadWritePaths"]) == expected


def test_tc364_caddy_unit():
    entries = unit("library-caddy.service")
    for key in ("After", "Wants"):
        assert any("library-app.service" in value.split() for value in entries[key]), key
    assert entries["AmbientCapabilities"] == ["CAP_NET_BIND_SERVICE"]
    assert entries["ExecStart"] == [
        "/usr/local/bin/caddy run --config /opt/library/app/deploy/Caddyfile --adapter caddyfile"
    ]
    data_dir = unit_environment(entries)["XDG_DATA_HOME"]
    assert data_dir == "/var/lib/library/caddy"
    assert unit_paths(entries["ReadWritePaths"]) == {data_dir}


# --- TC-365 -----------------------------------------------------------------


def test_tc365_user_guide_notes():
    text = read(DOCS / "kullanim-kilavuzu.md").casefold()
    assert "üyeye adını sor" in text  # ADR-0032
    assert "geçmiş kapalı tarihleri silmeyin" in text  # ADR-0040
    assert "geçmiş tarihli rıza" in text  # ADR-0047


def test_tc365_readme_sections_and_links():
    text = read(REPO_ROOT / "README.md")
    headings = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    for heading in ("Veri kaynakları", "Demo verisi", "Geliştirme ortamı", "Testler", "Belgeler"):
        assert heading in headings, heading
    assert "(docs/kurulum.md)" in text
    assert "(docs/kullanim-kilavuzu.md)" in text
    assert "G19'da eklenecek" not in text


# --- TC-366 -----------------------------------------------------------------


def install_doc() -> str:
    return read(DOCS / "kurulum.md")


def section(text: str, heading: str) -> str:
    start = text.index(f"\n## {heading}\n")
    end = text.find("\n## ", start + 1)
    return text[start : end if end != -1 else len(text)]


def test_tc366_install_doc_has_both_platform_sections():
    headings = re.findall(r"^## (.+)$", install_doc(), flags=re.MULTILINE)
    assert "Windows" in headings and "Linux" in headings  # ADR-0060


def test_tc366_install_doc_seven_steps_and_notes():
    text = install_doc()
    for required in (
        "manage.py migrate",
        "manage.py collectstatic",
        "manage.py createsuperuser",
        "root.crt",
        "certutil -addstore -f Root root.crt",
        "library-app",
        "library-caddy",
        "LIBRARY_BACKUP_DIR",
        "LIBRARY_EXPORT_DIR",
        "w32tm",
        "timedatectl",
        "manage.py restore_backup",
        "pre-restore",
        "KVKK",
        "git archive --format=zip --prefix=library/",
        "DHCP",
        "LocalSubnet",
        "ufw",
        "WinSW-x64.exe",
        "v2.12.0",
    ):
        assert required in text, required
    assert "git clone" not in text  # ADR-0064


def test_tc366_update_procedure_backs_up_before_migrate():
    update = section(install_doc(), "Güncelleme")
    order = [
        update.index("manage.py backup_db"),
        update.index("pip install -r requirements.txt"),
        update.index("manage.py migrate"),
        update.index("manage.py collectstatic"),
    ]
    assert order == sorted(order)


def test_tc366_caddy_download_links_are_pinned():
    versions = re.findall(
        r"github\.com/caddyserver/caddy/releases/download/v(\d+\.\d+\.\d+)/", install_doc()
    )
    assert len(versions) >= 2
    assert set(versions) == {CADDY_VERSION}
