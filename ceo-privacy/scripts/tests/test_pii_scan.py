import csv
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
SKILL = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

import pii_scan  # noqa: E402

FAKE_EMAIL = "maria.souza" + "@gmail.com"
FAKE_CPF = "123.456.789-09"  # valid check digits, synthetic


def write(root, rel, content):
    path = os.path.join(str(root), *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content if isinstance(content, str) else json.dumps(content, indent=2))
    return path


def scan(*roots, include_tests=False):
    return pii_scan.Scanner([str(r) for r in roots], include_tests).run().result()


def ids(result):
    return {(f["id"], f["categoria"]) for f in result["achados"]}


def mapped(result):
    return {(e["contexto"], e["campo"]): e for e in result["mapa"]}


def mobile_app(root):
    write(root, "package.json", {"dependencies": {"expo": "~54.0.0", "react-native": "0.81.0",
                                                   "@sentry/react-native": "^7.0.0", "@react-native-async-storage/async-storage": "2.0.0",
                                                   "@react-native-firebase/analytics": "^22.0.0"}})
    write(root, "app.json", {"expo": {"ios": {"infoPlist": {"NSLocationWhenInUseUsageDescription": "Usamos a localização."}},
                                      "android": {"permissions": ["android.permission.CAMERA"]}}})
    write(root, "src/auth.ts", """
import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import * as Sentry from '@sentry/react-native';
export async function signUp(email: string, password: string) {
  await AsyncStorage.setItem('auth_token', token);
  await SecureStore.setItemAsync('refresh', refreshToken);
  console.log('login ok', user.email);
  console.log('carregando tela');
  Sentry.setUser({ id: user.id, email: user.email });
  Sentry.setUser({ id: user.id });
  console.log(user);
}
""")
    write(root, "src/types.ts", """
export interface UserProfile {
  fullName: string;
  phone?: string;
  birthDate: string;
  emailVerified: boolean;
  locationId: string;
}
""")
    return root


def test_mobile_findings_and_values_never_printed(tmp_path, capsys):
    app = mobile_app(tmp_path / "app")
    write(app, "src/seed.ts", f"const owner = '{FAKE_EMAIL}'; const doc = '{FAKE_CPF}';\n")
    result = scan(app)
    found = ids(result)
    assert ("PRV-ARM", "credencial") in found
    assert ("PRV-LOG", "email") in found
    assert ("PRV-TER", "email") in found
    assert ("PRV-LOG", "objeto_inteiro") in found
    assert ("PRV-LIT", "email") in found and ("PRV-LIT", "documento") in found
    assert ("PRV-CTA", "conta") in found and ("PRV-POL", "politica") in found
    ter = [f for f in result["achados"] if f["id"] == "PRV-TER"]
    assert len(ter) == 1, "setUser with id only is not personal data sent to a third party"
    assert result["armazenamento_seguro_usos"] == 1
    fields = mapped(result)
    assert fields[("UserProfile", "fullName")]["categoria"] == "nome"
    assert fields[("UserProfile", "phone")]["categoria"] == "telefone"
    assert fields[("UserProfile", "birthDate")]["categoria"] == "nascimento"
    assert ("UserProfile", "emailVerified") not in fields and ("UserProfile", "locationId") not in fields
    sdks = {s["pacote"] for s in result["sdks"]}
    assert {"@sentry/react-native", "@react-native-firebase/analytics"} <= sdks
    assert "NSLocationWhenInUseUsageDescription" in result["permissoes"]
    assert pii_scan.main([str(app)]) == 1
    pii_scan.main([str(app), "--json"])
    out = capsys.readouterr().out
    assert FAKE_EMAIL not in out and FAKE_CPF not in out and "12345678909" not in out


def test_account_deletion_and_policy_found(tmp_path):
    app = mobile_app(tmp_path / "app")
    write(app, "src/settings.tsx", """
export function Settings() {
  return <><Button title="Excluir minha conta" onPress={deleteAccount} />
  <Link href="https://exemplo.com.br/privacidade">Política de privacidade</Link></>;
}
""")
    result = scan(app)
    assert not {f["id"] for f in result["achados"]} & {"PRV-CTA", "PRV-POL"}
    state = result["exclusao_conta"]["app"]
    assert state["tela"] and state["codigo"] and state["politica_no_app"]


def test_phoenix_server_schema_logs_and_deletion(tmp_path):
    server = tmp_path / "server"
    write(server, "mix.exs", 'defp deps do\n [{:phoenix, "~> 1.8"}, {:sentry, "~> 11.0"}]\nend\n')
    write(server, "lib/app/accounts/user.ex", """
defmodule App.Accounts.User do
  schema "users" do
    field :name, :string
    field :email, :string
    field :cpf, :string, redact: true
    field :health_notes, :string
    field :email_confirmed_at, :utc_datetime
    field :hashed_password, :string, redact: true
  end
  def registration_changeset(user, attrs), do: user
end
""")
    write(server, "priv/repo/migrations/20260101_create_users.exs", """
defmodule App.Repo.Migrations.CreateUsers do
  def change do
    create table(:users) do
      add :phone, :string
      add :latitude, :float
    end
  end
end
""")
    write(server, "lib/app_web/controllers/auth_controller.ex", """
def create(conn, params) do
  Logger.info("login", email: params["email"], ip: ip)
  Logger.info("login ok")
  Logger.debug("params #{inspect(params)}")
  Logger.info("token issued", token: token)
end
""")
    result = scan(server)
    fields = mapped(result)
    assert fields[("users", "name")]["categoria"] == "nome"
    assert fields[("users", "cpf")]["redact"] is True
    assert fields[("users", "health_notes")]["sensivel"] is True
    assert fields[("users", "phone")]["origem"] == "ecto_migration"
    assert ("users", "email_confirmed_at") not in fields
    found = ids(result)
    assert ("PRV-LOG", "email") in found
    assert ("PRV-LOG", "objeto_inteiro") in found
    assert ("PRV-LOGCRED", "credencial") in found
    assert ("PRV-CTA2", "conta") in found
    assert {s["pacote"] for s in result["sdks"]} >= {"sentry"}


def test_prisma_sql_typeorm_drizzle(tmp_path):
    repo = tmp_path / "api"
    write(repo, "package.json", {"dependencies": {"express": "4.0.0"}})
    write(repo, "prisma/schema.prisma", "model Customer {\n  id Int @id\n  name String\n  address String?\n  religion String?\n}\n")
    write(repo, "db/001.sql", "CREATE TABLE IF NOT EXISTS public.patients (\n  id uuid primary key,\n  full_name text,\n  blood_type text,\n  CONSTRAINT x CHECK (true)\n);\nALTER TABLE patients ADD COLUMN gender text;\n")
    write(repo, "src/entity/Driver.ts", "@Entity()\nexport class Driver {\n  @Column()\n  cpf: string;\n  helper(): string { return ''; }\n}\n")
    write(repo, "src/db/schema.ts", "export const leads = pgTable('leads', {\n  email: text('email'),\n  title: text('title'),\n});\n")
    write(repo, "src/routes.ts", "router.delete('/me', deleteMe);\nexport const createUser = () => 1;\n")
    result = scan(repo)
    fields = mapped(result)
    assert fields[("Customer", "name")]["categoria"] == "nome"
    assert fields[("Customer", "religion")]["sensivel"] is True
    assert fields[("patients", "blood_type")]["categoria"] == "saude"
    assert fields[("patients", "gender")]["categoria"] == "genero"
    assert fields[("Driver", "cpf")]["origem"] == "typeorm"
    assert fields[("leads", "email")]["origem"] == "drizzle"
    assert ("leads", "title") not in fields
    assert "PRV-CTA2" not in {f["id"] for f in result["achados"]}


def test_name_needs_person_context():
    assert pii_scan.classify("name", ("products",)) is None
    assert pii_scan.classify("name", ("user_profiles",)) == "nome"
    assert pii_scan.classify("deviceId") == "aparelho"
    assert pii_scan.classify("max_age") is None
    assert pii_scan.classify("image") is None


def test_storage_variants(tmp_path):
    app = tmp_path / "app"
    write(app, "package.json", {"dependencies": {"expo": "1"}})
    write(app, "src/plain.ts", "import { createMMKV } from 'react-native-mmkv';\nconst s = createMMKV({ id: 'a' });\ns.set('access_token', t);\n")
    write(app, "src/enc.ts", "import { MMKV } from 'react-native-mmkv';\nconst s = new MMKV({ id: 'b', encryptionKey: k });\ns.set('access_token', t);\n")
    write(app, "src/supa.ts", "import AsyncStorage from 'x';\nexport const c = createClient(u, k, { auth: { storage: AsyncStorage } });\n")
    write(app, "src/marker.ts", "import AsyncStorage from 'x';\nAsyncStorage.setItem(key(userId), now());\nAsyncStorage.setItem('user', JSON.stringify(u));\n")
    write(app, "src/dev.ts", "if (__DEV__) {\n  console.warn('x', body);\n}\n")
    result = scan(app)
    arm = {(f["arquivo"], f["categoria"]) for f in result["achados"] if f["id"].startswith("PRV-ARM")}
    assert ("src/plain.ts", "credencial") in arm
    assert not any(a == "src/enc.ts" for a, _ in arm)
    assert ("src/supa.ts", "credencial") in arm
    assert ("src/marker.ts", "objeto_inteiro") in arm
    assert len([a for a in arm if a[0] == "src/marker.ts"]) == 1
    assert not any(f["arquivo"] == "src/dev.ts" for f in result["achados"])


def test_skips_vendor_tests_and_secret_files_by_relative_path(tmp_path):
    root = tmp_path / "deps" / "repo"  # parent named like a skipped folder must not matter
    write(root, "src/a.ts", "console.log(user.email);\n")
    write(root, "node_modules/lib/index.js", "console.log(user.email);\n")
    write(root, "_build/x.ex", "Logger.info(email)\n")
    write(root, "__tests__/a.test.ts", "console.log(user.email);\n")
    write(root, "src/b.test.ts", "console.log(user.email);\n")
    write(root, ".env.local", f"ADMIN={FAKE_EMAIL}\n")
    result = scan(root)
    assert result["arquivos"] == 1
    assert [f["arquivo"] for f in result["achados"] if f["id"] == "PRV-LOG"] == ["src/a.ts"]
    assert scan(root, include_tests=True)["arquivos"] == 3


def test_bad_input_and_empty_repo(tmp_path, capsys):
    assert pii_scan.main(["--", "-x"]) == 2
    assert pii_scan.main([str(tmp_path / "missing")]) == 2
    empty = tmp_path / "empty"
    write(empty, "node_modules/a.js", "x")
    assert pii_scan.main([str(empty)]) == 2
    assert "0 arquivos" in capsys.readouterr().err


def test_cli_runs_without_shell(tmp_path):
    app = mobile_app(tmp_path / "app")
    proc = subprocess.run([sys.executable, "-I", os.path.join(SCRIPTS, "pii_scan.py"), str(app), "--max", "2"],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 1
    assert "## Mapa de dados pessoais" in proc.stdout and "## Exclusão de conta" in proc.stdout


def test_every_check_id_used_exists_in_csv_with_source():
    with open(os.path.join(SKILL, "data", "checks.csv"), encoding="utf-8") as handle:
        rows = {row["id"]: row for row in csv.DictReader(handle)}
    with open(os.path.join(SCRIPTS, "pii_scan.py"), encoding="utf-8") as handle:
        code = handle.read()
    used = set(__import__("re").findall(r'"(PRV-[A-Z0-9]+)"', code))
    assert used and used <= set(rows)
    assert all(rows[i]["source"].startswith("https://") and rows[i]["severidade"] in ("P1", "P2", "P3") for i in used)


def test_sdk_csv_rows_have_source():
    with open(os.path.join(SKILL, "data", "sdks.csv"), encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows and all(r["source"].startswith("https://") and r["ecossistema"] in ("npm", "hex") for r in rows)


def test_max_files_cut_warns_and_skips_judging_unread_repo(tmp_path, monkeypatch, capsys):
    first, app = tmp_path / "first", mobile_app(tmp_path / "app")
    for i in range(3):
        write(first, f"f{i}.ts", "export const x = 1;\n")
    monkeypatch.setattr(pii_scan, "MAX_FILES", 2)
    result = scan(first, app)
    assert result["cortado_em"] == "first"
    assert result["nao_varridos"] == ["app"]
    assert not [f for f in result["achados"] if f["repo"] == "app"]
    pii_scan.main([str(first), str(app)])
    out = capsys.readouterr().out
    assert "cortada" in out and "first" in out and "app" in out and "não varrido" in out
    assert "- app: NÃO VERIFICADO" in out


def test_cut_inside_repo_does_not_judge_deletion(tmp_path, monkeypatch):
    app = mobile_app(tmp_path / "app")
    assert "PRV-CTA" in {f["id"] for f in scan(app)["achados"]}
    monkeypatch.setattr(pii_scan, "MAX_FILES", 3)
    result = scan(app)
    assert result["cortado_em"] == "app"
    assert not {f["id"] for f in result["achados"]} & {"PRV-CTA", "PRV-CTA2", "PRV-POL"}


def test_repo_with_zero_files_read_is_flagged_per_repo(tmp_path, capsys):
    app = mobile_app(tmp_path / "app")
    images = tmp_path / "images"
    (images).mkdir()
    (images / "logo.png").write_bytes(b"\x89PNG")
    result = scan(app, images)
    assert result["nao_varridos"] == ["images"]
    assert pii_scan.main([str(app), str(images)]) in (0, 1)
    assert "images" in capsys.readouterr().out.split("## Achados")[0]
    empty = tmp_path / "empty"
    empty.mkdir()
    assert pii_scan.main([str(images), str(empty)]) == 2
    assert "não varrido" in capsys.readouterr().err
