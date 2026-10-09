// Minimal Phoenix-like WebSocket server (no deps) used to test phx_actor.mjs.
// Usage: node fake_phoenix.mjs <path to phx_actor.mjs>
// Accepts phx_join on any topic, replies ok to "send_answer", broadcasts "question_created" 300 ms
// after the join, then runs the actor as a child with a 3-step script and relays its JSON log.
import http from "node:http";
import crypto from "node:crypto";
import { spawn } from "node:child_process";

const GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";

function decodeFrame(buffer) {
  const second = buffer[1];
  const masked = (second & 0x80) !== 0;
  let length = second & 0x7f;
  let offset = 2;
  if (length === 126) { length = buffer.readUInt16BE(2); offset = 4; }
  else if (length === 127) { length = Number(buffer.readBigUInt64BE(2)); offset = 10; }
  let payload = buffer.subarray(offset + (masked ? 4 : 0), offset + (masked ? 4 : 0) + length);
  if (masked) {
    const mask = buffer.subarray(offset, offset + 4);
    payload = Buffer.from(payload.map((b, i) => b ^ mask[i % 4]));
  }
  return { opcode: buffer[0] & 0x0f, text: payload.toString("utf8"), size: offset + (masked ? 4 : 0) + length };
}

function encodeText(text) {
  const payload = Buffer.from(text, "utf8");
  let header;
  if (payload.length < 126) header = Buffer.from([0x81, payload.length]);
  else { header = Buffer.alloc(4); header[0] = 0x81; header[1] = 126; header.writeUInt16BE(payload.length, 2); }
  return Buffer.concat([header, payload]);
}

const server = http.createServer();
server.on("upgrade", (req, socket) => {
  const accept = crypto.createHash("sha1").update(req.headers["sec-websocket-key"] + GUID).digest("base64");
  socket.write(["HTTP/1.1 101 Switching Protocols", "Upgrade: websocket", "Connection: Upgrade", `Sec-WebSocket-Accept: ${accept}`, "", ""].join("\r\n"));
  const send = (frame) => socket.write(encodeText(JSON.stringify(frame)));
  let buffered = Buffer.alloc(0);
  socket.on("data", (chunk) => {
    buffered = Buffer.concat([buffered, chunk]);
    while (buffered.length >= 2) {
      const frame = decodeFrame(buffered);
      if (buffered.length < frame.size) break;
      buffered = buffered.subarray(frame.size);
      if (frame.opcode === 8) { socket.end(); return; }
      if (frame.opcode !== 1) continue;
      const [joinRef, ref, topic, event, payload] = JSON.parse(frame.text);
      if (event === "phx_join") {
        send([joinRef, ref, topic, "phx_reply", { status: "ok", response: {} }]);
        setTimeout(() => send([null, null, topic, "question_created", { id: 7, text: "2+2?" }]), 300);
      } else if (event === "heartbeat") {
        send([null, ref, "phoenix", "phx_reply", { status: "ok", response: {} }]);
      } else if (event === "send_answer") {
        send([joinRef, ref, topic, "phx_reply", { status: "ok", response: { echoed: payload } }]);
      } else {
        send([joinRef, ref, topic, "phx_reply", { status: "error", response: { reason: "unmatched" } }]);
      }
    }
  });
  socket.on("error", () => {});
});

server.listen(0, "127.0.0.1", () => {
  const port = server.address().port;
  const script = JSON.stringify([
    { push: "send_answer", payload: { text: "4" } },
    { wait: "question_created", timeout: 3000 },
    { repeat: 3, push: "send_answer", payload: { text: "burst" }, interval: 20 },
  ]);
  const child = spawn(process.execPath, [process.argv[2], "--url", `ws://127.0.0.1:${port}/socket`, "--topic", "class:1",
    "--params", '{"token":"t"}', "--script", script, "--role", "tester", "--duration", "8000"], { stdio: ["ignore", "pipe", "inherit"] });
  let out = "";
  child.stdout.on("data", (d) => { out += d; });
  child.on("exit", (code) => { process.stdout.write(out); server.close(); process.exit(code); });
});
