#!/usr/bin/env python3
"""Pre-flight of a mobile app before sending a version to the App Store and Google Play.

Usage: python3 preflight.py <app-dir> [--config expo-config.json] [--json]

Reads, without writing anything:
- app.json (Expo) or the output of `npx expo config --json` passed with --config.
  app.config.ts/js is code: the script does not run it and says so (CFG01).
- eas.json, package.json and, when they exist, ios/ and android/.
Every finding carries the id of a row in data/checks.csv, where severity and the
primary source (URL) live. Checks marked `manual` in the CSV are not automated:
the skill walks through them with the person.

Exit code: 0 no P0/P1, 1 some P0/P1, 2 bad input.
"""
import argparse
import csv
import glob
import json
import os
import plistlib
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKS_CSV = os.path.join(os.path.dirname(HERE), "data", "checks.csv")
SEVERITY_ORDER = ("P0", "P1", "P2", "P3")
REQUIRED_TARGET_SDK = 36
MIN_EXPO_SDK_TARGETING_36 = 54
SKIP_DIRS = {"node_modules", "ios", "android", ".git", ".expo", "dist", "build", "web-build", "coverage", "Pods", "__tests__", "test", "tests", "e2e", ".maestro"}
SOURCE_EXT = (".ts", ".tsx", ".js", ".jsx", ".json")
MAX_SOURCE_FILES = 20000
CONFIG_FILES = {"package.json", "package-lock.json", "app.json", "eas.json", "tsconfig.json", "jsconfig.json"}

# Library -> (config plugin option, Info.plist key). The plugin writes a generic English
# default ("Allow $(PRODUCT_NAME) to ...") when the option is not set, even if the app never asks.
PERMISSION_LIBS = {
    "expo-camera": [("cameraPermission", "NSCameraUsageDescription"), ("microphonePermission", "NSMicrophoneUsageDescription")],
    "expo-image-picker": [("photosPermission", "NSPhotoLibraryUsageDescription"), ("cameraPermission", "NSCameraUsageDescription"),
                          ("microphonePermission", "NSMicrophoneUsageDescription")],
    "expo-location": [("locationWhenInUsePermission", "NSLocationWhenInUseUsageDescription"),
                      ("locationAlwaysAndWhenInUsePermission", "NSLocationAlwaysAndWhenInUseUsageDescription"),
                      ("locationAlwaysPermission", "NSLocationAlwaysUsageDescription"),
                      ("motionUsagePermission", "NSMotionUsageDescription")],
    "expo-contacts": [("contactsPermission", "NSContactsUsageDescription")],
    "expo-calendar": [("calendarPermission", "NSCalendarsUsageDescription"), ("remindersPermission", "NSRemindersUsageDescription")],
    "expo-local-authentication": [("faceIDPermission", "NSFaceIDUsageDescription")],
    "expo-secure-store": [("faceIDPermission", "NSFaceIDUsageDescription")],
    "expo-tracking-transparency": [("userTrackingPermission", "NSUserTrackingUsageDescription")],
    "expo-sensors": [("motionPermission", "NSMotionUsageDescription")],
    "expo-audio": [("microphonePermission", "NSMicrophoneUsageDescription")],
}
SENSITIVE_ANDROID = {
    "ACCESS_BACKGROUND_LOCATION": "AND04",
    "READ_SMS": "AND05", "SEND_SMS": "AND05", "RECEIVE_SMS": "AND05", "RECEIVE_MMS": "AND05", "RECEIVE_WAP_PUSH": "AND05",
    "READ_CALL_LOG": "AND05", "WRITE_CALL_LOG": "AND05", "PROCESS_OUTGOING_CALLS": "AND05",
    "QUERY_ALL_PACKAGES": "AND06",
    "READ_MEDIA_IMAGES": "AND07", "READ_MEDIA_VIDEO": "AND07",
    "USE_EXACT_ALARM": "AND09",
    "MANAGE_EXTERNAL_STORAGE": "AND10",
}
AUTH_LIBS = {"@react-native-google-signin/google-signin", "expo-auth-session", "@react-native-firebase/auth", "@supabase/supabase-js",
             "expo-apple-authentication", "@invertase/react-native-apple-authentication", "react-native-fbsdk-next", "@clerk/clerk-expo",
             "@aws-amplify/auth", "aws-amplify", "react-native-auth0"}
SOCIAL_LOGIN_LIBS = {"@react-native-google-signin/google-signin", "react-native-fbsdk-next"}
APPLE_LOGIN_LIBS = {"expo-apple-authentication", "@invertase/react-native-apple-authentication"}
AUTH_CODE = re.compile(r"\b(signUp|signInWith\w+|createUserWithEmailAndPassword|signInWithPassword)\b")
SOCIAL_CODE = re.compile(r"expo-auth-session/providers/(google|facebook)")
DELETION_CODE = re.compile(
    r"(delete|remove|excluir|apagar|deletar|encerrar)[\s_-]*(my[\s_-]*|minha[\s_-]*|a[\s_-]*|sua[\s_-]*)?(account|conta)"
    r"|deleteUser|delete_user|account[_-]?deletion", re.I)
PRIVACY_CODE = re.compile(r"privacidade|privacy|privacidad", re.I)
DEFAULT_TEXT = re.compile(r"Allow \$\(PRODUCT_NAME\)")


def load_checks():
    with open(CHECKS_CSV, encoding="utf-8") as handle:
        return {row["id"]: row for row in csv.DictReader(handle)}


class BadInput(Exception):
    """File exists but is not a JSON object: exit 2, never a fake finding."""


def obj(value):
    return value if isinstance(value, dict) else {}


def read_json(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return None


def read_text(path):
    try:
        with open(path, encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except OSError:
        return ""


def line_of(path, needle):
    for number, line in enumerate(read_text(path).splitlines(), 1):
        if needle in line:
            return f"{os.path.basename(path)}:{number}"
    return os.path.basename(path)


def gitignored_root_dir(app, name):
    """True when the root .gitignore ignores the folder (CNG: ios/ and android/ are generated)."""
    patterns = {line.strip() for line in read_text(os.path.join(app, ".gitignore")).splitlines()}
    return bool(patterns & {name, f"/{name}", f"{name}/", f"/{name}/"})


def word_count(text):
    return len(re.findall(r"\w+", text or ""))


def major(version):
    match = re.search(r"(\d+)", version or "")
    return int(match.group(1)) if match else None


class Preflight:
    def __init__(self, app, config_path=None):
        self.app = os.path.abspath(app)
        self.checks = load_checks()
        self.findings = []
        self.not_evaluated = []
        self.config, self.config_label, self.config_file = self._load_config(config_path)
        self.package = obj(read_json(os.path.join(self.app, "package.json")))
        self.deps = {**obj(self.package.get("devDependencies")), **obj(self.package.get("dependencies"))}
        eas = read_json(os.path.join(self.app, "eas.json"))
        self.eas = obj(eas) if eas is not None else None
        self.ios_dir = os.path.join(self.app, "ios")
        self.android_dir = os.path.join(self.app, "android")
        self.has_ios = os.path.isdir(self.ios_dir)
        self.has_android = os.path.isdir(self.android_dir)
        self.ios_generated = self.has_ios and gitignored_root_dir(self.app, "ios")
        self.android_generated = self.has_android and gitignored_root_dir(self.app, "android")
        self._sources = None

    # ---------- input ----------
    def _load_config(self, config_path):
        if config_path:
            data = read_json(config_path)
            if not isinstance(data, dict):
                raise BadInput(f"{config_path} não é um objeto JSON (saída de `npx expo config --json`)")
            data = obj(data.get("exp")) or obj(data.get("expo")) or data
            return data, f"--config {os.path.basename(config_path)}", config_path
        app_json = os.path.join(self.app, "app.json")
        dynamic = [name for name in ("app.config.ts", "app.config.js", "app.config.mjs", "app.config.cjs")
                   if os.path.exists(os.path.join(self.app, name))]
        if dynamic:
            self.findings.append(self._finding("CFG01", f"{dynamic[0]} não avaliado; checagens que dependem do app config ficaram de fora",
                                               dynamic[0]))
            return None, f"{dynamic[0]} (não avaliado)", None
        if not os.path.exists(app_json):
            return None, "nenhum", None
        data = read_json(app_json)
        if not isinstance(data, dict) or ("expo" in data and not isinstance(data["expo"], dict)):
            raise BadInput("app.json inválido (JSON quebrado ou não é objeto)")
        return data.get("expo", data), "app.json", app_json

    def _finding(self, check_id, detail, evidence=""):
        row = self.checks[check_id]
        return {"id": check_id, "severity": row["severity"], "store": row["store"], "check": row["check"],
                "detail": detail, "evidence": evidence, "source": row["source"]}

    def add(self, check_id, detail, evidence=""):
        self.findings.append(self._finding(check_id, detail, evidence))

    def where(self, needle):
        if self.config_file and self.config_label == "app.json":
            return line_of(self.config_file, needle)
        return "app config resolvido" if self.config_file else self.config_label

    def plugin_options(self, name):
        for entry in (self.config or {}).get("plugins") if isinstance((self.config or {}).get("plugins"), list) else []:
            if entry == name:
                return {}
            if isinstance(entry, list) and entry and entry[0] == name:
                return entry[1] if len(entry) > 1 and isinstance(entry[1], dict) else {}
        return None

    def source_files(self):
        if self._sources is None:
            found = []
            for root, dirs, files in os.walk(self.app):
                dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
                found += [os.path.join(root, f) for f in files if f.endswith(SOURCE_EXT) and f not in CONFIG_FILES]
                if len(found) > MAX_SOURCE_FILES:
                    break
            self._sources = found
        return self._sources

    def code_matches(self, pattern):
        for path in self.source_files():
            if pattern.search(read_text(path)):
                return os.path.relpath(path, self.app)
        return None

    # ---------- checks ----------
    def run(self):
        if self.config is None and not (self.has_ios or self.has_android) and not self.findings:
            self.add("CFG02", "sem app.json, app.config ou pastas nativas", self.app)
            return self
        if self.config is not None:
            self.check_versions()
            self.check_ota()
            self.check_ios_config()
            self.check_android_config()
        else:
            self.not_evaluated += ["versão e build", "runtimeVersion e OTA", "textos de permissão no app config", "identificadores"]
        self.check_eas()
        self.check_sdk()
        self.check_native_ios()
        self.check_native_android()
        self.check_account_and_privacy()
        return self

    def check_versions(self):
        cfg = self.config
        if not cfg.get("version"):
            self.add("VER01", "sem `version`", self.config_label)
        source = obj((self.eas or {}).get("cli")).get("appVersionSource")
        production = obj(obj((self.eas or {}).get("build")).get("production"))
        ios_build, android_code = obj(cfg.get("ios")).get("buildNumber"), obj(cfg.get("android")).get("versionCode")
        if source == "local" and not production.get("autoIncrement"):
            self.add("VER02", f"appVersionSource local sem autoIncrement (buildNumber={ios_build}, versionCode={android_code})",
                     line_of(os.path.join(self.app, "eas.json"), "appVersionSource"))
        if source == "remote" and (ios_build or android_code):
            self.add("VER04", "buildNumber/versionCode no app config são ignorados com fonte remote", self.where("buildNumber" if ios_build else "versionCode"))

    def check_ota(self):
        if "expo-updates" not in self.deps:
            return
        cfg = self.config
        # The platform value wins over the top-level one (docs.expo.dev/eas-update/runtime-versions/).
        runtimes = {p: obj(cfg.get(p)).get("runtimeVersion") or cfg.get("runtimeVersion") for p in ("ios", "android")}
        if not any(runtimes.values()):
            self.add("OTA01", "expo-updates instalado e nenhum runtimeVersion", self.config_label)
        fragile = []
        for platform, runtime in runtimes.items():
            if not runtime:
                continue
            policy = runtime.get("policy") if isinstance(runtime, dict) else None
            if policy != "fingerprint":
                fragile.append(f"{platform}: " + (f"policy {policy}" if policy else f"texto fixo \"{runtime}\""))
        if fragile:
            self.add("OTA02", "runtimeVersion " + "; ".join(fragile), self.where("runtimeVersion"))
        if not obj(cfg.get("updates")).get("url"):
            self.add("OTA04", "sem updates.url", self.config_label)
        production = obj((self.eas or {}).get("build")).get("production")
        if isinstance(production, dict) and not production.get("channel"):
            self.add("OTA03", "perfil production sem channel", line_of(os.path.join(self.app, "eas.json"), '"production"'))

    def check_ios_config(self):
        ios = obj(self.config.get("ios"))
        if not ios.get("bundleIdentifier") and not (self.has_ios and not self.ios_generated):
            self.add("IOS01", "sem ios.bundleIdentifier", self.config_label)
        info = obj(ios.get("infoPlist"))
        if "usesNonExemptEncryption" not in obj(ios.get("config")) and "ITSAppUsesNonExemptEncryption" not in info:
            self.add("IOS02", "nem ios.config.usesNonExemptEncryption nem infoPlist.ITSAppUsesNonExemptEncryption", self.config_label)
        if ios.get("supportsTablet"):
            self.add("IOS07", "supportsTablet: true", self.where("supportsTablet"))
        for lib, pairs in PERMISSION_LIBS.items():
            if lib not in self.deps:
                continue
            options = self.plugin_options(lib) or {}
            default_keys, short_keys = [], []
            for option, key in pairs:
                value = info.get(key, options.get(option))
                if value is False:
                    continue
                if value is None or (isinstance(value, str) and DEFAULT_TEXT.search(value)):
                    default_keys.append(key)
                elif isinstance(value, str) and word_count(value) < 4:
                    short_keys.append(key)
            if default_keys:
                self.add("IOS03", f"{lib} sem texto próprio para {', '.join(default_keys)}", self.where(lib))
            if short_keys:
                self.add("IOS03", f"{lib}: texto curto demais para {', '.join(short_keys)}", self.where(lib))
        location = self.plugin_options("expo-location") or {}
        if location.get("isIosBackgroundLocationEnabled") or "location" in (info.get("UIBackgroundModes") or []):
            self.add("IOS08", "localização em segundo plano ligada", self.where("isIosBackgroundLocationEnabled"))

    def check_android_config(self):
        android = obj(self.config.get("android"))
        if not android.get("package") and not (self.has_android and not self.android_generated):
            self.add("AND01", "sem android.package", self.config_label)
        blocked = {p.split(".")[-1] for p in android.get("blockedPermissions") or [] if isinstance(p, str)}
        for permission in [p for p in android.get("permissions") or [] if isinstance(p, str)]:
            self._sensitive(permission, self.where(permission.split(".")[-1]))
        location = self.plugin_options("expo-location") or {}
        if "expo-location" in self.deps and location.get("isAndroidBackgroundLocationEnabled"):
            self.add("AND04", "expo-location com isAndroidBackgroundLocationEnabled", self.where("isAndroidBackgroundLocationEnabled"))
        if "expo-media-library" in self.deps:
            self.add("AND07", "expo-media-library instalado (acesso amplo a fotos)", "package.json")
        build_props = obj(obj(self.plugin_options("expo-build-properties")).get("android"))
        target = build_props.get("targetSdkVersion")
        if major(str(target)) is not None and major(str(target)) < REQUIRED_TARGET_SDK:
            self.add("AND02", f"targetSdkVersion {target}", self.where("targetSdkVersion"))
        if "RECORD_AUDIO" not in blocked:
            picker, camera = self.plugin_options("expo-image-picker"), self.plugin_options("expo-camera")
            if "expo-image-picker" in self.deps and (picker or {}).get("microphonePermission") is not False:
                self.add("AND11", "expo-image-picker sem microphonePermission: false", self.where("expo-image-picker"))
            if "expo-camera" in self.deps and (camera or {}).get("recordAudioAndroid") is not False:
                self.add("AND11", "expo-camera sem recordAudioAndroid: false", self.where("expo-camera"))

    def _sensitive(self, permission, evidence):
        name = permission.split(".")[-1]
        if name.startswith("FOREGROUND_SERVICE_"):
            self.add("AND08", name, evidence)
        elif name in SENSITIVE_ANDROID:
            self.add(SENSITIVE_ANDROID[name], name, evidence)

    def check_eas(self):
        if self.eas is None:
            if "expo" in self.deps:
                self.add("EAS01", "sem eas.json", self.app)
            return
        eas_path = os.path.join(self.app, "eas.json")
        if not (obj(self.eas.get("cli")).get("appVersionSource")):
            self.add("VER03", "sem cli.appVersionSource", "eas.json")
        if "production" not in obj(self.eas.get("build")):
            self.add("EAS02", "sem build.production", "eas.json")
        if "production" not in obj(self.eas.get("submit")):
            self.add("EAS03", "sem submit.production", line_of(eas_path, '"submit"'))

    def check_sdk(self):
        installed = read_json(os.path.join(self.app, "node_modules", "expo", "package.json")) or {}
        version = installed.get("version") or self.deps.get("expo")
        sdk = major(version) if version else None
        if sdk is not None and sdk < MIN_EXPO_SDK_TARGETING_36:
            self.add("AND03", f"expo {version}", line_of(os.path.join(self.app, "package.json"), '"expo"'))

    def check_native_ios(self):
        if not self.has_ios:
            return
        if self.ios_generated and self.config is not None:
            return  # app config is the source of truth; ios/ may be stale
        note = " (pasta ios/ gerada e fora do git: pode estar velha, corrija no app config)" if self.ios_generated else ""
        plists = [p for p in glob.glob(os.path.join(self.ios_dir, "*", "Info.plist"))
                  if not re.search(r"/(Pods|build|.*Tests)/", p)]
        for path in plists:
            try:
                with open(path, "rb") as handle:
                    info = plistlib.load(handle)
            except Exception:  # noqa: BLE001 - malformed plist is reported as not evaluated
                self.not_evaluated.append(os.path.relpath(path, self.app))
                continue
            rel = os.path.relpath(path, self.app)
            weak = [k for k, v in info.items() if k.endswith("UsageDescription") and isinstance(v, str)
                    and (DEFAULT_TEXT.search(v) or word_count(v) < 4)]
            if weak:
                self.add("IOS04", f"{', '.join(sorted(weak))}{note}", rel)
            if "location" in (info.get("UIBackgroundModes") or []):
                self.add("IOS08", f"UIBackgroundModes inclui location{note}", rel)
            if "ITSAppUsesNonExemptEncryption" not in info and self.config is None:
                self.add("IOS02", f"Info.plist sem ITSAppUsesNonExemptEncryption{note}", rel)
        if not self.ios_generated:
            manifests = [p for p in glob.glob(os.path.join(self.ios_dir, "**", "PrivacyInfo.xcprivacy"), recursive=True)
                         if "/Pods/" not in p and "/build/" not in p]
            if plists and not manifests:
                self.add("IOS05", "nenhum PrivacyInfo.xcprivacy no projeto iOS", "ios/")

    def check_native_android(self):
        if not self.has_android or (self.android_generated and self.config is not None):
            return
        manifest = os.path.join(self.android_dir, "app", "src", "main", "AndroidManifest.xml")
        for permission in sorted(set(re.findall(r'uses-permission[^>]*android:name="([^"]+)"', read_text(manifest)))):
            self._sensitive(permission, line_of(manifest, permission))
        gradle = os.path.join(self.android_dir, "app", "build.gradle")
        texts = read_text(gradle) + "\n" + read_text(os.path.join(self.android_dir, "gradle.properties")) + "\n" + \
            read_text(os.path.join(self.android_dir, "build.gradle"))
        match = re.search(r"targetSdk(?:Version)?\s*[=:]?\s*(\d+)", texts)
        if match and int(match.group(1)) < REQUIRED_TARGET_SDK:
            self.add("AND02", f"targetSdkVersion {match.group(1)}", "android/")

    def check_account_and_privacy(self):
        auth_libs = AUTH_LIBS & set(self.deps)
        auth_code = None if auth_libs else self.code_matches(AUTH_CODE)
        if auth_libs or auth_code:
            if not self.code_matches(DELETION_CODE):
                why = ", ".join(sorted(auth_libs)) if auth_libs else auth_code
                self.add("ACC01", f"login detectado ({why}) e nenhum texto ou chamada de exclusão de conta", "código do app")
            social = (SOCIAL_LOGIN_LIBS & set(self.deps)) or ({"expo-auth-session"} if "expo-auth-session" in self.deps and self.code_matches(SOCIAL_CODE) else set())
            if social and not (APPLE_LOGIN_LIBS & set(self.deps)):
                self.add("IOS06", f"login social ({', '.join(sorted(social))}) sem Sign in with Apple instalado", "package.json")
        if self.source_files() and not self.code_matches(PRIVACY_CODE):
            self.add("PRV01", "nenhuma menção a política de privacidade", "código do app")

    # ---------- output ----------
    def result(self):
        order = {s: i for i, s in enumerate(SEVERITY_ORDER)}
        findings = sorted(self.findings, key=lambda f: (order.get(f["severity"], 9), f["id"]))
        manual = [row["id"] for row in self.checks.values() if row["auto"] == "manual"]
        return {"app": self.app, "config": self.config_label, "ios_dir": self._dir_label(self.has_ios, self.ios_generated),
                "android_dir": self._dir_label(self.has_android, self.android_generated), "findings": findings,
                "not_evaluated": self.not_evaluated, "manual_checks": manual}

    @staticmethod
    def _dir_label(exists, generated):
        return "ausente" if not exists else ("gerada (fora do git)" if generated else "no git")


def render(result):
    lines = [f"Preflight: {result['app']}",
             f"Config: {result['config']} | ios/: {result['ios_dir']} | android/: {result['android_dir']}"]
    if not result["findings"]:
        lines.append("Nenhum achado automático.")
    for finding in result["findings"]:
        lines.append(f"- {finding['severity']} [{finding['id']}] {finding['detail']} ({finding['evidence']}) [fonte: {finding['source']}]")
    if result["not_evaluated"]:
        lines.append("Não avaliado: " + "; ".join(result["not_evaluated"]))
    lines.append(f"Checagens manuais pendentes: {len(result['manual_checks'])} (data/checks.csv, auto=manual)")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("app")
    parser.add_argument("--config", help="JSON de `npx expo config --json`")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not os.path.isdir(args.app):
        print(f"error: {args.app} is not a directory", file=sys.stderr)
        return 2
    try:
        result = Preflight(args.app, args.config).run().result()
    except BadInput as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    if any(f["id"] == "CFG01" for f in result["findings"]):  # app config not evaluated: never a passing preflight
        print("error: app.config.ts/js não foi avaliado; rode `npx expo config --json > /tmp/app-config.json` "
              "e repita com `--config /tmp/app-config.json`", file=sys.stderr)
        return 2
    return 1 if any(f["severity"] in ("P0", "P1") for f in result["findings"]) else 0


if __name__ == "__main__":
    sys.exit(main())
