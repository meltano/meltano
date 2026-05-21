/**
 * Downloads api/ blobs from an Azure Blob container into _snippets.
 *
 * Required env vars:
 *   AZURE_STORAGE_CONNECTION_STRING - Azure Storage connection string
 *   AZURE_STORAGE_CONTAINER         - blob container name
 *
 * Optional:
 *   SNIPPETS_EXCLUDE - comma-separated list of glob patterns to skip (supports * and **)
 */

import { BlobServiceClient } from '@azure/storage-blob';
import { access, mkdir } from 'node:fs/promises';
import { dirname, join } from 'node:path';
import { minimatch } from 'minimatch';

const OUTPUT_DIR = 'docs/reference/cloud/api/resources/_snippets';
const PREFIX = 'api/';

async function main() {
  await access(OUTPUT_DIR);

  const connStr = process.env.AZURE_STORAGE_CONNECTION_STRING;
  if (!connStr) throw new Error('AZURE_STORAGE_CONNECTION_STRING is required');

  const container = process.env.AZURE_STORAGE_CONTAINER;
  if (!container) throw new Error('AZURE_STORAGE_CONTAINER is required');

  const excludeGlobs = process.env.SNIPPETS_EXCLUDE?.split(',') ?? [];

  const containerClient = BlobServiceClient.fromConnectionString(connStr).getContainerClient(container);

  const downloads = [];

  for await (const blob of containerClient.listBlobsFlat({ prefix: PREFIX })) {
    if (excludeGlobs.some((p) => minimatch(blob.name, p))) {
      console.log(`  skipped: ${blob.name}`);
      continue;
    }
    const localPath = join(OUTPUT_DIR, blob.name.slice(PREFIX.length));
    const download = mkdir(dirname(localPath), { recursive: true })
      .then(() => containerClient.getBlobClient(blob.name).downloadToFile(localPath))
      .then(() => console.log(`  downloaded: ${blob.name} → ${localPath}`));
    downloads.push(download);
  }

  if (downloads.length === 0) {
    console.warn(`No blobs found in container "${container}" with prefix "${PREFIX}"`);
    return;
  }

  await Promise.all(downloads);
  console.log(`Downloaded ${downloads.length} snippet(s)`);
}

main().catch((err) => {
  console.error('download-api-snippets failed:', err.message);
  process.exit(1);
});
