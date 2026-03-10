export interface CsvRow {
  [key: string]: string;
}

export interface ParsedCsv {
  headers: string[];
  rows: CsvRow[];
}

export function parseCsv(text: string): ParsedCsv {
  // Detect separator (;  ,  \t)
  const firstLine = text.split("\n")[0];
  const sep = firstLine.includes(";") ? ";" : firstLine.includes("\t") ? "\t" : ",";

  const lines = text.trim().split("\n").filter(Boolean);
  if (lines.length < 2) return { headers: [], rows: [] };

  const headers = parseLine(lines[0], sep);
  const rows = lines.slice(1).map((line) => {
    const values = parseLine(line, sep);
    const row: CsvRow = {};
    headers.forEach((h, i) => {
      row[h] = (values[i] ?? "").trim();
    });
    return row;
  });

  return { headers, rows };
}

function parseLine(line: string, sep: string): string[] {
  const result: string[] = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const ch = line[i];
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (ch === sep && !inQuotes) {
      result.push(current.trim());
      current = "";
    } else {
      current += ch;
    }
  }
  result.push(current.trim());
  return result;
}

/** Parse a date string in common French bank formats */
export function parseDate(value: string): string | null {
  // DD/MM/YYYY or DD-MM-YYYY
  const dmy = value.match(/^(\d{2})[/\-.](\d{2})[/\-.](\d{4})$/);
  if (dmy) return `${dmy[3]}-${dmy[2]}-${dmy[1]}`;
  // YYYY-MM-DD
  const iso = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (iso) return value;
  return null;
}

/** Parse amount: handles French format (1 234,56) and standard (1234.56) */
export function parseAmount(value: string): number | null {
  let cleaned = value.replace(/\s/g, "").replace(/€/g, "").trim();
  // French decimal comma
  if (cleaned.includes(",") && !cleaned.includes(".")) {
    cleaned = cleaned.replace(",", ".");
  } else if (cleaned.includes(",") && cleaned.includes(".")) {
    // 1.234,56 → 1234.56
    cleaned = cleaned.replace(/\./g, "").replace(",", ".");
  }
  const n = parseFloat(cleaned);
  return isNaN(n) ? null : n;
}

/** Bank presets for column mapping */
export interface BankPreset {
  name: string;
  dateColumn: string;
  labelColumn: string;
  amountColumn: string;
  debitColumn?: string;
  creditColumn?: string;
}

export const BANK_PRESETS: BankPreset[] = [
  { name: "Générique (Date, Libellé, Montant)", dateColumn: "Date", labelColumn: "Libellé", amountColumn: "Montant" },
  { name: "Crédit Agricole", dateColumn: "Date", labelColumn: "Libellé", amountColumn: "Montant", debitColumn: "Débit", creditColumn: "Crédit" },
  { name: "Boursorama", dateColumn: "dateOp", labelColumn: "label", amountColumn: "amount" },
  { name: "BNP Paribas", dateColumn: "Date", labelColumn: "Objet", amountColumn: "Montant" },
];
