/**
 * Build-time data loader
 * Reads processed CSVs from ../data/processed/ and writes JSON to public/data/
 */
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'fs';
import { fileURLToPath } from 'url';
import { resolve, dirname, join } from 'path';
import Papa from 'papaparse';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const PROJECT_ROOT = resolve(__dirname, '..');
const PROCESSED_DIR = resolve(PROJECT_ROOT, '../data/processed');
const OUTPUT_DIR = resolve(PROJECT_ROOT, 'public/data');
const CATALOG_PATH = resolve(PROJECT_ROOT, '../config/data_catalog.json');

console.log(`Project root: ${PROJECT_ROOT}`);
console.log(`Processed dir: ${PROCESSED_DIR}`);
console.log(`Output dir: ${OUTPUT_DIR}`);
console.log(`Catalog: ${CATALOG_PATH}`);

const catalogConfig = JSON.parse(readFileSync(CATALOG_PATH, 'utf-8'));
const tables = catalogConfig.datasets;

mkdirSync(OUTPUT_DIR, { recursive: true });

const generatedAt = new Date().toISOString();
const catalog = {
  ...catalogConfig,
  generatedAt,
  datasets: [],
};
const requiredIssues = [];

for (const config of tables) {
  const { input, output } = config;
  const inputPath = join(PROCESSED_DIR, input);
  const outputPath = join(OUTPUT_DIR, output);

  if (!existsSync(inputPath)) {
    const status = config.required ? 'missing_required' : 'missing_optional';
    console.warn(`⚠  Not found: ${inputPath}`);
    writeFileSync(outputPath, JSON.stringify([]));
    catalog.datasets.push({
      ...config,
      status,
      rows: 0,
      columns: [],
      missingFields: config.fields || [],
      bytes: 2,
    });
    if (config.required) requiredIssues.push(`${config.id}: missing ${input}`);
    continue;
  }

  const csv = readFileSync(inputPath, 'utf-8');
  const result = Papa.parse(csv, { header: true, dynamicTyping: true, skipEmptyLines: true });
  const columns = result.meta.fields || [];
  const missingFields = (config.fields || []).filter(field => !columns.includes(field));
  const status = missingFields.length ? 'schema_warning' : 'ok';

  writeFileSync(outputPath, JSON.stringify(result.data, null, 2));
  const bytes = readFileSync(outputPath).byteLength;
  catalog.datasets.push({
    ...config,
    status,
    rows: result.data.length,
    columns,
    missingFields,
    bytes,
  });
  console.log(`✅ ${input} → ${output} (${result.data.length} rows)`);

  if (config.required && missingFields.length) {
    requiredIssues.push(`${config.id}: missing fields ${missingFields.join(', ')}`);
  }
}

writeFileSync(join(OUTPUT_DIR, 'catalog.json'), JSON.stringify(catalog, null, 2));
console.log(`✅ data_catalog.json → catalog.json (${catalog.datasets.length} datasets)`);

if (requiredIssues.length) {
  throw new Error(`Required data contract issues:\n- ${requiredIssues.join('\n- ')}`);
}

console.log('\nData loading complete!');
