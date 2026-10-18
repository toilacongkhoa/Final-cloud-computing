import test from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { request } from 'node:http';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { createApp } from '../src/server.js';

for (const [release, version] of [['blue', '1.0.0'], ['green', '2.0.0']]) {
  test(`${release}: page and API report the same release`, async (t) => {
    const logs = [];
    const server = createApp(release, (line) => logs.push(JSON.parse(line)));
    server.listen(0, '127.0.0.1');
    await once(server, 'listening');
    t.after(() => new Promise((resolve) => server.close(resolve)));
    const base = `http://127.0.0.1:${server.address().port}`;

    const page = await fetch(base);
    assert.equal(page.status, 200);
    assert.equal(page.headers.get('cache-control'), 'no-store');
    const html = await page.text();
    assert.ok(html.includes(`data-color="${release}"`));
    assert.ok(html.includes(`v${version}`));
    assert.ok(!html.includes('{{'));

    const info = await (await fetch(`${base}/version`)).json();
    assert.equal(info.version, version);
    assert.equal(info.color, release);
    assert.ok(info.hostname);
    assert.ok(Number.isFinite(Date.parse(info.startedAt)));
    const health = await fetch(`${base}/health`);
    assert.equal(health.status, 200);
    assert.deepEqual(await health.json(), { status: 'ok' });
    const css = await fetch(`${base}/styles.css`);
    assert.equal(css.status, 200);
    assert.match(css.headers.get('content-type'), /text\/css/);
    assert.ok((await css.text()).includes('[data-color="green"]'));
    assert.equal((await fetch(`${base}/version?sample=1`)).status, 200);
    assert.equal((await fetch(`${base}/releases/blue.json`)).status, 404);
    const forbidden = await fetch(`${base}/version`, { method: 'POST' });
    assert.equal(forbidden.status, 405);
    assert.equal(forbidden.headers.get('allow'), 'GET, HEAD');
    const head = await fetch(`${base}/health`, { method: 'HEAD' });
    assert.equal(head.status, 200);
    assert.equal(await head.text(), '');
    assert.ok(logs.some((entry) => entry.path === '/version' && entry.color === release));
  });
}

test('rejects an unknown release instead of silently running the wrong version', () => {
  assert.throws(() => createApp('../private'), /APP_RELEASE must be blue or green/);
});

test('a malformed request returns 400 without crashing the server', async (t) => {
  const server = createApp('blue', () => {});
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(() => new Promise((resolve) => server.close(resolve)));
  const port = server.address().port;
  const result = await new Promise((resolve, reject) => {
    const req = request({ hostname: '127.0.0.1', port, path: 'http://[' }, (res) => {
      res.resume();
      res.on('end', () => resolve(res.statusCode));
    });
    req.on('error', reject);
    req.end();
  });
  assert.equal(result, 400);
  assert.equal((await fetch(`http://127.0.0.1:${port}/health`)).status, 200);
});

const serverPath = fileURLToPath(new URL('../src/server.js', import.meta.url));
for (const scenario of [
  { name: 'invalid port', env: { PORT: '-1' }, args: [], error: /PORT must be/ },
  { name: 'invalid release', env: { APP_RELEASE: 'purple' }, args: [], error: /APP_RELEASE must be/ },
  { name: 'unknown CLI option', env: {}, args: ['--unknown'], error: /Usage:/ }
]) {
  test(`startup rejects ${scenario.name}`, () => {
    const result = spawnSync(process.execPath, [serverPath, ...scenario.args], {
      env: { ...process.env, PORT: '8080', APP_RELEASE: 'blue', ...scenario.env },
      encoding: 'utf8', timeout: 5000
    });
    assert.equal(result.status, 1);
    assert.match(result.stderr, scenario.error);
  });
}
