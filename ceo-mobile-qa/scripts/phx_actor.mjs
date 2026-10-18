#!/usr/bin/env node
// Second actor for multi-user tests: a Phoenix Channels client that joins a topic, pushes events,
// waits for events and prints a JSON log. No dependencies: speaks the Phoenix v2 wire protocol
// over Node's built-in WebSocket (Node 22+).
//
// Usage:
//   node phx_actor.mjs --url ws://localhost:4000/socket --topic class:1 --params '{"token":"..."}' \
//        --script steps.json [--role admin] [--duration 20000] [--verbose]
//
// steps.json is a list, executed in order:
//   {"push": "send_answer", "payload": {"text": "42"}}          push and wait for the reply (ok/error/timeout)
//   {"wait": "question_created", "timeout": 5000}                wait for an event from the server
//   {"sleep": 500}                                               pause (ms)
//   {"disconnect": true} / {"reconnect": true}                   simulate a drop and a rejoin
//   {"repeat": 5, "push": "send_answer", "payload": {}, "interval": 40}   double-tap style burst
// Exit code 0 when every step succeeded, 1 otherwise. The last stdout line is always the JSON log:
// {"role","joined","pushed":[{event,status,ms}],"received":[{event,at,payload}],"script_steps_ok","errors"}
import fs from "node:fs";

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, all) => {
  if (a.startsWith("--")) acc.push([a.slice(2), all[i + 1] && !all[i + 1].startsWith("--") ? all[i + 1] : true]);
  return acc;
}, []));
if (!args.url || !args.topic) {
  console.error("usage: node phx_actor.mjs --url ws://host:4000/socket --topic <topic> [--params JSON] [--script file|JSON] [--role name]");
  process.exit(2);
}
const verbose = !!args.verbose;
const role = args.role || "actor";
const params = args.params ? JSON.parse(args.params) : {};
const steps = args.script ? (fs.existsSync(args.script) ? JSON.parse(fs.readFileSync(args.script, "utf8")) : JSON.parse(args.script)) : [];
const duration = Number(args.duration || 15000);
const log = { role, joined: null, pushed: [], received: [], script_steps_ok: 0, errors: [] };

const endpoint = (url) => {
  const u = new URL(url.replace(/\/$/, "") + (url.includes("/websocket") ? "" : "/websocket"));
  u.searchParams.set("vsn", "2.0.0");
  for (const [k, v] of Object.entries(params)) u.searchParams.set(k, String(v));
  return u.toString();
};

class Actor {
  constructor() { this.ref = 0; this.pending = new Map(); this.waiters = []; this.ws = null; this.joinRef = null; this.heartbeat = null; }
  nextRef() { return String(++this.ref); }
  connect() {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(endpoint(args.url));
      this.ws = ws;
      ws.addEventListener("open", () => { this.heartbeat = setInterval(() => this.send([null, this.nextRef(), "phoenix", "heartbeat", {}]), 30000); resolve(); });
      ws.addEventListener("error", (e) => { log.errors.push(`socket error: ${e.message || "unknown"}`); reject(new Error("socket error")); });
      ws.addEventListener("close", (e) => { clearInterval(this.heartbeat); log.received.push({ event: "phx_close", at: Date.now(), payload: { code: e.code } }); });
      ws.addEventListener("message", (m) => this.onMessage(JSON.parse(m.data)));
    });
  }
  send(frame) { if (verbose) console.error("→", JSON.stringify(frame)); this.ws.send(JSON.stringify(frame)); }
  onMessage([joinRef, ref, topic, event, payload]) {
    if (verbose) console.error("←", JSON.stringify([joinRef, ref, topic, event, payload]));
    if (event === "phx_reply" && this.pending.has(ref)) {
      const { resolve, started } = this.pending.get(ref);
      this.pending.delete(ref);
      resolve({ status: payload.status, response: payload.response, ms: Date.now() - started });
      return;
    }
    if (topic !== args.topic) return;
    log.received.push({ event, at: Date.now(), payload });
    this.waiters = this.waiters.filter((w) => (w.event === event ? (w.resolve(payload), false) : true));
  }
  request(event, payload, timeout = 10000) {
    const ref = this.nextRef();
    const started = Date.now();
    return new Promise((resolve) => {
      const timer = setTimeout(() => { if (this.pending.delete(ref)) resolve({ status: "timeout", ms: Date.now() - started }); }, timeout);
      this.pending.set(ref, { resolve: (r) => { clearTimeout(timer); resolve(r); }, started });
      this.send([this.joinRef, ref, args.topic, event, payload]);
    });
  }
  async join() {
    this.joinRef = this.nextRef();
    const ref = this.joinRef;
    const started = Date.now();
    const reply = await new Promise((resolve) => {
      this.pending.set(ref, { resolve, started });
      this.send([this.joinRef, ref, args.topic, "phx_join", params]);
    });
    if (reply.status !== "ok") throw new Error(`join ${args.topic} failed: ${JSON.stringify(reply.response)}`);
    log.joined = args.topic;
  }
  waitFor(event, timeout) {
    return new Promise((resolve, reject) => {
      const already = log.received.find((r) => r.event === event && !r.consumed);
      if (already) { already.consumed = true; return resolve(already.payload); }
      const timer = setTimeout(() => { this.waiters = this.waiters.filter((w) => w.resolve !== ok); reject(new Error(`timeout waiting ${event}`)); }, timeout);
      const ok = (p) => { clearTimeout(timer); resolve(p); };
      this.waiters.push({ event, resolve: ok });
    });
  }
  close() { clearInterval(this.heartbeat); if (this.ws && this.ws.readyState <= 1) this.ws.close(); }
}

const actor = new Actor();
const deadline = setTimeout(() => { log.errors.push(`duration ${duration}ms exceeded`); finish(1); }, duration);

function finish(code) {
  clearTimeout(deadline);
  actor.close();
  console.log(JSON.stringify(log));
  process.exit(code);
}

async function run() {
  await actor.connect();
  await actor.join();
  for (const step of steps) {
    try {
      if (step.push) {
        const times = step.repeat || 1;
        for (let i = 0; i < times; i++) {
          const p = actor.request(step.push, step.payload || {}, step.timeout);
          if (step.interval && i < times - 1) await new Promise((r) => setTimeout(r, step.interval));
          const reply = await p;
          log.pushed.push({ event: step.push, status: reply.status, ms: reply.ms, response: reply.response });
          if (reply.status !== (step.expect_status || "ok")) throw new Error(`push ${step.push}: ${reply.status}`);
        }
      } else if (step.wait) {
        await actor.waitFor(step.wait, step.timeout || 5000);
      } else if (step.sleep) {
        await new Promise((r) => setTimeout(r, step.sleep));
      } else if (step.disconnect) {
        actor.close();
      } else if (step.reconnect) {
        await actor.connect();
        await actor.join();
        log.received.push({ event: "phx_rejoin", at: Date.now(), payload: {} });
      }
      log.script_steps_ok += 1;
    } catch (error) {
      log.errors.push(`step ${JSON.stringify(step)}: ${error.message}`);
      if (!step.continue_on_error) return finish(1);
    }
  }
  finish(log.errors.length ? 1 : 0);
}

run().catch((error) => { log.errors.push(error.message); finish(1); });
