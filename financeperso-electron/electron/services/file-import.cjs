/**
 * File Import Service
 * Gestion des imports CSV et exports PDF/Excel
 */

const fs = require('node:fs');
const path = require('node:path');
const { parse } = require('csv-parse/sync');

class FileImportService {
  constructor(dbService) {
    this.dbService = dbService;
  }

  async importCSV(filePath, options = {}) {
    try {
      console.log('[Import] Starting import of:', filePath);
      
      // Lire le fichier
      const content = fs.readFileSync(filePath, 'utf-8');
      
      // Détecter l'encodage si nécessaire
      const encoding = options.encoding || this.detectEncoding(content);
      
      // Parser le CSV
      const delimiter = options.delimiter || this.detectDelimiter(content);
      
      const records = parse(content, {
        columns: true,
        skip_empty_lines: true,
        delimiter: delimiter,
        trim: true,
      });

      if (records.length === 0) {
        return { success: false, error: 'Fichier vide ou invalide' };
      }

      // Mapping des colonnes
      const mappings = options.mappings || this.detectMappings(records[0]);
      
      console.log('[Import] Detected mappings:', mappings);
      
      // Transformer et valider
      const transactions = [];
      const errors = [];
      
      for (let i = 0; i < records.length; i++) {
        try {
          const tx = this.transformRecord(records[i], mappings, i + 1);
          if (tx) transactions.push(tx);
        } catch (error) {
          errors.push({ row: i + 1, error: error.message });
        }
      }

      // Insérer dans la base
      const imported = [];
      const duplicates = [];
      
      for (const tx of transactions) {
        try {
          // Vérifier les doublons (même date, libellé, montant)
          const existing = this.dbService.query(
            `SELECT id FROM transactions 
             WHERE date = ? AND label = ? AND ABS(amount - ?) < 0.01`,
            [tx.date, tx.label, tx.amount]
          );
          
          if (existing.length > 0) {
            duplicates.push(tx);
            continue;
          }
          
          const result = this.dbService.insertTransaction(tx);
          imported.push(result);
        } catch (error) {
          errors.push({ row: 'insert', error: error.message, data: tx });
        }
      }

      console.log(`[Import] Completed: ${imported.length} imported, ${duplicates.length} duplicates, ${errors.length} errors`);

      return {
        success: true,
        total: records.length,
        imported: imported.length,
        duplicates: duplicates.length,
        errors: errors.length,
        errorDetails: errors.slice(0, 10), // Limiter les détails
        fileName: path.basename(filePath),
        mappings,
      };
    } catch (error) {
      console.error('[Import] Error:', error);
      return {
        success: false,
        error: error.message,
      };
    }
  }

  detectEncoding(content) {
    // Détection simple basée sur BOM
    if (content.charCodeAt(0) === 0xFEFF) return 'utf-8-bom';
    return 'utf-8';
  }

  detectDelimiter(content) {
    const firstLine = content.split('\n')[0];
    const semicolons = (firstLine.match(/;/g) || []).length;
    const commas = (firstLine.match(/,/g) || []).length;
    const tabs = (firstLine.match(/\t/g) || []).length;
    
    if (semicolons > commas && semicolons > tabs) return ';';
    if (tabs > semicolons && tabs > commas) return '\t';
    return ',';
  }

  detectMappings(firstRow) {
    const columns = Object.keys(firstRow);
    const normalizedColumns = columns.map(c => ({
      original: c,
      lower: c.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    }));
    
    const findColumn = (patterns) => {
      for (const pattern of patterns) {
        const found = normalizedColumns.find(c => 
          c.lower.includes(pattern) || 
          pattern.includes(c.lower)
        );
        if (found) return found.original;
      }
      return null;
    };
    
    return {
      date: findColumn(['date', 'jour', 'operation', 'date operation']) || columns[0],
      label: findColumn(['libelle', 'label', 'description', 'motif', 'transaction']) || columns[1],
      amount: findColumn(['montant', 'amount', 'credit', 'debit', 'solde']) || columns[2],
      category: findColumn(['categorie', 'category', 'type', 'nature']) || null,
      account: findColumn(['compte', 'account', 'numero', 'rib']) || null,
    };
  }

  transformRecord(record, mappings, rowNum) {
    const rawAmount = record[mappings.amount];
    if (!rawAmount) {
      throw new Error(`Montant manquant à la ligne ${rowNum}`);
    }
    
    const amount = this.parseAmount(rawAmount);
    
    return {
      date: this.parseDate(record[mappings.date]),
      label: this.cleanLabel(record[mappings.label] || 'Sans libellé'),
      amount: Math.abs(amount),
      type: amount >= 0 ? 'credit' : 'debit',
      category: mappings.category ? this.cleanCategory(record[mappings.category]) : 'Inconnu',
      account: mappings.account ? record[mappings.account] : null,
    };
  }

  parseAmount(value) {
    if (!value) return 0;
    
    // Gérer les formats européens: "1 234,56" ou "1.234,56"
    const cleaned = value.toString()
      .replace(/\s/g, '')           // Enlever espaces
      .replace(/\./g, '')           // Enlever points (séparateurs milliers)
      .replace(',', '.');           // Virgule -> point décimal
    
    const parsed = parseFloat(cleaned);
    return isNaN(parsed) ? 0 : parsed;
  }

  parseDate(value) {
    if (!value) return new Date().toISOString().split('T')[0];
    
    // Essayer différents formats
    const formats = [
      // DD/MM/YYYY
      { regex: /(\d{1,2})\/(\d{1,2})\/(\d{4})/, fn: (m) => `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}` },
      // DD-MM-YYYY
      { regex: /(\d{1,2})-(\d{1,2})-(\d{4})/, fn: (m) => `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}` },
      // YYYY-MM-DD
      { regex: /(\d{4})-(\d{1,2})-(\d{1,2})/, fn: (m) => `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}` },
      // DD.MM.YYYY
      { regex: /(\d{1,2})\.(\d{1,2})\.(\d{4})/, fn: (m) => `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}` },
    ];

    for (const format of formats) {
      const match = value.toString().match(format.regex);
      if (match) return format.fn(match);
    }

    // Fallback: parser JavaScript
    const date = new Date(value);
    if (!isNaN(date.getTime())) {
      return date.toISOString().split('T')[0];
    }

    return new Date().toISOString().split('T')[0];
  }

  cleanLabel(label) {
    return label
      .toString()
      .trim()
      .replace(/\s+/g, ' ')        // Espaces multiples -> simple
      .replace(/\b(CB|VIREMENT|PRELEVEMENT|PRLV)\b/gi, '')  // Retirer préfixes bancaires
      .trim();
  }

  cleanCategory(category) {
    if (!category) return 'Inconnu';
    
    const mapping = {
      'alimentation': 'Alimentation',
      'restaurant': 'Alimentation',
      'courses': 'Alimentation',
      'transport': 'Transport',
      'essence': 'Transport',
      'carburant': 'Transport',
      'loyer': 'Logement',
      'charges': 'Logement',
      'santé': 'Santé',
      'pharmacie': 'Santé',
      'loisirs': 'Loisirs',
      'divertissement': 'Loisirs',
      'salaire': 'Revenus',
      'revenu': 'Revenus',
      'epargne': 'Épargne',
    };
    
    const normalized = category.toString().toLowerCase().trim();
    return mapping[normalized] || category.toString().trim();
  }

  async exportToPDF(data, outputPath) {
    // TODO: Implémenter export PDF avec puppeteer ou pdfkit
    console.log('[Export] PDF export requested:', outputPath);
    return { success: true, path: outputPath };
  }

  async exportToExcel(data, outputPath) {
    // TODO: Implémenter export Excel avec xlsx
    console.log('[Export] Excel export requested:', outputPath);
    return { success: true, path: outputPath };
  }
}

module.exports = { FileImportService };
