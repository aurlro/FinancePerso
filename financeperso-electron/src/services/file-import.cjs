const fs = require('node:fs');
const path = require('node:path');
const { parse } = require('csv-parse/sync');

class FileImportService {
  constructor(dbService) {
    this.dbService = dbService;
  }

  async importCSV(filePath, options = {}) {
    try {
      // Lire le fichier
      const content = fs.readFileSync(filePath, options.encoding || 'utf-8');
      
      // Parser le CSV
      const records = parse(content, {
        columns: true,
        skip_empty_lines: true,
        delimiter: options.delimiter || ';',
        trim: true,
      });

      if (records.length === 0) {
        return {
          success: false,
          error: 'Fichier CSV vide',
          total: 0,
          imported: 0,
          errors: 0,
          fileName: path.basename(filePath),
        };
      }

      // Détection automatique des colonnes
      const mappings = options.mappings || this.detectMappings(records[0]);
      
      // Transformer et valider
      const transactions = [];
      const errors = [];
      
      for (let i = 0; i < records.length; i++) {
        try {
          const tx = this.transformRecord(records[i], mappings, i);
          if (tx) transactions.push(tx);
        } catch (error) {
          errors.push({ row: i + 1, error: error.message });
        }
      }

      // Insérer dans la base
      const imported = await this.insertTransactions(transactions);

      return {
        success: true,
        total: records.length,
        imported: imported.length,
        errors: errors.length,
        fileName: path.basename(filePath),
        errorDetails: errors.slice(0, 5), // Limiter à 5 erreurs
      };
    } catch (error) {
      console.error('[Import] Error:', error);
      return {
        success: false,
        error: error.message,
        total: 0,
        imported: 0,
        errors: 0,
        fileName: path.basename(filePath),
      };
    }
  }

  detectMappings(firstRow) {
    const columns = Object.keys(firstRow);
    const lowerColumns = columns.map(c => c.toLowerCase());
    
    // Détection des colonnes par patterns
    const findColumn = (patterns) => {
      for (let i = 0; i < lowerColumns.length; i++) {
        const col = lowerColumns[i];
        for (const pattern of patterns) {
          if (col.includes(pattern.toLowerCase())) {
            return columns[i];
          }
        }
      }
      return columns[0]; // Fallback
    };

    return {
      date: findColumn(['date', 'jour', 'date operation', 'date opération', 'valeur']),
      description: findColumn(['libelle', 'label', 'description', 'libellé', 'motif', 'transaction']),
      amount: findColumn(['montant', 'amount', 'credit', 'debit', 'crédit', 'débit', 'euros']),
      category: findColumn(['categorie', 'category', 'catégorie', 'type']) || null,
    };
  }

  transformRecord(record, mappings, index) {
    try {
      const rawAmount = record[mappings.amount];
      const amount = this.parseAmount(rawAmount);
      
      if (isNaN(amount)) {
        throw new Error(`Montant invalide: ${rawAmount}`);
      }

      const parsedDate = this.parseDate(record[mappings.date]);
      if (!parsedDate) {
        throw new Error(`Date invalide: ${record[mappings.date]}`);
      }

      return {
        date: parsedDate,
        description: record[mappings.description]?.trim() || 'Sans libellé',
        amount: Math.abs(amount),
        type: amount >= 0 ? 'income' : 'expense',
        category: mappings.category ? record[mappings.category]?.trim() : null,
      };
    } catch (error) {
      console.warn(`[Import] Erreur ligne ${index + 1}:`, error.message);
      throw error;
    }
  }

  parseAmount(value) {
    if (!value) return 0;
    
    // Nettoyer le format: "1 234,56" → "1234.56"
    const cleaned = value.toString()
      .replace(/\s/g, '')        // Espaces
      .replace(/\u00a0/g, '')    // Espaces insécables
      .replace(',', '.');         // Virgule française
    
    return parseFloat(cleaned) || 0;
  }

  parseDate(value) {
    if (!value) return new Date().toISOString().split('T')[0];
    
    const str = value.toString().trim();
    
    // Formats supportés
    const formats = [
      // DD/MM/YYYY
      { regex: /^(\d{1,2})\/(\d{1,2})\/(\d{4})$/, fn: (m) => `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}` },
      // DD-MM-YYYY
      { regex: /^(\d{1,2})-(\d{1,2})-(\d{4})$/, fn: (m) => `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}` },
      // YYYY-MM-DD
      { regex: /^(\d{4})-(\d{1,2})-(\d{1,2})$/, fn: (m) => `${m[1]}-${m[2].padStart(2, '0')}-${m[3].padStart(2, '0')}` },
      // DD.MM.YYYY
      { regex: /^(\d{1,2})\.(\d{1,2})\.(\d{4})$/, fn: (m) => `${m[3]}-${m[2].padStart(2, '0')}-${m[1].padStart(2, '0')}` },
    ];

    for (const format of formats) {
      const match = str.match(format.regex);
      if (match) {
        const result = format.fn(match);
        // Vérifier que la date est valide
        const date = new Date(result);
        if (!isNaN(date.getTime())) {
          return result;
        }
      }
    }

    // Fallback: essayer Date.parse
    const parsed = new Date(str);
    if (!isNaN(parsed.getTime())) {
      return parsed.toISOString().split('T')[0];
    }

    return null;
  }

  async insertTransactions(transactions) {
    const inserted = [];
    
    for (const tx of transactions) {
      try {
        // Vérifier doublon (même date, description, montant)
        const existing = await new Promise((resolve, reject) => {
          this.dbService.db.get(
            'SELECT id FROM transactions WHERE date = ? AND description = ? AND amount = ?',
            [tx.date, tx.description, tx.amount],
            (err, row) => {
              if (err) reject(err);
              else resolve(row);
            }
          );
        });

        if (existing) {
          continue; // Doublon, ignorer
        }

        // Insérer
        const result = await new Promise((resolve, reject) => {
          this.dbService.db.run(
            'INSERT INTO transactions (date, description, amount, type, category) VALUES (?, ?, ?, ?, ?)',
            [tx.date, tx.description, tx.amount, tx.type, tx.category || 'Non catégorisé'],
            function(err) {
              if (err) reject(err);
              else resolve({ id: this.lastID });
            }
          );
        });

        inserted.push({ ...tx, id: result.id });
      } catch (error) {
        console.warn('[Import] Erreur insertion:', error.message);
      }
    }
    
    return inserted;
  }
}

module.exports = { FileImportService };
