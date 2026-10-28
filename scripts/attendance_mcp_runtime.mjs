// Helper declarations for the connected functions.exec runtime; no automatic
// execution, remote writes, retries or credentials. All captured data is private.
const root = '/workspace/kc2-integrated-data-system-vidhan';
const project = 'hmlbdozsqxlwzvjimjwh';
const evidenceDirectory = globalThis.ATTENDANCE_EVIDENCE_DIRECTORY ?? 'work/attendance-resumption';
if (!['work/attendance-resumption', 'work/attendance-prefix172'].includes(evidenceDirectory)) {
  throw Error('Unapproved private evidence directory');
}
const run = async cmd => {
  let r = await tools.exec_command({ cmd, workdir: root, max_output_tokens: 18000, yield_time_ms: 1000 });
  let out = r.output;
  while (r.exit_code === undefined) {
    r = await tools.write_stdin({ session_id: r.session_id, chars: '', max_output_tokens: 18000, yield_time_ms: 1000 });
    out += r.output;
  }
  if (r.exit_code !== 0) throw Error('Local evidence command failed');
  return out;
};
const moduleLoad = code => {
  const module = { exports: {} };
  return new Function('module', 'exports', 'require', 'process', code + ';return module.exports;')(module, module.exports, undefined, undefined);
};
const zip = moduleLoad(await run('cat scripts/vendor/fflate-0.8.2.js'));
const hash = moduleLoad(await run('cat scripts/vendor/js-sha256-0.11.1.js'));
const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
const b64encode = bytes => {
  let out = '';
  for (let i = 0; i < bytes.length; i += 3) {
    const n = (bytes[i] << 16) | ((bytes[i + 1] || 0) << 8) | (bytes[i + 2] || 0);
    out += alphabet[n >>> 18 & 63] + alphabet[n >>> 12 & 63] + (i + 1 < bytes.length ? alphabet[n >>> 6 & 63] : '=') + (i + 2 < bytes.length ? alphabet[n & 63] : '=');
  }
  return out;
};
const save = async (name, value) => {
  if (!/^[a-z0-9-]+\.json$/.test(name)) throw Error('Invalid evidence filename');
  const encoded = b64encode(zip.gzipSync(zip.strToU8(JSON.stringify(value))));
  await run("work/review-venv/bin/python -c \"from pathlib import Path; p=Path('" + evidenceDirectory + "/" + name + ".gz'); p.touch(mode=0o600); p.chmod(0o600); p.write_bytes(b'')\"");
  for (let at = 0; at < encoded.length; at += 12000) {
    await run("work/review-venv/bin/python -c \"import base64; from pathlib import Path; f=Path('" + evidenceDirectory + "/" + name + ".gz').open('ab'); f.write(base64.b64decode('" + encoded.slice(at, at + 12000) + "')); f.close()\"");
  }
  await run("work/review-venv/bin/python -c \"import gzip; from pathlib import Path; p=Path('" + evidenceDirectory + "/" + name + "'); p.touch(mode=0o600); p.chmod(0o600); p.write_bytes(gzip.decompress(Path(str(p)+'.gz').read_bytes()))\"");
};
const rows = result => {
  if (result.isError) throw Error('Supabase read failed');
  const parsed = JSON.parse(result.content.find(x => x.type === 'text').text);
  const match = parsed.result?.match(/\n<untrusted-data-([^>]+)>\s*([\s\S]*?)\s*<\/untrusted-data-\1>/);
  if (!match) throw Error('Unexpected SQL response wrapper');
  return JSON.parse(match[2]);
};
