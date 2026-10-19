import csv
import json
import os
import plistlib
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SKILL = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

import preflight  # noqa: E402


def write(root, rel, content):
    path = os.path.join(str(root), *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    with open(path, mode, **({} if mode == "wb" else {"encoding": "utf-8"})) as handle:
        handle.write(content if isinstance(content, (str, bytes)) else json.dumps(content, indent=2))
    return path


def ids(app, config=None):
    return {f["id"] for f in preflight.Preflight(str(app), config).run().result()["findings"]}


GOOD_TEXT = "Usamos a câmera para você tirar a foto do seu perfil."


def clean_app(root):
    write(root, "package.json", {"dependencies": {"expo": "~57.0.4", "expo-updates": "~57.0.6", "expo-image-picker": "~57.0.2",
                                                  "@react-native-google-signin/google-signin": "^16.0.0",
                                                  "expo-apple-authentication": "~57.0.0"}})
    write(root, "app.json", {"expo": {
        "name": "Exemplo", "version": "1.2.0", "runtimeVersion": {"policy": "fingerprint"},
        "updates": {"url": "https://u.expo.dev/00000000-0000-0000-0000-000000000000"},
        "ios": {"bundleIdentifier": "com.exemplo.app", "config": {"usesNonExemptEncryption": False}},
        "android": {"package": "com.exemplo.app"},
        "plugins": [["expo-image-picker", {"photosPermission": "Usamos suas fotos para você escolher a foto do perfil.",
                                           "cameraPermission": GOOD_TEXT, "microphonePermission": False}]]}})
    write(root, "eas.json", {"cli": {"appVersionSource": "remote"},
                             "build": {"production": {"autoIncrement": True, "channel": "production"}},
                             "submit": {"production": {}}})
    write(root, "src/screens/settings.tsx", 'signInWithApple(); const t = "Excluir minha conta"; const p = "Política de privacidade";')
    return root


def test_csv_ids_unique_and_every_row_has_a_url_source():
    for name in ("checks.csv", "rejections.csv"):
        with open(os.path.join(SKILL, "data", name), encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        assert len({r["id"] for r in rows}) == len(rows)
        assert all(r["source"].startswith("https://") for r in rows), name


def test_every_id_used_by_the_script_exists_in_the_csv():
    with open(os.path.join(SCRIPTS, "preflight.py"), encoding="utf-8") as handle:
        source = handle.read()
    import re
    used = set(re.findall(r'"([A-Z]{3}\d{2})"', source))
    assert used and used <= set(preflight.load_checks())


def test_clean_app_has_no_findings(tmp_path):
    result = preflight.Preflight(str(clean_app(tmp_path))).run().result()
    assert result["findings"] == []
    code = subprocess.run([sys.executable, os.path.join(SCRIPTS, "preflight.py"), str(tmp_path)], capture_output=True).returncode
    assert code == 0


def test_default_permission_texts_and_missing_basics(tmp_path):
    write(tmp_path, "package.json", {"dependencies": {"expo": "~57.0.4", "expo-updates": "~57.0.6", "expo-image-picker": "*",
                                                      "expo-location": "*", "@react-native-google-signin/google-signin": "*"}})
    write(tmp_path, "app.json", {"expo": {"name": "Exemplo", "ios": {"supportsTablet": True},
                                          "plugins": ["expo-image-picker", ["expo-location", {"isIosBackgroundLocationEnabled": True}]]}})
    write(tmp_path, "eas.json", {"cli": {"appVersionSource": "local"}, "build": {"production": {}}})
    write(tmp_path, "src/app.tsx", "export default function App() { return null }")
    found = ids(tmp_path)
    assert {"VER01", "VER02", "OTA01", "OTA03", "OTA04", "IOS01", "IOS02", "IOS03", "IOS06", "IOS07", "IOS08",
            "AND01", "AND11", "EAS03", "ACC01", "PRV01"} <= found
    code = subprocess.run([sys.executable, os.path.join(SCRIPTS, "preflight.py"), str(tmp_path)], capture_output=True).returncode
    assert code == 1


def test_runtime_policy_other_than_fingerprint_is_flagged(tmp_path):
    clean_app(tmp_path)
    path = os.path.join(str(tmp_path), "app.json")
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data["expo"]["runtimeVersion"] = {"policy": "sdkVersion"}
    write(tmp_path, "app.json", data)
    assert ids(tmp_path) == {"OTA02"}


def test_dynamic_config_is_not_evaluated_without_resolved_json(tmp_path):
    clean_app(tmp_path)
    os.remove(os.path.join(str(tmp_path), "app.json"))
    write(tmp_path, "app.config.ts", "export default () => ({ name: 'x' })")
    result = preflight.Preflight(str(tmp_path)).run().result()
    assert {f["id"] for f in result["findings"]} == {"CFG01"}
    assert "runtimeVersion e OTA" in result["not_evaluated"]
    resolved = write(tmp_path, "resolved/config.json", {"name": "x", "version": "1.0.0", "runtimeVersion": "1.0.0",
                                                        "ios": {"bundleIdentifier": "a.b", "infoPlist": {"ITSAppUsesNonExemptEncryption": False}},
                                                        "android": {"package": "a.b"}, "updates": {"url": "https://u.expo.dev/x"},
                                                        "plugins": [["expo-image-picker", {"photosPermission": GOOD_TEXT,
                                                                                           "cameraPermission": False, "microphonePermission": False}]]})
    assert ids(tmp_path, resolved) == {"OTA02"}


def test_dynamic_config_without_resolved_json_exits_2(tmp_path):
    clean_app(tmp_path)
    os.remove(os.path.join(str(tmp_path), "app.json"))
    write(tmp_path, "app.config.js", "module.exports = { name: 'x' }")
    out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "preflight.py"), str(tmp_path)], capture_output=True, text=True)
    assert out.returncode == 2
    assert "--config" in out.stderr and "CFG01" in out.stdout


def test_bare_native_projects(tmp_path):
    write(tmp_path, "package.json", {"dependencies": {"react-native": "0.86.0"}})
    write(tmp_path, "ios/App/Info.plist", plistlib.dumps({
        "NSCameraUsageDescription": "Allow $(PRODUCT_NAME) to access your camera",
        "NSPhotoLibraryUsageDescription": "Fotos",
        "NSContactsUsageDescription": "Usamos seus contatos para você convidar amigos para o grupo.",
        "UIBackgroundModes": ["location"], "ITSAppUsesNonExemptEncryption": False}))
    write(tmp_path, "android/app/src/main/AndroidManifest.xml",
          '<manifest><uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION"/>'
          '<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION"/>'
          '<uses-permission android:name="android.permission.CAMERA"/></manifest>')
    write(tmp_path, "android/app/build.gradle", "android { defaultConfig { targetSdkVersion 34 } }")
    result = preflight.Preflight(str(tmp_path)).run().result()
    found = {f["id"]: f for f in result["findings"]}
    assert {"IOS04", "IOS05", "IOS08", "AND02", "AND04", "AND08"} <= set(found)
    assert "NSContactsUsageDescription" not in found["IOS04"]["detail"]
    assert "CFG02" not in found and "EAS01" not in found


def test_generated_native_folder_is_ignored_when_config_is_known(tmp_path):
    clean_app(tmp_path)
    write(tmp_path, ".gitignore", "node_modules\n/ios\n/android\n")
    write(tmp_path, "ios/App/Info.plist", plistlib.dumps({"NSCameraUsageDescription": "Allow $(PRODUCT_NAME) to access your camera"}))
    write(tmp_path, "android/app/src/main/AndroidManifest.xml",
          '<manifest><uses-permission android:name="android.permission.QUERY_ALL_PACKAGES"/></manifest>')
    assert ids(tmp_path) == set()


def test_sensitive_android_permissions_and_old_sdk(tmp_path):
    clean_app(tmp_path)
    write(tmp_path, "package.json", {"dependencies": {"expo": "~53.0.0", "expo-media-library": "*",
                                                      "expo-apple-authentication": "*"}})
    path = os.path.join(str(tmp_path), "app.json")
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data["expo"]["android"]["permissions"] = ["android.permission.READ_SMS", "QUERY_ALL_PACKAGES", "USE_EXACT_ALARM",
                                              "MANAGE_EXTERNAL_STORAGE"]
    data["expo"]["plugins"] = [["expo-build-properties", {"android": {"targetSdkVersion": 35}}]]
    write(tmp_path, "app.json", data)
    assert {"AND02", "AND03", "AND05", "AND06", "AND07", "AND09", "AND10"} <= ids(tmp_path)


def test_missing_eas_and_config(tmp_path):
    write(tmp_path, "package.json", {"dependencies": {"expo": "~57.0.0"}})
    assert ids(tmp_path) == {"CFG02"}
    write(tmp_path, "app.json", {"expo": {"name": "x", "version": "1.0.0", "ios": {"bundleIdentifier": "a.b",
                                                                                   "config": {"usesNonExemptEncryption": False}},
                                          "android": {"package": "a.b"}}})
    assert ids(tmp_path) == {"EAS01"}


def test_cli_rejects_missing_dir(tmp_path):
    code = subprocess.run([sys.executable, os.path.join(SCRIPTS, "preflight.py"), str(tmp_path / "nope")], capture_output=True).returncode
    assert code == 2


def test_json_output_has_sources(tmp_path):
    write(tmp_path, "package.json", {"dependencies": {"expo": "~57.0.0"}})
    out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "preflight.py"), str(tmp_path), "--json"],
                         capture_output=True, text=True).stdout
    data = json.loads(out)
    assert data["findings"] and all(f["source"].startswith("https://") for f in data["findings"])
    assert data["manual_checks"]


def test_broken_app_json_exits_2_instead_of_fake_finding(tmp_path):
    write(tmp_path, "app.json", "{ broken")
    run = subprocess.run([sys.executable, os.path.join(SCRIPTS, "preflight.py"), str(tmp_path)], capture_output=True, text=True)
    assert run.returncode == 2 and "app.json" in run.stderr
    write(tmp_path, "app.json", "[1]")
    assert subprocess.run([sys.executable, os.path.join(SCRIPTS, "preflight.py"), str(tmp_path)], capture_output=True).returncode == 2


def test_platform_runtime_version_wins_over_top_level(tmp_path):
    clean_app(tmp_path)
    path = os.path.join(str(tmp_path), "app.json")
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    data["expo"]["runtimeVersion"] = "1.0.0"
    data["expo"]["ios"]["runtimeVersion"] = {"policy": "fingerprint"}
    data["expo"]["android"]["runtimeVersion"] = {"policy": "fingerprint"}
    write(tmp_path, "app.json", data)
    assert ids(tmp_path) == set()


def test_odd_shapes_do_not_crash(tmp_path):
    write(tmp_path, "package.json", {"dependencies": None, "devDependencies": None})
    write(tmp_path, "eas.json", {"build": {"production": True}, "cli": [], "submit": "x"})
    write(tmp_path, "app.json", {"expo": {"ios": "x", "android": {"permissions": [1, "QUERY_ALL_PACKAGES"], "blockedPermissions": [None]},
                                          "plugins": "x", "updates": [], "version": "1.0.0"}})
    assert "AND06" in ids(tmp_path)
