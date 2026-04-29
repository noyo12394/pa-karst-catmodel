import { copyFile, cp, mkdir, rm, stat } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const source = join(root, "dashboard");
const target = join(root, "dist");
const files = ["index.html", "styles.css", "app.js"];

await rm(target, { recursive: true, force: true });
await mkdir(target, { recursive: true });

for (const file of files) {
  await copyFile(join(source, file), join(target, file));
}

await cp(join(source, "assets"), join(target, "assets"), { recursive: true });

try {
  await stat(join(source, "downloads"));
  await cp(join(source, "downloads"), join(target, "downloads"), { recursive: true });
} catch {
  // Downloads are optional in local development.
}

console.log(`Dashboard build complete: ${target}`);
