// Real HTTP observations only. Run through a complete deployment, then Ctrl+C.
import { appendFileSync, existsSync, mkdirSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
const base = process.argv[2];
const label = process.argv[3] ?? 'deployment';
const seconds = Number(process.argv[4] ?? 1200);
if (!base || !/^https?:\/\//.test(base)) throw Error('Usage: node infra/aws/monitor.mjs <production-url> <label> [seconds]');
const directory = resolve('evidence/week-03/data');
mkdirSync(directory, { recursive: true });
const file = resolve(directory, `http-${label}.csv`);
writeFileSync(file, 'timestamp,status,latency_ms,version,color,error\n');
const summary = { base, label, startedAt: new Date().toISOString(), requests: 0, ok: 0, failed: 0, versions: {}, maxLatencyMs: 0 };
let stopping = false;
process.on('SIGINT', () => { stopping = true; });
const end = Date.now() + seconds * 1000;
while (!stopping && Date.now() < end && !existsSync(resolve('.local', `monitor-${label}.stop`))) {
  const started = Date.now();
  let status = 0, version = '', color = '', error = '';
  try {
    const response = await fetch(new URL('/version', base), { signal: AbortSignal.timeout(5000) });
    status = response.status;
    const data = await response.json();
    version = data.version ?? ''; color = data.color ?? '';
    if (status === 200 && version && color) summary.ok++;
    else { summary.failed++; error = 'HTTP or release metadata failure'; }
  } catch (e) { summary.failed++; error = e.cause?.code ?? e.name; }
  const latency = Date.now() - started;
  summary.requests++;
  summary.maxLatencyMs = Math.max(summary.maxLatencyMs, latency);
  if (version) summary.versions[version] = (summary.versions[version] ?? 0) + 1;
  appendFileSync(file, `${new Date().toISOString()},${status},${latency},${version},${color},${error}\n`);
  if (summary.requests % 30 === 0) console.log(JSON.stringify(summary));
  await new Promise(r => setTimeout(r, Math.max(0, 1000 - latency)));
}
summary.endedAt = new Date().toISOString();
writeFileSync(resolve(directory, `http-${label}-summary.json`), JSON.stringify(summary, null, 2));
console.log(JSON.stringify(summary, null, 2));
