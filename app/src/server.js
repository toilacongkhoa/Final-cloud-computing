import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';
import { hostname } from 'node:os';
import { pathToFileURL } from 'node:url';

const htmlTemplate = readFileSync(new URL('../public/index.html', import.meta.url), 'utf8');
const stylesheet = readFileSync(new URL('../public/styles.css', import.meta.url), 'utf8');
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[char]));

// One process serves one release. CodeDeploy changes which process receives traffic.
export function createApp(releaseName = 'blue', logger = console.log) {
  if (!['blue', 'green'].includes(releaseName)) {
    throw new Error('APP_RELEASE must be blue or green');
  }
  const release = JSON.parse(readFileSync(new URL(`../releases/${releaseName}.json`, import.meta.url), 'utf8'));
  const metadata = {
    service: 'ecs-bluegreen-demo',
    version: release.version,
    color: release.color,
    hostname: hostname(),
    startedAt: new Date().toISOString()
  };
  const values = { ...metadata, message: release.message, colorLabel: release.color.toUpperCase() };
  const html = htmlTemplate.replace(/\{\{(\w+)\}\}/g, (_, key) => escapeHtml(values[key] ?? ''));

  return createServer((req, res) => {
    let path = req.url;
    res.setHeader('Cache-Control', 'no-store');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.on('finish', () => logger(JSON.stringify({
      time: new Date().toISOString(), method: req.method, path,
      status: res.statusCode, version: metadata.version, color: metadata.color
    })));

    function send(status, contentType, body) {
      res.writeHead(status, { 'Content-Type': contentType });
      res.end(req.method === 'HEAD' ? undefined : body);
    }
    function json(status, data) {
      send(status, 'application/json; charset=utf-8', JSON.stringify(data));
    }

    try {
      path = new URL(req.url, 'http://localhost').pathname;
    } catch {
      return json(400, { error: 'Invalid request URL' });
    }

    if (req.method !== 'GET' && req.method !== 'HEAD') {
      res.setHeader('Allow', 'GET, HEAD');
      return json(405, { error: 'Method not allowed' });
    }
    if (path === '/') return send(200, 'text/html; charset=utf-8', html);
    if (path === '/styles.css') return send(200, 'text/css; charset=utf-8', stylesheet);
    if (path === '/health') return json(200, { status: 'ok' });
    if (path === '/version') return json(200, metadata);
    if (path === '/favicon.ico') return send(204, 'image/x-icon', '');
    return json(404, { error: 'Not found' });
  });
}

// Importing this file in tests does not start a server.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const args = process.argv.slice(2);
    if (args.length && (args.length !== 2 || args[0] !== '--release')) {
      throw new Error('Usage: node app/src/server.js [--release blue|green]');
    }
    const releaseName = args[1] ?? process.env.APP_RELEASE ?? 'blue';
    const port = Number(process.env.PORT ?? 8080);
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      throw new Error('PORT must be an integer between 1 and 65535');
    }
    const server = createApp(releaseName);
    server.on('error', (error) => { console.error(error.message); process.exitCode = 1; });
    server.listen(port, '0.0.0.0', () => {
      console.log(JSON.stringify({ event: 'listening', port, release: releaseName }));
    });
    const shutdown = () => {
      server.close(() => process.exit(0));
      setTimeout(() => process.exit(1), 10000).unref();
    };
    process.once('SIGTERM', shutdown);
    process.once('SIGINT', shutdown);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
