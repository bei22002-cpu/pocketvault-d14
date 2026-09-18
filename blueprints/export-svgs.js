/**
 * Export printable SVG orthographic sheets for all Nereid designs.
 * Run: node blueprints/export-svgs.js
 */
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const designsPath = path.join(__dirname, "designs.js");
const outDir = path.join(__dirname, "svg");
fs.mkdirSync(outDir, { recursive: true });

const sandbox = { window: {} };
vm.runInNewContext(fs.readFileSync(designsPath, "utf8"), sandbox);
const designs = sandbox.window.NEREID_DESIGNS;

function dimLine(x1, y1, x2, y2, label, opts = {}) {
  const offset = opts.offset ?? 14;
  const horizontal = Math.abs(y2 - y1) < 0.1;
  let ax1, ay1, ax2, ay2, tx, ty;
  if (horizontal) {
    ay1 = ay2 = y1 + (opts.side === "up" ? -offset : offset);
    ax1 = x1;
    ax2 = x2;
    tx = (x1 + x2) / 2;
    ty = ay1 + (opts.side === "up" ? -4 : 12);
  } else {
    ax1 = ax2 = x1 + (opts.side === "left" ? -offset : offset);
    ay1 = y1;
    ay2 = y2;
    tx = ax1 + (opts.side === "left" ? -4 : 8);
    ty = (y1 + y2) / 2 + 4;
  }
  return `
    <line x1="${x1}" y1="${y1}" x2="${ax1}" y2="${ay1}" stroke="#5a6a4a" stroke-width="0.6" />
    <line x1="${x2}" y1="${y2}" x2="${ax2}" y2="${ay2}" stroke="#5a6a4a" stroke-width="0.6" />
    <line x1="${ax1}" y1="${ay1}" x2="${ax2}" y2="${ay2}" stroke="#5a6a4a" stroke-width="0.8" />
    <text x="${tx}" y="${ty}" fill="#3d4a32" font-size="9" font-family="sans-serif" text-anchor="middle">${label}</text>
  `;
}

function buildSvg(d) {
  const ox = 40,
    oy = 36;
  const scale = 2.2;
  const L = d.outer.L * scale,
    W = d.outer.W * scale,
    H = d.outer.H * scale;
  const aL = d.aperture.L * scale,
    aW = d.aperture.W * scale;
  const ax = ox + (L - aL) / 2,
    ay = oy + (W - aW) / 2;
  const sx = ox + L + 70,
    sy = oy;
  const stack = [
    { label: "Shell", h: Math.max(8, (typeof d.shell.t === "number" ? d.shell.t : 1.5) * scale * 2) },
    { label: "Seal", h: 4 },
    { label: "Window " + d.window.t + "mm", h: Math.max(6, d.window.t * scale * 3) },
    { label: "Air pocket", h: 14 },
    { label: "Phone", h: 18 },
    { label: "Back", h: 10 },
  ];
  let stackY = sy + 10;
  const stackRects = stack
    .map((s) => {
      const r = `<rect x="${sx}" y="${stackY}" width="${H}" height="${s.h}" fill="none" stroke="#1a1a1a" stroke-width="1.1" />
        <text x="${sx + H + 8}" y="${stackY + s.h / 2 + 3}" fill="#333" font-size="9" font-family="sans-serif">${s.label}</text>`;
      stackY += s.h;
      return r;
    })
    .join("");

  const senseHint =
    d.sensing === "Load cell"
      ? `
        <circle cx="${ax + 8}" cy="${ay + 8}" r="3.5" fill="none" stroke="#1a1a1a" />
        <circle cx="${ax + aL - 8}" cy="${ay + 8}" r="3.5" fill="none" stroke="#1a1a1a" />
        <circle cx="${ax + 8}" cy="${ay + aW - 8}" r="3.5" fill="none" stroke="#1a1a1a" />
        <circle cx="${ax + aL - 8}" cy="${ay + aW - 8}" r="3.5" fill="none" stroke="#1a1a1a" />
      `
      : "";

  const title = `${d.id} · ${d.name.toUpperCase()}`;
  const vbW = sx + H + 160;
  const vbH = Math.max(oy + W + 70, stackY + 40);

  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${vbW} ${vbH}" width="${vbW}" height="${vbH}">
  <rect width="100%" height="100%" fill="#f4f1ea" />
  <text x="20" y="18" font-size="12" font-weight="600" font-family="sans-serif" fill="#1a1a1a">${title}</text>
  <text x="20" y="30" font-size="8" font-family="sans-serif" fill="#666">FRONT ELEVATION — ~2.2 px/mm · Nereid Rev A</text>
  <rect x="${ox}" y="${oy}" width="${L}" height="${W}" fill="#fff" stroke="#1a1a1a" stroke-width="1.6" />
  <rect x="${ax}" y="${ay}" width="${aL}" height="${aW}" fill="#e8ece8" stroke="#1a1a1a" stroke-width="1.1" />
  <text x="${ax + aL / 2}" y="${ay + aW / 2}" text-anchor="middle" font-size="9" fill="#555" font-family="sans-serif">${d.window.material}</text>
  ${senseHint}
  ${dimLine(ox, oy + W, ox + L, oy + W, d.outer.L + " mm", { side: "down" })}
  ${dimLine(ox + L, oy, ox + L, oy + W, d.outer.W + " mm", { side: "right" })}
  ${dimLine(ax, ay, ax + aL, ay, "AP " + d.aperture.L + " mm", { side: "up", offset: 10 })}
  <text x="${sx}" y="${sy - 6}" font-size="9" font-weight="600" fill="#1a1a1a" font-family="sans-serif">SECTION STACK</text>
  ${stackRects}
  ${dimLine(sx, sy + 10, sx + H, sy + 10, d.outer.H + " mm H", { side: "up", offset: 8 })}
  <text x="20" y="${vbH - 28}" font-size="8" fill="#444" font-family="sans-serif">Shell: ${d.shell.material} · Mount: ${d.window.mount}</text>
  <text x="20" y="${vbH - 16}" font-size="8" fill="#444" font-family="sans-serif">Depth ${d.depthM} m · ${d.weightG} g · ${d.sensing}</text>
  <rect x="${vbW - 150}" y="${vbH - 42}" width="130" height="30" fill="none" stroke="#1a1a1a" stroke-width="0.8" />
  <text x="${vbW - 140}" y="${vbH - 28}" font-size="8" fill="#1a1a1a" font-family="sans-serif">NEREID PROGRAM</text>
  <text x="${vbW - 140}" y="${vbH - 16}" font-size="8" fill="#1a1a1a" font-family="sans-serif">DWG ${d.id}-00 · REV A</text>
</svg>`;
}

for (const d of designs) {
  const file = path.join(outDir, `${d.id}-${d.name.toLowerCase().replace(/\s+/g, "-")}.svg`);
  fs.writeFileSync(file, buildSvg(d), "utf8");
  console.log("Wrote", path.basename(file));
}
console.log("Done:", designs.length, "SVG sheets →", outDir);
