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

console.log(`Project root: ${PROJECT_ROOT}`);
console.log(`Processed dir: ${PROCESSED_DIR}`);
console.log(`Output dir: ${OUTPUT_DIR}`);

const tables = [
  { input: 'population_annual.csv', output: 'population_annual.json' },
  { input: 'population_age_gender.csv', output: 'population_age_gender.json' },
  { input: 'population_village_monthly.csv', output: 'population_village_monthly.json' },
  { input: 'budget_revenue_by_source.csv', output: 'budget_revenue_by_source.json' },
  { input: 'budget_expenditure_by_function.csv', output: 'budget_expenditure_by_function.json' },
  { input: 'budget_expenditure_by_agency.csv', output: 'budget_expenditure_by_agency.json' },
  { input: 'fund_operating.csv', output: 'fund_operating.json' },
  { input: 'fund_business.csv', output: 'fund_business.json' },
  { input: 'fund_affairs.csv', output: 'fund_affairs.json' },
  { input: 'county_population_comparison.csv', output: 'county_population_comparison.json' },
  { input: 'budget_by_policy_domain.csv', output: 'budget_by_policy_domain.json' },
  { input: 'budget_expenditure_classified.csv', output: 'budget_expenditure_classified.json' },
  { input: 'budget_agency_classified.csv', output: 'budget_agency_classified.json' },
  { input: 'budget_agency_by_domain.csv', output: 'budget_agency_by_domain.json' },
  { input: 'cw_happy_city_rankings.csv', output: 'cw_happy_city_rankings.json' },
  { input: 'cw_happy_city_dimensions.csv', output: 'cw_happy_city_dimensions.json' },
  { input: 'gvm_mayor_satisfaction.csv', output: 'gvm_mayor_satisfaction.json' },
];

mkdirSync(OUTPUT_DIR, { recursive: true });

for (const { input, output } of tables) {
  const inputPath = join(PROCESSED_DIR, input);
  const outputPath = join(OUTPUT_DIR, output);

  if (!existsSync(inputPath)) {
    console.warn(`⚠  Not found: ${inputPath}`);
    writeFileSync(outputPath, JSON.stringify([]));
    continue;
  }

  const csv = readFileSync(inputPath, 'utf-8');
  const result = Papa.parse(csv, { header: true, dynamicTyping: true, skipEmptyLines: true });
  writeFileSync(outputPath, JSON.stringify(result.data, null, 2));
  console.log(`✅ ${input} → ${output} (${result.data.length} rows)`);
}

console.log('\nData loading complete!');
