// N clientes Phoenix Channels por sala: join, heartbeat, um push por segundo; mede p95 do phx_reply.
// k6 run --vus 50 --duration 60s -e WS_URL=ws://localhost:4000/socket -e TOPIC=room:1 -e TOKEN=xxx -e EVENT=ping assets/k6-phoenix-ws.js
// Fonte do protocolo: serializer v2 [join_ref, ref, topic, event, payload]
// https://raw.githubusercontent.com/phoenixframework/phoenix/main/assets/js/phoenix/serializer.js
import { WebSocket } from 'k6/websockets';
import { Trend, Counter } from 'k6/metrics';
import { check, sleep } from 'k6';

const replyMs = new Trend('phx_reply_ms', true);
const joinFail = new Counter('phx_join_failures');
const broadcasts = new Counter('phx_broadcasts_received');

const url = `${__ENV.WS_URL}/websocket?vsn=2.0.0${__ENV.TOKEN ? `&token=${__ENV.TOKEN}` : ''}`;
const topic = __ENV.TOPIC || 'room:1';
const event = __ENV.EVENT || 'ping';

export const options = {
  thresholds: { phx_reply_ms: ['p(95)<500'], phx_join_failures: ['count==0'] },
};

export default function () {
  const ws = new WebSocket(url);
  let ref = 0;
  const pending = {};
  const send = (frame) => ws.send(JSON.stringify(frame));
  const next = () => String(++ref);

  ws.addEventListener('open', () => {
    const joinRef = next();
    pending[joinRef] = Date.now();
    send([joinRef, joinRef, topic, 'phx_join', {}]);
    const hb = setInterval(() => send([null, next(), 'phoenix', 'heartbeat', {}]), 30000);
    const pusher = setInterval(() => {
      const r = next();
      pending[r] = Date.now();
      send([joinRef, r, topic, event, { vu: __VU, t: Date.now() }]);
    }, 1000);
    setTimeout(() => { clearInterval(hb); clearInterval(pusher); ws.close(); }, 20000);
  });

  ws.addEventListener('message', (m) => {
    const [, r, t, ev, payload] = JSON.parse(m.data);
    if (ev === 'phx_reply' && pending[r]) {
      replyMs.add(Date.now() - pending[r]);
      if (r === '1') check(payload, { 'join ok': (p) => p.status === 'ok' }) || joinFail.add(1);
      delete pending[r];
    } else if (t === topic) {
      broadcasts.add(1);
    }
  });

  ws.addEventListener('error', () => joinFail.add(1));
  sleep(1);
}
