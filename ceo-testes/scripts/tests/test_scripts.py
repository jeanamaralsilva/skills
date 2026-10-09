"""Tests for the ceo-testes tools. Run from scripts/: python -m pytest -q tests"""
import json
import os
import re
import subprocess
import sys
import textwrap

import pytest

SCRIPTS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.dirname(SCRIPTS)
sys.path.insert(0, SCRIPTS)

import lint_report  # noqa: E402
import map_flows  # noqa: E402
import map_realtime  # noqa: E402
import search  # noqa: E402
import sim_session  # noqa: E402


# ---------- fixtures: a tiny Expo app + a tiny Phoenix server, generated at test time ----------

def make_mobile(root):
    app = os.path.join(root, "mobile")
    os.makedirs(os.path.join(app, "app", "(tabs)"))
    os.makedirs(os.path.join(app, "app", "class"))
    os.makedirs(os.path.join(app, "src", "lib"))
    os.makedirs(os.path.join(app, "src", "features", "chat"))
    open(os.path.join(app, "package.json"), "w").write('{"name":"m","dependencies":{"expo-router":"~6.0.0","phoenix":"1.8.0"}}')
    open(os.path.join(app, "app", "_layout.tsx"), "w").write("export default function L(){return null}")
    open(os.path.join(app, "app", "(tabs)", "index.tsx"), "w").write(textwrap.dedent("""
        import { Button, Pressable } from 'react-native';
        export default function Home() {
          const m = useMutation({ mutationFn: joinClass });
          return (<>
            <Pressable onPress={() => m.mutate()} testID="join">Entrar na aula</Pressable>
            <Button title="Sair" onPress={logout} />
          </>);
        }
    """))
    open(os.path.join(app, "app", "class", "[id].tsx"), "w").write(textwrap.dedent("""
        export default function ClassScreen() {
          const { isPending, error } = useQuery({ queryKey: ['class'] });
          if (isPending) return <Spinner/>;
          if (error) return <Text>erro</Text>;
          return <Pressable onPress={send} accessibilityLabel="Enviar resposta"/>;
        }
    """))
    open(os.path.join(app, "src", "lib", "socket.ts"), "w").write(textwrap.dedent("""
        import { Socket } from 'phoenix';
        export const socket = new Socket(url, { params: { token } });
        export function joinClass(id) {
          const channel = socket.channel(`class:${id}`, {});
          channel.on('question_created', onQuestion);
          channel.on("answer_received", onAnswer);
          channel.on('presence_state', onState);
          channel.push('join_class', { id });
          channel.push("send_answer", payload);
          return channel;
        }
    """))
    open(os.path.join(app, "src", "features", "chat", "chat.tsx"), "w").write(textwrap.dedent("""
        channel.on('message_new', add);
        channel.push('message_send', body);
    """))
    return app


def make_server(root):
    srv = os.path.join(root, "server")
    os.makedirs(os.path.join(srv, "lib", "app_web", "channels"))
    open(os.path.join(srv, "mix.exs"), "w").write('defmodule App.MixProject do\n  use Mix.Project\nend\n')
    open(os.path.join(srv, "lib", "app_web", "channels", "user_socket.ex"), "w").write(textwrap.dedent("""
        defmodule AppWeb.UserSocket do
          use Phoenix.Socket
          channel "class:*", AppWeb.ClassChannel
          channel "chat:*", AppWeb.ChatChannel
          def connect(%{"token" => token}, socket, _info), do: {:ok, socket}
          def id(socket), do: "user_socket:#{socket.assigns.user_id}"
        end
    """))
    open(os.path.join(srv, "lib", "app_web", "channels", "class_channel.ex"), "w").write(textwrap.dedent("""
        defmodule AppWeb.ClassChannel do
          use AppWeb, :channel
          def join("class:" <> id, _payload, socket), do: {:ok, socket}
          def handle_in("join_class", %{"id" => id}, socket) do
            broadcast!(socket, "student_joined", %{id: id})
            {:reply, :ok, socket}
          end
          def handle_in("send_answer", payload, socket) do
            push(socket, "answer_received", payload)
            {:noreply, socket}
          end
          def handle_in("create_question", payload, socket) do
            broadcast(socket, "question_created", payload)
            {:noreply, socket}
          end
        end
    """))
    open(os.path.join(srv, "lib", "app_web", "channels", "chat_channel.ex"), "w").write(textwrap.dedent("""
        defmodule AppWeb.ChatChannel do
          use AppWeb, :channel
          def join("chat:" <> _, _p, socket), do: {:ok, socket}
          def handle_in("message_send", body, socket) do
            broadcast!(socket, "message_new", body)
            {:noreply, socket}
          end
        end
    """))
    return srv


# ---------- map_flows ----------

def test_map_flows_lists_screens_actions_and_states(tmp_path):
    app = make_mobile(str(tmp_path))
    result = map_flows.scan(app)
    routes = {r["route"] for r in result["screens"]}
    assert "/(tabs)/" in routes or "/" in routes
    assert any(r["route"].startswith("/class/[id]") for r in result["screens"])
    home = next(r for r in result["screens"] if r["file"].endswith("index.tsx"))
    labels = {a["label"] for a in home["actions"]}
    assert "Entrar na aula" in labels and "Sair" in labels
    assert any(a["mutation"] for a in home["actions"]), "join action should be flagged as a mutation"
    klass = next(r for r in result["screens"] if "[id]" in r["file"])
    assert klass["states"]["loading"] and klass["states"]["error"]
    assert not home["states"]["error"]


def test_map_flows_matrix_has_one_row_per_action_and_sad_path(tmp_path):
    app = make_mobile(str(tmp_path))
    rows = map_flows.matrix(map_flows.scan(app))
    joins = [r for r in rows if r["action"] == "Entrar na aula"]
    paths = {r["path"] for r in joins}
    assert {"feliz", "duplo-toque", "sem-rede"} <= paths


def test_map_flows_cli_json(tmp_path):
    app = make_mobile(str(tmp_path))
    out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "map_flows.py"), app, "--json"], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    data = json.loads(out.stdout)
    assert data["screens"] and data["matrix"]


# ---------- map_realtime ----------

def test_map_realtime_pairs_events_and_flags_gaps(tmp_path):
    app = make_mobile(str(tmp_path))
    srv = make_server(str(tmp_path))
    result = map_realtime.scan(app, srv)
    assert {"class:*", "chat:*"} <= set(result["topics"])
    # server pushes answer_received and the mobile listens: paired
    assert "answer_received" in result["paired_server_to_mobile"]
    # server broadcasts student_joined but nobody listens on mobile
    assert "student_joined" in result["server_events_without_listener"]
    # mobile listens presence_state, which Phoenix.Presence emits (not a gap)
    assert "presence_state" not in result["mobile_listeners_without_server_event"]
    # mobile pushes join_class / send_answer / message_send and the server handles all three
    assert result["mobile_pushes_without_handler"] == []
    # server handles create_question but the mobile never pushes it (another actor does)
    assert "create_question" in result["handlers_without_mobile_push"]


def test_map_realtime_matrix_targets_two_actors(tmp_path):
    app = make_mobile(str(tmp_path))
    srv = make_server(str(tmp_path))
    rows = map_realtime.matrix(map_realtime.scan(app, srv))
    q = next(r for r in rows if r["event"] == "question_created")
    assert q["actor_b"] == "phx_actor"  # only another actor can trigger it
    assert "B41" in q["bugs"] or "B43" in q["bugs"]


# ---------- sim_session (fake xcrun) ----------

@pytest.fixture
def fake_xcrun(tmp_path, monkeypatch):
    log = tmp_path / "xcrun.log"
    state = tmp_path / "state.json"
    state.write_text(json.dumps({"devices": {}}))
    script = tmp_path / "xcrun"
    script.write_text(textwrap.dedent(f"""\
        #!/usr/bin/env python3
        import json, sys, uuid
        args = sys.argv[1:]
        open({str(log)!r}, "a").write(" ".join(args) + "\\n")
        state = json.load(open({str(state)!r}))
        if args[:2] == ["simctl", "list"]:
            devs = [{{"udid": u, "name": d["name"], "state": d["state"], "isAvailable": True}} for u, d in state["devices"].items()]
            print(json.dumps({{"devices": {{"com.apple.CoreSimulator.SimRuntime.iOS-26-0": devs}},
                              "devicetypes": [{{"identifier": "com.apple.CoreSimulator.SimDeviceType.iPhone-17", "name": "iPhone 17"}}],
                              "runtimes": [{{"identifier": "com.apple.CoreSimulator.SimRuntime.iOS-26-0", "name": "iOS 26.0", "isAvailable": True}}]}}))
        elif args[:2] == ["simctl", "create"]:
            u = str(uuid.uuid4()).upper(); state["devices"][u] = {{"name": args[2], "state": "Shutdown"}}; print(u)
        elif args[:2] == ["simctl", "boot"]:
            state["devices"][args[2]]["state"] = "Booted"
        elif args[:2] == ["simctl", "shutdown"]:
            for u in ([args[2]] if args[2] != "all" else list(state["devices"])):
                state["devices"][u]["state"] = "Shutdown"
        elif args[:2] == ["simctl", "delete"]:
            state["devices"].pop(args[2], None)
        json.dump(state, open({str(state)!r}, "w"))
    """))
    script.chmod(0o755)
    monkeypatch.setattr(sim_session, "XCRUN", str(script))
    return log


def test_sim_session_creates_prefixed_devices_and_cleans_only_its_own(fake_xcrun, tmp_path):
    session = sim_session.Session(prefix="ceo-", artifacts=str(tmp_path / "runs"))
    a = session.create("papelA", device_type="iPhone 17", runtime="iOS 26.0", boot=True)
    b = session.create("papelB", device_type="iPhone 17", runtime="iOS 26.0", boot=False)
    names = {d["name"] for d in sim_session.list_devices()}
    assert {"ceo-papelA", "ceo-papelB"} <= names
    # a device that is not ours must survive cleanup
    subprocess.run([sim_session.XCRUN, "simctl", "create", "Meu iPhone", "x", "y"], check=True)
    (tmp_path / "runs" / "old.mov").parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / "runs" / "old.mov").write_bytes(b"0")
    removed = session.cleanup()
    assert set(removed["devices"]) == {a, b}
    assert "old.mov" in removed["artifacts"][0]
    assert {d["name"] for d in sim_session.list_devices()} == {"Meu iPhone"}
    assert not (tmp_path / "runs" / "old.mov").exists()


def test_sim_session_refuses_more_than_max(fake_xcrun, tmp_path):
    session = sim_session.Session(prefix="ceo-", artifacts=str(tmp_path / "r"), max_devices=1)
    session.create("a", device_type="iPhone 17", runtime="iOS 26.0")
    with pytest.raises(sim_session.TooManySimulators):
        session.create("b", device_type="iPhone 17", runtime="iOS 26.0")


def test_sim_session_plan_is_dry_run(fake_xcrun, tmp_path):
    out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "sim_session.py"), "plan", "--roles", "admin,user", "--ram-gb", "16"],
                         capture_output=True, text=True, env={**os.environ, "CEO_XCRUN": sim_session.XCRUN})
    assert out.returncode == 0, out.stderr
    assert "1 simulador" in out.stdout and "phx_actor" in out.stdout
    assert not fake_xcrun.exists() or fake_xcrun.read_text().count("create") == 0


# ---------- video_frames (ffmpeg optional) ----------

def test_video_frames_builds_commands_without_running():
    import video_frames
    cmds = video_frames.commands("bug.mp4", "out", threshold=0.3)
    joined = " ".join(" ".join(c) for c in cmds)
    assert ("-fps_mode vfr" in joined) != ("-vsync vfr" in joined)  # exactly one, chosen by the local ffmpeg
    assert "scene" in joined and "tile=" in joined


@pytest.mark.skipif(subprocess.run(["which", "ffmpeg"], capture_output=True).returncode != 0, reason="no ffmpeg")
def test_video_frames_extracts_scene_changes(tmp_path):
    import video_frames
    video = tmp_path / "v.mp4"
    # 2 s of red then 2 s of blue: exactly one scene change
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "color=red:s=64x64:d=2", "-f", "lavfi", "-i",
                    "color=blue:s=64x64:d=2", "-filter_complex", "[0][1]concat=n=2:v=1", "-pix_fmt", "yuv420p", str(video)], check=True)
    result = video_frames.extract(str(video), str(tmp_path / "out"), threshold=0.3)
    assert len(result["scene_frames"]) >= 1
    assert os.path.exists(result["contact_sheet"])
    assert result["scene_times"][0] == pytest.approx(2.0, abs=0.2)


# ---------- phx_actor (node, fake ws server) ----------

@pytest.mark.skipif(subprocess.run(["which", "node"], capture_output=True).returncode != 0, reason="no node")
def test_phx_actor_joins_pushes_and_records_events(tmp_path):
    out = subprocess.run(["node", os.path.join(SCRIPTS, "tests", "fake_phoenix.mjs"), os.path.join(SCRIPTS, "phx_actor.mjs")],
                         capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr + out.stdout
    log = json.loads(out.stdout.strip().splitlines()[-1])
    assert log["joined"] == "class:1"
    assert log["pushed"][0]["event"] == "send_answer" and log["pushed"][0]["status"] == "ok"
    assert any(e["event"] == "question_created" for e in log["received"])
    assert log["script_steps_ok"] >= 2


# ---------- search / lint / packaging ----------

def test_search_finds_double_tap_bug():
    hits = search.search("toque duplo duplicado", domains=["bugs"], limit=3)
    assert hits and hits[0]["id"] == "B01"


def test_search_finds_simctl_recipe():
    hits = search.search("gravar video simulador", domains=["recipes"], limit=3)
    assert any(h["id"] == "T16" for h in hits)


def test_lint_accepts_good_bug_report():
    good = (
        "**Veredito:** fluxo principal passa; 2 bugs reproduzidos.\n"
        "- **P0** Resposta enviada duas vezes com toque duplo [repro: B01, flow double-tap.yaml] `src/lib/socket.ts:9`\n"
        "- **P1** Sheet não fecha após erro [video: runs/sheet.mov 00:12]\n"
    )
    assert lint_report.lint(good, max_words=400) == []


def test_lint_rejects_bug_without_evidence_and_em_dash():
    bad = "- **P0** O app trava às vezes — precisa investigar\n"
    rules = {r for _, r, _ in lint_report.lint(bad, max_words=400)}
    assert {"no-evidence", "em-dash"} <= rules


def test_every_file_cited_in_skill_md_exists():
    skill_md = open(os.path.join(SKILL, "SKILL.md"), encoding="utf-8").read()
    cited = set(re.findall(r"`((?:references|scripts|data|assets|agents)/[\w./-]+)`", skill_md))
    assert cited, "SKILL.md cites no bundled file"
    missing = [c for c in cited if not os.path.exists(os.path.join(SKILL, c))]
    assert missing == []
    names = os.listdir(os.path.join(SKILL, "references"))
    for short in set(re.findall(r"`(\d\d-[\w-]+\.md)`", skill_md)):
        assert short in names, short


def test_data_rows_have_sources_and_unique_ids():
    import csv
    for name in ("bugs", "recipes", "tours"):
        rows = list(csv.DictReader(open(os.path.join(SKILL, "data", f"{name}.csv"), encoding="utf-8")))
        ids = [r["id"] for r in rows]
        assert len(ids) == len(set(ids)), name
        assert all(r["source"].strip() for r in rows), name


def test_maestro_templates_are_valid_yaml_and_use_env():
    import yaml  # type: ignore
    folder = os.path.join(SKILL, "assets", "maestro")
    files = [f for f in os.listdir(folder) if f.endswith(".yaml")]
    assert len(files) >= 6
    for f in files:
        docs = list(yaml.safe_load_all(open(os.path.join(folder, f), encoding="utf-8")))
        assert docs[0].get("appId") == "${APP_ID}", f
        assert isinstance(docs[1], list) and docs[1], f
