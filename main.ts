import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const png = readFileSync(fileURLToPath(new URL('./entry.png', import.meta.url)));
const signature = Buffer.from('89504e470d0a1a0a', 'hex');

if (!png.subarray(0, signature.length).equals(signature)) {
  throw new Error('entry.png has an invalid PNG signature');
}
if (png.length > 1048576) {
  throw new Error('entry.png exceeds 1048576 bytes');
}
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
if (width < 1 || width > 1024 || height < 1 || height > 1024) {
  throw new Error('entry.png dimensions must be between 1 and 1024 pixels');
}

const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
mkdirSync(outputDir, { recursive: true });
writeFileSync(join(outputDir, 'entry.png'), png);
console.log(`Wrote ${png.length} bytes to entry.png`);
