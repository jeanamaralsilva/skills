#!/usr/bin/env python3
"""Finds where an app with a server handles personal data, without ever printing a value.

Usage: python3 pii_scan.py <repo> [<repo> ...] [--json] [--max 15] [--include-tests]

Reads, without writing anything:
- Schemas and models: Ecto (schema and migrations), Prisma, TypeORM, Drizzle, SQL
  (CREATE/ALTER TABLE), TypeScript interfaces and types, zod objects. Each field whose name
  points to personal data becomes a row of the data map, with the category and whether it is
  sensitive (LGPD art. 5, II).
- Log calls (console, Logger, IO.inspect, logger) and calls to analytics, crash and
  engagement SDKs that carry personal data or credentials.
- Storage on the device: AsyncStorage, MMKV without encryptionKey, localStorage and state
  persisted in them, versus SecureStore and Keychain.
- SDKs that collect data, from package.json and mix.exs, matched against data/sdks.csv.
- Account deletion (screen and endpoint), privacy policy link and permissions asked.
- Literal personal data in the code (valid CPF, personal e-mail), reported by type only.

Output: file:line, category and the code identifier (field or key name). Values are never
read into the report. Every finding carries the id of a row in data/checks.csv, with source.
Folders like node_modules, _build, deps and .git are skipped by their path relative to the
repo root. Secret-looking files (.env*, keys, dumps) are never opened.

Exit code: 0 no P1, 1 some P1, 2 bad input or nothing scanned.
"""
import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "data")
SEVERITY_ORDER = {"P1": 0, "P2": 1, "P3": 2}
MAX_FILE_BYTES = 1_000_000
MAX_FILES = 30000

SKIP_DIRS = {
    "node_modules", "_build", "deps", ".git", ".expo", ".next", "dist", "build", "web-build", "coverage",
    "Pods", ".venv", "venv", "__pycache__", ".turbo", ".gradle", "vendor", ".ceo", ".elixir_ls", "cover",
    ".svelte-kit", ".cache", "tmp", ".pytest_cache", "DerivedData",
}
TEST_DIRS = {"test", "tests", "__tests__", "__mocks__", "e2e", "spec", "fixtures", "__fixtures__", "mocks", ".maestro", "stubs"}
TEST_FILE_RE = re.compile(r"\.(test|spec|stories)\.[jt]sx?$|_test\.exs$")
SECRET_FILE_RE = re.compile(
    r"^\.env|\.(pem|key|p8|p12|pfx|keystore|jks|dump|sqlite3?|db|mobileprovision|cer|crt)$|^id_(rsa|ed25519|ecdsa)|credentials",
    re.I,
)
CODE_EXT = (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".ex", ".exs", ".heex", ".eex", ".sql", ".prisma")
CONFIG_FILES = {"package.json", "mix.exs", "app.json", "app.config.ts", "app.config.js", "AndroidManifest.xml", "Info.plist"}
I18N_EXT = (".json",)

# ---------------------------------------------------------------- categories of personal data
# Category id -> (label, sensitive). Matches data/categorias.csv.
CATEGORIES = {
    "nome": ("nome", False), "email": ("e-mail", False), "telefone": ("telefone", False),
    "documento": ("documento (CPF, RG, CNH, passaporte)", False), "nascimento": ("data de nascimento ou idade", False),
    "endereco": ("endereço", False), "localizacao": ("localização (GPS)", False), "ip": ("endereço IP", False),
    "foto": ("foto ou imagem do rosto", False), "aparelho": ("identificador de aparelho ou push", False),
    "genero": ("gênero ou sexo", False), "financeiro": ("dado financeiro (cartão, conta, Pix)", False),
    "saude": ("saúde", True), "biometria": ("biometria", True), "origem_racial": ("origem racial ou étnica", True),
    "religiao": ("convicção religiosa", True), "opiniao_politica": ("opinião política", True),
    "vida_sexual": ("vida ou orientação sexual", True), "genetico": ("dado genético", True),
    "filiacao_sindical": ("filiação a sindicato", True), "credencial": ("credencial (senha, token, sessão)", False),
    "objeto_inteiro": ("objeto inteiro de usuário, params ou body", False),
}
# Joined lowercase names first (more specific), then single tokens. Order is priority.
COMPOUNDS = [
    ("email", {"emailaddress", "useremail", "contactemail"}),
    ("aparelho", {"deviceid", "devicetoken", "pushtoken", "expopushtoken", "fcmtoken", "apnstoken", "apnsdevicetoken",
                  "advertisingid", "installationid", "androidid", "adid", "notificationtoken"}),
    ("credencial", {"accesstoken", "refreshtoken", "idtoken", "authtoken", "sessiontoken", "apikey", "passwordhash",
                    "hashedpassword", "encryptedpassword", "jwt"}),
    ("nome", {"fullname", "firstname", "lastname", "displayname", "username", "givenname", "familyname", "nomecompleto",
              "surname", "sobrenome", "nickname", "apelido", "socialname", "nomesocial"}),
    ("nascimento", {"birthdate", "dateofbirth", "datanascimento", "datadenascimento", "birthday", "birthyear"}),
    ("financeiro", {"cardnumber", "creditcard", "cartaocredito", "numerocartao", "bankaccount", "contabancaria",
                    "chavepix", "pixkey"}),
    ("vida_sexual", {"sexualorientation", "orientacaosexual"}),
    ("ip", {"ipaddress", "remoteip", "lastsigninip", "currentsigninip", "clientip"}),
    ("filiacao_sindical", {"unionmember", "unionmembership"}),
]
TOKENS = [
    ("email", {"email", "mail", "emails"}),
    ("telefone", {"phone", "telefone", "celular", "whatsapp", "cellphone", "phonenumber", "mobilephone", "fone", "tel"}),
    ("documento", {"cpf", "rg", "cnh", "passport", "passaporte", "ssn", "nif", "document", "documento", "taxid"}),
    ("nascimento", {"birth", "birthdate", "dob", "nascimento", "age", "idade", "birthday"}),
    ("endereco", {"address", "endereco", "street", "rua", "logradouro", "cep", "zipcode", "zip", "postal", "postcode",
                  "neighborhood", "bairro", "complemento", "city", "cidade"}),
    ("localizacao", {"latitude", "longitude", "lat", "lng", "lon", "coords", "coordinates", "geolocation", "geo",
                     "location", "localizacao", "geopoint", "gps"}),
    ("ip", {"ip"}),
    ("foto", {"avatar", "photo", "picture", "foto", "selfie"}),
    ("aparelho", {"idfa", "idfv", "gaid"}),
    ("genero", {"gender", "genero", "sexo", "sex", "pronoun", "pronouns"}),
    ("financeiro", {"iban", "cvv", "cvc", "pix"}),
    ("saude", {"health", "saude", "medical", "diagnosis", "diagnostico", "disease", "doenca", "allergy", "allergies",
               "alergia", "alergias", "blood", "sangue", "symptom", "symptoms", "sintoma", "sintomas", "medication",
               "medications", "medicamento", "medicamentos", "pregnancy", "gravidez", "gestante", "disability",
               "deficiencia", "cid"}),
    ("biometria", {"biometric", "biometrics", "biometria", "faceprint", "facial"}),
    ("origem_racial", {"race", "raca", "ethnicity", "etnia"}),
    ("religiao", {"religion", "religiao", "religious", "religiosa"}),
    ("opiniao_politica", {"political", "politico", "politica_partidaria"}),
    ("genetico", {"genetic", "genetico", "dna", "genome"}),
    ("filiacao_sindical", {"sindicato", "sindical"}),
    ("credencial", {"password", "senha", "token", "secret", "jwt", "otp", "pin", "credential", "credentials",
                    "cookie", "session", "authorization", "passcode"}),
]
# A token in the name that turns it into metadata, not the data itself (email_verified, location_id).
NEGATIVE = {
    "verified", "confirmed", "confirmation", "enabled", "sent", "template", "subject", "notification", "notifications",
    "provider", "type", "status", "count", "label", "placeholder", "error", "errors", "valid", "invalid", "required",
    "format", "regex", "pattern", "mask", "visible", "visibility", "opt", "optin", "optout", "preference", "preferences",
    "permission", "permissions", "granted", "accuracy", "precision", "max", "min", "cache", "ttl", "id", "ids", "key",
    "input", "field", "ref", "style", "styles", "icon", "color", "size", "width", "height", "modal", "screen", "button",
    "loading", "changed", "updated", "expires", "expiry", "expired", "length", "strength", "policy", "settings",
    "service", "services", "mode", "query", "range", "filter", "sort", "on", "off", "is", "has", "should", "can",
}
KEEP_WITH_ID = {"aparelho"}
PERSON_CONTEXT = {
    "user", "users", "usuario", "usuarios", "profile", "profiles", "perfil", "perfis", "customer", "customers",
    "cliente", "clientes", "client", "clients", "member", "members", "membro", "membros", "account", "accounts",
    "conta", "contas", "person", "people", "pessoa", "pessoas", "contact", "contacts", "contato", "contatos",
    "patient", "patients", "paciente", "pacientes", "employee", "employees", "funcionario", "funcionarios",
    "driver", "drivers", "motorista", "motoristas", "student", "students", "aluno", "alunos", "guardian",
    "responsavel", "owner", "owners", "lead", "leads", "professional", "professionals", "profissional",
    "teacher", "teachers", "professor", "professores", "dependent", "dependente", "child", "children", "kid", "kids",
    "learner", "learners", "subscriber", "subscribers", "candidate", "candidates", "candidato", "tutor",
}
CAMEL_RE = re.compile(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+")


def split_name(name):
    parts = []
    for chunk in re.split(r"[_\-\s.]+", name or ""):
        parts.extend(p.lower() for p in CAMEL_RE.findall(chunk))
    return parts


def classify(name, context_words=()):
    """Returns the category id for an identifier, or None. Context words are table/model/object names."""
    tokens = split_name(name)
    if not tokens:
        return None
    joined = "".join(tokens)
    for category, names in COMPOUNDS:
        if joined in names or any(joined.endswith(n) and len(n) > 6 for n in names):
            if NEGATIVE.intersection(tokens[1:]) - {"id"} and category not in KEEP_WITH_ID:
                return None
            return category
    for category, names in TOKENS:  # sensitive data stays sensitive even as status, type or foreign key
        if CATEGORIES[category][1] and names.intersection(tokens):
            return category
    if NEGATIVE.intersection(tokens):
        return None
    for category, names in TOKENS:  # the last word names the data: address_lat is a coordinate
        if tokens[-1] in names:
            return category
    for category, names in TOKENS:
        if names.intersection(tokens):
            return category
    if tokens in (["name"], ["nome"]) and any(set(split_name(w)) & PERSON_CONTEXT for w in context_words):
        return "nome"
    return None


# ---------------------------------------------------------------- helpers
STRING_RE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`', re.S)
INTERP_RE = re.compile(r"#\{([^}]*)\}|\$\{([^}]*)\}")
IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def code_only(text):
    """Drops string literals but keeps what is interpolated inside them (#{...}, ${...})."""
    def keep(match):
        return " ".join(a or b for a, b in INTERP_RE.findall(match.group(0)))
    return STRING_RE.sub(keep, text)


def call_args(lines, index, start):
    """Text of a call from `start` in lines[index] to the closing paren, up to 8 lines. No parens: rest of line."""
    text = lines[index][start:]
    stripped = text.lstrip()
    if not stripped.startswith("("):
        return text
    depth, out = 0, []
    for offset in range(0, 8):
        if index + offset >= len(lines):
            break
        chunk = text if offset == 0 else lines[index + offset]
        for ch in chunk:
            out.append(ch)
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    return "".join(out)
        out.append("\n")
    return "".join(out)


def categories_in(text, context=()):
    found = []
    for ident in IDENT_RE.findall(text):
        category = classify(ident, context)
        if category and category not in found:
            found.append(category)
    return found


def rel(root, path):
    return os.path.relpath(path, root).replace(os.sep, "/")


def load_csv(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


# ---------------------------------------------------------------- schema parsers
ECTO_SCHEMA_RE = re.compile(r'^\s*schema\s+"(\w+)"')
ECTO_TABLE_RE = re.compile(r"^\s*(?:create|alter)(?:_if_not_exists)?\s+table\(\s*:?\"?(\w+)")
ECTO_MODULE_RE = re.compile(r"^\s*defmodule\s+([\w.]+)")
ECTO_FIELD_RE = re.compile(r"^\s*(?:field|add|add_if_not_exists|modify)\s*\(?\s*:(\w+)\s*,\s*([^\n]*)")
PRISMA_MODEL_RE = re.compile(r"^\s*model\s+(\w+)\s*\{")
PRISMA_FIELD_RE = re.compile(r"^\s*(\w+)\s+[A-Z]\w*[\[\]?]*")
SQL_CREATE_RE = re.compile(r"create\s+table\s+(?:if\s+not\s+exists\s+)?(?:[\w\"]+\.)?\"?(\w+)\"?\s*\(", re.I)
SQL_COLUMN_RE = re.compile(r"^\s*\"?(\w+)\"?\s+(?:[a-z]+)", re.I)
SQL_ALTER_RE = re.compile(r"alter\s+table\s+(?:only\s+)?(?:if\s+exists\s+)?(?:[\w\"]+\.)?\"?(\w+)\"?\s+add\s+(?:column\s+)?(?:if\s+not\s+exists\s+)?\"?(\w+)\"?", re.I)
SQL_NOT_COLUMN = {"constraint", "primary", "foreign", "unique", "check", "references", "exclude", "like", "index", "key"}
TS_BLOCK_RE = re.compile(r"^\s*(?:export\s+)?(?:declare\s+)?(?:interface\s+(\w+)|type\s+(\w+)\s*=\s*\{|class\s+(\w+))")
TS_PROP_RE = re.compile(r"^\s*(?:readonly\s+|public\s+|private\s+|protected\s+)*[\"']?(\w+)[\"']?\s*[?!]?\s*:\s*\S")
ZOD_PROP_RE = re.compile(r"^\s*[\"']?(\w+)[\"']?\s*:\s*z\.")
DRIZZLE_TABLE_RE = re.compile(r"(?:pg|mysql|sqlite)Table\(\s*[\"'](\w+)")
DRIZZLE_FIELD_RE = re.compile(r"^\s*(\w+)\s*:\s*(?:text|varchar|char|integer|int|bigint|smallint|timestamp|date|boolean|uuid|json|jsonb|real|doublePrecision|numeric|decimal|serial|point|geometry|inet)\s*\(")
ENTITY_RE = re.compile(r"@Entity\s*\(")
COLUMN_DECORATOR_RE = re.compile(r"@(?:Column|PrimaryColumn|PrimaryGeneratedColumn|CreateDateColumn|UpdateDateColumn)\b")


def schema_fields(path, lines):
    """Yields (line_number, origin, context, field) for every field-like declaration."""
    name = os.path.basename(path)
    if name.endswith((".ex", ".exs")):
        context = ""
        for number, line in enumerate(lines, 1):
            for pattern in (ECTO_SCHEMA_RE, ECTO_TABLE_RE):
                found = pattern.match(line)
                if found:
                    context = found.group(1)
            module = ECTO_MODULE_RE.match(line)
            if module and not context:
                context = module.group(1).split(".")[-1]
            field = ECTO_FIELD_RE.match(line)
            if field and context:
                origin = "ecto_migration" if "migrations" in path.replace(os.sep, "/") else "ecto_schema"
                yield number, origin, context, field.group(1), "redact: true" in field.group(2)
        return
    if name.endswith(".prisma"):
        context = ""
        for number, line in enumerate(lines, 1):
            model = PRISMA_MODEL_RE.match(line)
            if model:
                context = model.group(1)
                continue
            if line.strip().startswith("}"):
                context = ""
            field = PRISMA_FIELD_RE.match(line)
            if field and context and not line.strip().startswith(("//", "@@")):
                yield number, "prisma", context, field.group(1), False
        return
    if name.endswith(".sql"):
        context = ""
        for number, line in enumerate(lines, 1):
            create = SQL_CREATE_RE.search(line)
            if create:
                context = create.group(1)
                tail = line[create.end():]
                column = SQL_COLUMN_RE.match(tail)
                if column and column.group(1).lower() not in SQL_NOT_COLUMN:
                    yield number, "sql", context, column.group(1), False
                continue
            for alter in SQL_ALTER_RE.finditer(line):
                if alter.group(2).lower() not in SQL_NOT_COLUMN:
                    yield number, "sql", alter.group(1), alter.group(2), False
            if context:
                if re.match(r"^\s*\)\s*;?", line):
                    context = ""
                    continue
                column = SQL_COLUMN_RE.match(line)
                if column and column.group(1).lower() not in SQL_NOT_COLUMN and not line.strip().startswith("--"):
                    yield number, "sql", context, column.group(1), False
        return
    if not name.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs")):
        return
    is_entity = any(ENTITY_RE.search(l) for l in lines)
    block, depth, table, last_decorator = "", 0, "", -10
    for number, line in enumerate(lines, 1):
        drizzle = DRIZZLE_TABLE_RE.search(line)
        if drizzle:
            table = drizzle.group(1)
        field = DRIZZLE_FIELD_RE.match(line)
        if field and table:
            yield number, "drizzle", table, field.group(1), False
            continue
        if COLUMN_DECORATOR_RE.search(line):
            last_decorator = number
        zod = ZOD_PROP_RE.match(line)
        if zod:
            yield number, "zod", block or "objeto", zod.group(1), False
            continue
        start = TS_BLOCK_RE.match(line)
        if start and depth == 0:
            block = start.group(1) or start.group(2) or start.group(3)
            depth = line.count("{") - line.count("}")
            if depth <= 0:
                depth = 1 if "{" not in line else 0
                if depth == 0:
                    block = ""
            continue
        if block:
            if depth == 1:
                prop = TS_PROP_RE.match(line)
                if prop and "(" not in line.split(":", 1)[0]:
                    if is_entity:
                        if number - last_decorator <= 3:
                            yield number, "typeorm", block, prop.group(1), False
                    else:
                        yield number, "tipo_ts", block, prop.group(1), False
            depth += line.count("{") - line.count("}")
            if depth <= 0:
                block, depth = "", 0


# ---------------------------------------------------------------- call detectors
LOG_CALL_RE = re.compile(
    r"\b(console\.(?:log|info|warn|error|debug|trace)|Logger\.(?:debug|info|notice|warning|warn|error|critical|alert)"
    r"|IO\.inspect|logger\.(?:debug|info|warn|warning|error|fatal|trace|log)|log\.(?:debug|info|warn|error))\b"
)
THIRD_CALL_RE = re.compile(
    r"\b(Sentry\.(?:captureMessage|captureException|setUser|setContext|setExtra|setExtras|setTag|setTags|addBreadcrumb)"
    r"|analytics\(\)\.(?:logEvent|setUserProperties|setUserProperty|setUserId)"
    r"|crashlytics\(\)\.(?:log|setAttribute|setAttributes|setUserId|recordError)"
    r"|(?:posthog|mixpanel|amplitude|Amplitude|segment|analytics|Analytics|rudder\w*|braze|Braze|appsFlyer|appsflyer"
    r"|OneSignal|Intercom|Bugsnag|DdLogs|datadogRum)\.\w+"
    r"|\blogEvent|setUserProperties|setUserProperty|setUserId)\b"
)
WHOLE_OBJECT_RE = re.compile(
    r"(?<![\w.])(user|usuario|currentUser|current_user|profile|perfil|customer|cliente|session|params|body|payload|"
    r"conn\.params|req\.body|request\.body|ctx\.request\.body|account|attrs|form|formData|values|credentials)(?![\w.\[?])"
)
STORAGE_SET_RE = re.compile(
    r"\b(AsyncStorage\.(?:setItem|multiSet|mergeItem)|localStorage\.setItem|sessionStorage\.setItem"
    r"|\w*(?:storage|Storage|mmkv|MMKV)\.set(?:String|Item)?)\s*\("
)
SECURE_RE = re.compile(r"\b(SecureStore\.(?:setItemAsync|setItem)|Keychain\.set\w+|EncryptedStorage\.setItem|setGenericPassword)\b")
PERSIST_RE = re.compile(r"storage\s*:\s*AsyncStorage\b|createJSONStorage\(\s*\(\)\s*=>\s*AsyncStorage\b|storage\s*:\s*(?:localStorage|mmkvStorage|\w*MMKV\w*)\b")
MMKV_NEW_RE = re.compile(r"new\s+MMKV\s*\(|createMMKV\s*\(")
SUPABASE_RE = re.compile(r"\bcreateClient\s*\(")
STORAGE_KEY_EXTRA = {"user", "profile", "perfil", "usuario", "account", "conta", "customer", "cliente"}

AUTH_RE = re.compile(
    r"\b(signUp|sign_up|signup|registerUser|register_user|createUser|create_user|createAccount|create_account|"
    r"signInWith\w+|GoogleSignin|AppleAuthentication|registration_changeset|register_changeset|cadastrar\w*|"
    r"signInWithPassword|signInWithOtp|getSession|generate_user_session_token|log_in_user)\b"
)
DELETE_TEXT_RE = re.compile(
    r"(excluir|deletar|apagar|encerrar|remover|eliminar)\s+(a\s+|minha\s+|sua\s+|mi\s+)?(conta|cuenta)"
    r"|\b(delete|close|remove)\s+(my\s+|your\s+|the\s+)?account", re.I
)
DELETE_CODE_RE = re.compile(
    r"\b(deleteAccount|delete_account|deleteMyAccount|delete_my_account|deleteUser|delete_user|deleteMe|delete_me|"
    r"removeAccount|remove_account|excluirConta|excluir_conta|destroyAccount|destroy_account|anonymizeUser|"
    r"anonymize_user|accountDeletion|account_deletion|requestAccountDeletion|request_account_deletion|"
    r"auth\.admin\.deleteUser)\b"
)
DELETE_ROUTE_RE = re.compile(
    r"\b(?:delete|\.delete)\s*\(?\s*[\"'][^\"']*/(?:account|accounts|me|users?/me|user|conta|minha-conta|profile|perfil)/?[\"']", re.I
)
POLICY_RE = re.compile(r"pol[ií]tica\s+de\s+privacidade|privacy\s*policy|privacy-policy|/privacidade\b|/privacy\b", re.I)
EMAIL_LITERAL_RE = re.compile(r"(?<![\w.+-])([A-Za-z0-9._%+-]+)@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+)")
CPF_LITERAL_RE = re.compile(r"(?<![\d.-])(\d{3}\.?\d{3}\.?\d{3}-?\d{2})(?![\d.-])")
GENERIC_LOCAL = {
    "noreply", "no-reply", "naoresponda", "nao-responda", "support", "suporte", "contato", "contact", "hello", "oi",
    "ola", "admin", "team", "time", "info", "privacy", "privacidade", "dpo", "encarregado", "help", "ajuda", "sac",
    "financeiro", "vendas", "sales", "billing", "security", "seguranca", "legal", "juridico", "dev", "devs", "test",
    "teste", "user", "usuario", "email", "foo", "bar", "name", "nome", "you", "voce", "seu", "seuemail", "your",
    "youremail", "exemplo", "example", "ops", "app", "apps", "mail", "postmaster", "webmaster", "abuse", "feedback",
    "atendimento", "ouvidoria", "comercial", "marketing", "news", "newsletter", "notifications", "notificacoes",
}
GENERIC_DOMAIN_RE = re.compile(
    r"(^|\.)(example\.(com|org|net)|exemplo\.com(\.br)?|test|invalid|localhost|local|email\.com|domain\.com|"
    r"dominio\.com(\.br)?|sentry\.io|ingest\.sentry\.io|[\w-]*\.ingest\.\w+\.sentry\.io|users\.noreply\.github\.com|"
    r"expo\.dev|expo\.io|2x|3x|\d+x)$", re.I
)
PERMISSION_RE = re.compile(r"\b(NS\w+UsageDescription)\b|android\.permission\.([A-Z_]+)")
PERMISSION_DATA = {
    "Location": "localizacao", "LOCATION": "localizacao", "Camera": "foto", "CAMERA": "foto", "PhotoLibrary": "foto",
    "READ_MEDIA_IMAGES": "foto", "Contacts": "contatos", "CONTACTS": "contatos", "Microphone": "audio",
    "RECORD_AUDIO": "audio", "Calendars": "calendario", "CALENDAR": "calendario", "FaceID": "biometria",
    "UserTracking": "rastreamento", "Health": "saude", "BODY_SENSORS": "saude", "Motion": "movimento",
    "ACTIVITY_RECOGNITION": "movimento", "Bluetooth": "bluetooth", "SMS": "sms", "CALL_LOG": "chamadas",
    "PHONE_STATE": "telefone", "SpeechRecognition": "audio",
}


def cpf_valid(digits):
    digits = re.sub(r"\D", "", digits)
    if len(digits) != 11 or digits == digits[0] * 11:
        return False
    for size in (9, 10):
        total = sum(int(d) * w for d, w in zip(digits[:size], range(size + 1, 1, -1)))
        check = (total * 10) % 11 % 10
        if check != int(digits[size]):
            return False
    return True


# ---------------------------------------------------------------- scanner
class Scanner:
    def __init__(self, repos, include_tests=False):
        self.repos = repos
        self.include_tests = include_tests
        self.files = 0
        self.read_by_repo = {}
        self.cut_at = None
        self.findings = []
        self.map = {}
        self.sdks = []
        self.permissions = {}
        self.deletion = {}
        self.secure_uses = 0
        self.checks = {row["id"]: row for row in load_csv("checks.csv")}
        self.sdk_rows = load_csv("sdks.csv")

    def add(self, check, repo, path, line, category, detail):
        self.findings.append({
            "id": check, "severidade": self.checks.get(check, {}).get("severidade", "P2"),
            "repo": os.path.basename(os.path.abspath(repo)), "arquivo": rel(repo, path), "linha": line,
            "categoria": category, "sensivel": CATEGORIES.get(category, ("", False))[1], "detalhe": detail,
            "source": self.checks.get(check, {}).get("source", ""),
        })

    def walk(self, root):
        for current, dirs, files in os.walk(root):
            relative = os.path.relpath(current, root)
            parts = [] if relative == "." else relative.split(os.sep)
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not os.path.islink(os.path.join(current, d))
                             and (self.include_tests or d not in TEST_DIRS))
            if parts and parts[0] in ("ios", "android") and len(parts) > 1 and parts[1] in ("build", "Pods"):
                continue
            for name in sorted(files):
                path = os.path.join(current, name)
                if os.path.islink(path) or SECRET_FILE_RE.search(name):
                    continue
                if not self.include_tests and TEST_FILE_RE.search(name):
                    continue
                if name.endswith(".min.js") or name.endswith(".d.ts") and "node_modules" in path:
                    continue
                if name.endswith(CODE_EXT) or name in CONFIG_FILES or (name.endswith(I18N_EXT) and "locale" in path.lower()
                                                                      or name.endswith(I18N_EXT) and "i18n" in path.lower()):
                    yield path

    def read(self, path):
        try:
            if os.path.getsize(path) > MAX_FILE_BYTES:
                return None
            with open(path, encoding="utf-8", errors="replace") as handle:
                return handle.read()
        except OSError:
            return None

    def run(self):
        for repo in self.repos:
            state = {"auth": [], "ui": [], "code": [], "route": [], "policy": [], "mobile": False, "server": False}
            name = os.path.basename(os.path.abspath(repo))
            self.read_by_repo[name] = 0
            complete = True
            for path in self.walk(repo):
                if self.files >= MAX_FILES:
                    self.cut_at = self.cut_at or name
                    complete = False
                    break
                text = self.read(path)
                if text is None:
                    continue
                self.files += 1
                self.read_by_repo[name] += 1
                self.scan_file(repo, path, text, state)
            self.deletion[name] = state
            # "Not found" only means something after a full read; a cut or unread repo is never judged.
            if complete and self.read_by_repo[name]:
                self.judge_deletion(repo, state)
        return self

    def scan_file(self, repo, path, text, state):
        name = os.path.basename(path)
        lines = text.splitlines()
        if name == "package.json":
            self.scan_package(repo, path, text, state)
            return
        if name == "mix.exs":
            self.scan_mix(repo, path, lines, state)
        if name in ("app.json", "app.config.ts", "app.config.js", "AndroidManifest.xml", "Info.plist"):
            self.scan_permissions(repo, path, lines)
            if name.endswith(".json") or name.endswith(".xml") or name.endswith(".plist"):
                return
        if name.endswith(I18N_EXT):
            self.scan_signals(repo, path, lines, state, text_only=True)
            return
        for number, origin, context, field, redacted in schema_fields(path, lines):
            category = classify(field, (context,))
            if not category or (category == "credencial" and origin in ("tipo_ts", "zod")):
                continue
            key = (category, origin, context.lower(), field.lower())
            entry = self.map.setdefault(key, {"categoria": category, "origem": origin, "contexto": context, "campo": field,
                                              "sensivel": CATEGORIES[category][1], "redact": redacted, "locais": []})
            entry["locais"].append(f"{os.path.basename(os.path.abspath(repo))}/{rel(repo, path)}:{number}")
        if name.endswith((".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".ex", ".exs", ".heex", ".eex")):
            self.scan_calls(repo, path, lines)
            self.scan_storage(repo, path, text, lines)
            self.scan_signals(repo, path, lines, state)
            self.scan_literals(repo, path, lines)

    def scan_calls(self, repo, path, lines):
        for number, line in enumerate(lines, 1):
            stripped = line.lstrip()
            if stripped.startswith(("//", "#", "*", "/*")):
                continue
            dev_only = any("__DEV__" in l for l in lines[max(0, number - 3):number])
            for pattern, check in ((THIRD_CALL_RE, "PRV-TER"), (LOG_CALL_RE, "PRV-LOG")):
                match = pattern.search(line)
                if not match or (dev_only and check == "PRV-LOG"):
                    continue
                args = code_only(call_args(lines, number - 1, match.end()))
                categories = categories_in(args, ("user",))
                if check == "PRV-LOG" and not categories and WHOLE_OBJECT_RE.search(args):
                    self.add("PRV-LOG", repo, path, number, "objeto_inteiro",
                             f"{match.group(1)} recebe um objeto inteiro (usuário, params ou body)")
                    break
                if categories:
                    labels = ", ".join(categories)
                    if check == "PRV-TER":
                        self.add(check, repo, path, number, categories[0], f"{match.group(1)} envia: {labels}")
                    else:
                        cred = "credencial" in categories
                        self.add("PRV-LOGCRED" if cred else check, repo, path, number,
                                 "credencial" if cred else categories[0], f"{match.group(1)} registra: {labels}")
                    break

    def scan_storage(self, repo, path, text, lines):
        if not re.search(r"AsyncStorage|localStorage|sessionStorage|MMKV|mmkv|SecureStore|Keychain|EncryptedStorage", text):
            return
        encrypted_mmkv = bool(MMKV_NEW_RE.search(text) and "encryptionKey" in text)
        uses_insecure = bool(re.search(r"AsyncStorage|localStorage|sessionStorage", text)) or (
            bool(re.search(r"MMKV|mmkv", text)) and not encrypted_mmkv)
        instances = re.findall(r"(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(?:new\s+MMKV|createMMKV)\s*\(", text)
        instance_re = re.compile(r"\b((?:%s)\.set(?:String)?)\s*\(" % "|".join(map(re.escape, instances))) if instances else None
        for number, line in enumerate(lines, 1):
            if line.lstrip().startswith(("//", "*")):
                continue
            if SECURE_RE.search(line):
                self.secure_uses += 1
                continue
            match = STORAGE_SET_RE.search(line) or (instance_re.search(line) if instance_re else None)
            if match and uses_insecure:
                if encrypted_mmkv and ("mmkv" in match.group(1).lower() or (instance_re and instance_re.match(match.group(0)))):
                    continue
                args = call_args(lines, number - 1, match.end() - 1)
                found = categories_in(args.replace("'", " ").replace('"', " ").replace("`", " "), ("user",))
                words = [split_name(w) for w in IDENT_RE.findall(args)]
                if not found and any("auth" in w for w in words):
                    found = ["credencial"]
                elif not found and any(w and w[-1] in STORAGE_KEY_EXTRA for w in words):
                    found = ["objeto_inteiro"]
                if found:
                    check = "PRV-ARM" if found[0] in ("credencial", "documento", "financeiro") or CATEGORIES.get(found[0], ("", False))[1] else "PRV-ARM2"
                    self.add(check, repo, path, number, found[0],
                             f"{match.group(1)} sem criptografia guarda: {', '.join(found)}")
            persist = PERSIST_RE.search(line)
            if persist:
                if SUPABASE_RE.search(text):
                    self.add("PRV-ARM", repo, path, number, "credencial",
                             "sessão de login (tokens) persistida em armazenamento sem criptografia")
                else:
                    found = [c for c in categories_in(code_only(text), ("user",)) if c != "aparelho"]
                    if found:
                        check = "PRV-ARM" if "credencial" in found else "PRV-ARM2"
                        self.add(check, repo, path, number, "credencial" if "credencial" in found else found[0],
                                 f"estado persistido sem criptografia contém: {', '.join(found[:4])}")

    def scan_signals(self, repo, path, lines, state, text_only=False):
        where = f"{os.path.basename(os.path.abspath(repo))}/{rel(repo, path)}"
        for number, line in enumerate(lines, 1):
            if DELETE_TEXT_RE.search(line):
                state["ui"].append(f"{where}:{number}")
            if POLICY_RE.search(line):
                state["policy"].append(f"{where}:{number}")
            if text_only:
                continue
            if AUTH_RE.search(line):
                state["auth"].append(f"{where}:{number}")
            if DELETE_CODE_RE.search(line):
                state["code"].append(f"{where}:{number}")
            if DELETE_ROUTE_RE.search(line):
                state["route"].append(f"{where}:{number}")

    def scan_literals(self, repo, path, lines):
        for number, line in enumerate(lines, 1):
            for match in EMAIL_LITERAL_RE.finditer(line):
                local, domain = match.group(1).lower(), match.group(2).lower()
                if local in GENERIC_LOCAL or GENERIC_DOMAIN_RE.search(domain) or local.startswith(("noreply", "no-reply")):
                    continue
                if "%" in local or "{" in line[max(0, match.start() - 2):match.start()]:
                    continue
                self.add("PRV-LIT", repo, path, number, "email", "e-mail escrito no código (valor não exibido)")
            for match in CPF_LITERAL_RE.finditer(line):
                if cpf_valid(match.group(1)):
                    self.add("PRV-LIT", repo, path, number, "documento", "CPF válido escrito no código (valor não exibido)")

    def scan_permissions(self, repo, path, lines):
        for number, line in enumerate(lines, 1):
            for match in PERMISSION_RE.finditer(line):
                permission = match.group(1) or match.group(2)
                data = next((v for k, v in PERMISSION_DATA.items() if k in permission), "outro")
                self.permissions.setdefault(permission, {"dado": data, "local": f"{os.path.basename(os.path.abspath(repo))}/{rel(repo, path)}:{number}"})

    def scan_package(self, repo, path, text, state):
        try:
            package = json.loads(text)
        except ValueError:
            return
        if not isinstance(package, dict):
            return
        deps = {}
        for field in ("dependencies", "optionalDependencies"):
            if isinstance(package.get(field), dict):
                deps.update(package[field])
        if any(k in deps for k in ("expo", "react-native")):
            state["mobile"] = True
        if any(k in deps for k in ("express", "fastify", "@nestjs/core", "koa", "hono", "@prisma/client", "next")):
            state["server"] = True
        self.match_sdks(repo, path, deps.keys(), "npm")

    def scan_mix(self, repo, path, lines, state):
        state["server"] = True
        names = []
        for line in lines:
            names.extend(re.findall(r"\{\s*:(\w+)\s*,", line))
        self.match_sdks(repo, path, names, "hex")

    def match_sdks(self, repo, path, names, ecosystem):
        for row in self.sdk_rows:
            if row.get("ecossistema") != ecosystem:
                continue
            pattern = row["pacote"]
            for name in names:
                if name == pattern or (pattern.endswith("*") and name.startswith(pattern[:-1])):
                    self.sdks.append({"pacote": name, "fornecedor": row["fornecedor"], "categoria": row["categoria"],
                                      "coleta": row["coleta"], "reduzir": row["como_reduzir"], "source": row["source"],
                                      "local": f"{os.path.basename(os.path.abspath(repo))}/{rel(repo, path)}"})

    def judge_deletion(self, repo, state):
        name = os.path.basename(os.path.abspath(repo))
        if not state["auth"]:
            return
        backend = state["code"] + state["route"]
        if state["mobile"] and not state["ui"] and not state["code"]:
            self.findings.append(self._repo_finding("PRV-CTA", name, "app tem conta, mas não achei caminho de excluir conta no app"))
        if state["server"] and not backend:
            self.findings.append(self._repo_finding("PRV-CTA2", name, "servidor tem conta, mas não achei endpoint ou função de exclusão"))
        if state["mobile"] and not state["policy"]:
            self.findings.append(self._repo_finding("PRV-POL", name, "não achei link para a política de privacidade no app"))

    def _repo_finding(self, check, repo_name, detail):
        row = self.checks.get(check, {})
        return {"id": check, "severidade": row.get("severidade", "P2"), "repo": repo_name, "arquivo": "", "linha": 0,
                "categoria": "conta" if check.startswith("PRV-CTA") else "politica", "sensivel": False,
                "detalhe": detail, "source": row.get("source", "")}

    def result(self):
        findings = sorted(self.findings, key=lambda f: (SEVERITY_ORDER.get(f["severidade"], 9), f["id"], f["repo"], f["arquivo"], f["linha"]))
        data_map = sorted(self.map.values(), key=lambda e: (not e["sensivel"], e["categoria"], e["origem"], e["contexto"]))
        deletion = {repo: {"tem_conta": bool(s["auth"]), "tela": s["ui"][:5], "codigo": (s["code"] + s["route"])[:5],
                           "politica_no_app": s["policy"][:3], "app_mobile": s["mobile"], "servidor": s["server"]}
                    for repo, s in self.deletion.items()}
        return {"repos": [os.path.basename(os.path.abspath(r)) for r in self.repos], "arquivos": self.files,
                "por_repo": self.read_by_repo, "cortado_em": self.cut_at,
                "nao_varridos": [repo for repo, count in self.read_by_repo.items() if count == 0],
                "achados": findings, "mapa": data_map, "sdks": self.sdks, "exclusao_conta": deletion,
                "permissoes": self.permissions, "armazenamento_seguro_usos": self.secure_uses}


def render(result, limit):
    out = [f"pii_scan: {', '.join(result['repos'])} | {result['arquivos']} arquivos lidos",
           "Valores nunca são exibidos: só arquivo:linha, categoria e nome do campo ou da chave."]
    if result["cortado_em"]:
        out.append(f"AVISO: varredura cortada no limite de {MAX_FILES} arquivos, no repo {result['cortado_em']};"
                   " o resto não foi lido e a exclusão de conta não foi julgada ali nem depois.")
    for repo in result["nao_varridos"]:
        out.append(f"AVISO: repo {repo} não varrido (0 arquivos lidos); ausência de achado ali não prova nada.")
    findings = result["achados"]
    out.append(f"\n## Achados ({len(findings)})")
    if not findings:
        out.append("Nenhum achado automático. Não verificado não é ok: veja o checklist manual.")
    groups = {}
    for finding in findings:
        groups.setdefault((finding["severidade"], finding["id"], finding["categoria"]), []).append(finding)
    for (severity, check, category), items in groups.items():
        sens = " SENSÍVEL" if CATEGORIES.get(category, ("", False))[1] else ""
        out.append(f"- {severity} [{check}] {category}{sens}: {len(items)} | {items[0]['detalhe']} [fonte: {items[0]['source']}]")
        for item in items[:limit]:
            if item["arquivo"]:
                out.append(f"    {item['repo']}/{item['arquivo']}:{item['linha']}")
        if len(items) > limit:
            out.append(f"    ... +{len(items) - limit}")
    out.append(f"\n## Mapa de dados pessoais em schemas e tipos ({len(result['mapa'])} campos)")
    by_category = {}
    for entry in result["mapa"]:
        by_category.setdefault(entry["categoria"], []).append(entry)
    for category, entries in sorted(by_category.items(), key=lambda kv: (not CATEGORIES[kv[0]][1], kv[0])):
        sens = " (SENSÍVEL, LGPD art. 11)" if CATEGORIES[category][1] else ""
        out.append(f"- {CATEGORIES[category][0]}{sens}: {len(entries)}")
        for entry in entries[:limit]:
            redact = " redact" if entry["redact"] else ""
            out.append(f"    {entry['contexto']}.{entry['campo']} [{entry['origem']}{redact}] {entry['locais'][0]}")
        if len(entries) > limit:
            out.append(f"    ... +{len(entries) - limit}")
    out.append(f"\n## SDKs e libs que tocam dado pessoal ({len(result['sdks'])})")
    for sdk in result["sdks"]:
        out.append(f"- {sdk['pacote']} ({sdk['fornecedor']}, {sdk['categoria']}): {sdk['coleta']} | reduzir: {sdk['reduzir']} [fonte: {sdk['source']}]")
    out.append("\n## Exclusão de conta e política")
    for repo, state in result["exclusao_conta"].items():
        kind = "app" if state["app_mobile"] else ("servidor" if state["servidor"] else "repo")
        if repo in result["nao_varridos"] or repo == result["cortado_em"]:
            out.append(f"- {repo}: NÃO VERIFICADO (repo não lido por inteiro; nada foi julgado)")
            continue
        out.append(f"- {repo} ({kind}): conta={'sim' if state['tem_conta'] else 'não achei'}"
                   f" | tela={state['tela'][0] if state['tela'] else 'não achei'}"
                   f" | código={state['codigo'][0] if state['codigo'] else 'não achei'}"
                   f" | política={state['politica_no_app'][0] if state['politica_no_app'] else 'não achei'}")
    out.append(f"\n## Permissões declaradas ({len(result['permissoes'])})")
    for permission, info in sorted(result["permissoes"].items()):
        out.append(f"- {permission} -> {info['dado']} ({info['local']})")
    out.append(f"\nSecureStore/Keychain: {result['armazenamento_seguro_usos']} uso(s).")
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repos", nargs="+", help="pasta(s) do repo: app, servidor ou monorepo")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--max", type=int, default=15, help="locais por grupo no texto (padrão 15)")
    parser.add_argument("--include-tests", action="store_true", help="varre também pastas e arquivos de teste")
    args = parser.parse_args(argv)
    for repo in args.repos:
        if repo.startswith("-") or any(ord(ch) < 32 for ch in repo):
            print(f"error: caminho inválido: {repo!r}", file=sys.stderr)
            return 2
        if not os.path.isdir(repo):
            print(f"error: {repo} não é uma pasta", file=sys.stderr)
            return 2
    if args.max < 1:
        print("error: --max precisa ser 1 ou mais", file=sys.stderr)
        return 2
    result = Scanner(args.repos, args.include_tests).run().result()
    if result["arquivos"] == 0:
        print(f"error: 0 arquivos varridos (não varrido: {', '.join(result['nao_varridos'])}); confira o caminho"
              " (pastas como node_modules e _build são ignoradas)", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result, args.max))
    return 1 if any(f["severidade"] == "P1" for f in result["achados"]) else 0


if __name__ == "__main__":
    sys.exit(main())
