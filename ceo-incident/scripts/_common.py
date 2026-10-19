"""Shared helpers for the ceo-incident scripts: masking of personal data and secrets, time parsing.

Everything these scripts read (logs, commit subjects, notes pasted by people) is untrusted text.
It is treated as data: masked, cut and printed, never executed.
"""
import datetime as dt
import re

MASK = "[oculto]"

# Order matters: the specific patterns run before the generic long-token one.
SENSITIVE = [
    ("chave_privada", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?(?:-----END [A-Z ]*PRIVATE KEY-----|$)", re.S)),
    ("bearer", re.compile(r"(?i)\b(bearer|basic)\s+[A-Za-z0-9._~+/=-]{8,}")),
    ("segredo_kv", re.compile(r"(?i)\b([\w-]*?(?:password|passwd|senha|secret|token|api[_-]?key|access[_-]?key|authorization|cookie|session))(\"?\s*[:=]\s*\"?)[^\s\"',;&]+")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}\b")),
    ("github", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")),
    ("aws", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack", re.compile(r"\bxox[abpors]-[A-Za-z0-9-]{10,}\b")),
    ("sk", re.compile(r"\b(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{10,}\b|\bsk-[A-Za-z0-9_-]{16,}\b")),
    ("url_credencial", re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://)[^\s/:@]+:[^\s/@]+@")),
    ("email", re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")),
    ("cpf", re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|(?<![\d.-])\d{11}(?![\d.-])")),
    ("cnpj", re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b")),
    ("telefone", re.compile(r"(?<![\w.:/-])(?:\+\d{1,3}[\s.-]?)?\(?\d{2}\)?[\s.-]?9?\d{4}[\s.-]?\d{4}(?![\w.:-])")),
    ("ipv4", re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    ("token_longo", re.compile(r"\b(?=[A-Za-z0-9_-]*\d)(?=[A-Za-z0-9_-]*[A-Za-z])[A-Za-z0-9_-]{32,}\b")),
]


def mask(text):
    """Replaces secrets and personal data with [oculto]. Best effort: a human still rereads."""
    text = str(text or "")
    for name, pattern in SENSITIVE:
        if name == "segredo_kv":
            text = pattern.sub(lambda m: m.group(1) + m.group(2) + MASK, text)
        elif name == "url_credencial":
            text = pattern.sub(lambda m: m.group(1) + MASK + "@", text)
        elif name == "bearer":
            text = pattern.sub(lambda m: m.group(1) + " " + MASK, text)
        else:
            text = pattern.sub(MASK, text)
    return text


def cut(text, limit):
    text = " ".join(str(text or "").split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


TZ_RE = re.compile(r"^(Z|[+-]\d{2}:?\d{2})$")
DATETIME_RE = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})(?:[T ](?P<time>\d{2}:\d{2}(?::\d{2})?)(?P<frac>[.,]\d+)?\s?(?P<tz>Z|[+-]\d{2}:?\d{2})?)?"
)


def parse_tz(value):
    """'Z', '+00:00', '-03:00' or '-0300' to a timezone. Raises ValueError otherwise."""
    value = (value or "").strip()
    if not TZ_RE.match(value):
        raise ValueError(f"fuso inválido: {value!r} (use Z ou ±HH:MM)")
    if value == "Z":
        return dt.timezone.utc
    sign = -1 if value[0] == "-" else 1
    digits = value[1:].replace(":", "")
    hours, minutes = int(digits[:2]), int(digits[2:])
    if hours > 14 or minutes > 59:
        raise ValueError(f"fuso inválido: {value!r}")
    return dt.timezone(sign * dt.timedelta(hours=hours, minutes=minutes))


def parse_moment(value, default_tz):
    """Parses 'YYYY-MM-DD', 'YYYY-MM-DD HH:MM[:SS]' or ISO 8601. Naive values use default_tz."""
    value = (value or "").strip()
    match = DATETIME_RE.fullmatch(value)
    if not match:
        raise ValueError(f"data inválida: {value!r} (use AAAA-MM-DD ou AAAA-MM-DDTHH:MM[:SS][±HH:MM])")
    time = match.group("time") or "00:00"
    if len(time) == 5:
        time += ":00"
    moment = dt.datetime.strptime(f"{match.group('date')} {time}", "%Y-%m-%d %H:%M:%S")
    tz = parse_tz(match.group("tz")) if match.group("tz") else default_tz
    return moment.replace(tzinfo=tz)


def safe_arg(value, what):
    """Rejects values that a subprocess could read as an option or that carry control characters."""
    value = str(value or "")
    if not value or value.startswith("-") or any(ord(ch) < 32 for ch in value):
        raise ValueError(f"{what} inválido: não pode ser vazio, começar com '-' nem ter caractere de controle")
    return value
