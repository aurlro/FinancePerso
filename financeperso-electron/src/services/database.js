const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

class DatabaseService {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
  }

  initialize() {
    return new Promise((resolve, reject) => {
      try {
        // Crée le dossier si nécessaire
        const dir = path.dirname(this.dbPath);
        if (!fs.existsSync(dir)) {
          fs.mkdirSync(dir, { recursive: true });
        }

        // Ouvre la base de données
        this.db = new sqlite3.Database(this.dbPath, (err) => {
          if (err) {
            console.error('[DB] Failed to open database:', err);
            reject(err);
            return;
          }
          
          console.log('[DB] Database opened at:', this.dbPath);
          
          // Crée les tables
          this.createTables().then(() => {
            resolve(true);
          }).catch(reject);
        });
      } catch (error) {
        console.error('[DB] Failed to initialize database:', error);
        reject(error);
      }
    });
  }

  async createTables() {
    return new Promise((resolve, reject) => {
      // Table des transactions
      this.db.run(`
        CREATE TABLE IF NOT EXISTS transactions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          date TEXT NOT NULL,
          description TEXT NOT NULL,
          amount REAL NOT NULL,
          category TEXT DEFAULT 'Non catégorisé',
          type TEXT CHECK(type IN ('income', 'expense')) NOT NULL,
          account TEXT DEFAULT 'Compte principal',
          notes TEXT,
          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
          updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
      `, (err) => {
        if (err) {
          reject(err);
          return;
        }

        // Table des catégories
        this.db.run(`
          CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            emoji TEXT DEFAULT '📁',
            color TEXT DEFAULT '#10b981',
            is_fixed INTEGER DEFAULT 0,
            budget_limit REAL
          )
        `, (err) => {
          if (err) {
            reject(err);
            return;
          }

          // Table des comptes
          this.db.run(`
            CREATE TABLE IF NOT EXISTS accounts (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT UNIQUE NOT NULL,
              type TEXT DEFAULT 'checking',
              balance REAL DEFAULT 0,
              currency TEXT DEFAULT 'EUR'
            )
          `, (err) => {
            if (err) {
              reject(err);
              return;
            }

            // Table des budgets
            this.db.run(`
              CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                period TEXT DEFAULT 'monthly',
                year INTEGER,
                month INTEGER,
                UNIQUE(category, year, month)
              )
            `, async (err) => {
              if (err) {
                reject(err);
                return;
              }

              // Table des règles d'apprentissage (pour l'IA)
              this.db.run(`
                CREATE TABLE IF NOT EXISTS learning_rules (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  pattern TEXT UNIQUE NOT NULL,
                  category TEXT NOT NULL,
                  confidence REAL DEFAULT 1.0,
                  usage_count INTEGER DEFAULT 0,
                  source TEXT DEFAULT 'manual',
                  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
              `, (err) => {
                if (err) {
                  reject(err);
                  return;
                }

                // Table des paramètres IA
                this.db.run(`
                  CREATE TABLE IF NOT EXISTS ai_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider TEXT DEFAULT 'local',
                    api_key TEXT,
                    auto_categorize INTEGER DEFAULT 0,
                    min_confidence REAL DEFAULT 0.7,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                  )
                `, async (err) => {
                  if (err) {
                    reject(err);
                    return;
                  }

                  // Table des membres (couples/familles)
                  this.db.run(`
                    CREATE TABLE IF NOT EXISTS members (
                      id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT NOT NULL,
                      type TEXT CHECK(type IN ('primary', 'secondary')) DEFAULT 'secondary',
                      color TEXT DEFAULT '#10b981',
                      emoji TEXT DEFAULT '👤',
                      email TEXT,
                      is_active INTEGER DEFAULT 1,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                  `, (err) => {
                    if (err) {
                      reject(err);
                      return;
                    }

                    // Table de liaison transactions-membres (pour répartition)
                    this.db.run(`
                      CREATE TABLE IF NOT EXISTS transaction_members (
                        transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
                        member_id INTEGER REFERENCES members(id) ON DELETE CASCADE,
                        split_amount REAL,
                        PRIMARY KEY (transaction_id, member_id)
                      )
                    `, async (err) => {
                      if (err) {
                        reject(err);
                        return;
                      }

                      // Insère les catégories par défaut
                      await this.insertDefaultCategories();
                      // Insère le membre principal par défaut
                      await this.insertDefaultMember();
                      console.log('[DB] Tables created successfully');
                      resolve();
                    });
                  });
                });
              });
            });
          });
        });
      });
    });
  }

  async insertDefaultCategories() {
    const defaultCategories = [
      { name: 'Alimentation', emoji: '🍽️', color: '#ef4444' },
      { name: 'Transport', emoji: '🚗', color: '#f97316' },
      { name: 'Logement', emoji: '🏠', color: '#8b5cf6' },
      { name: 'Santé', emoji: '⚕️', color: '#ec4899' },
      { name: 'Loisirs', emoji: '🎮', color: '#14b8a6' },
      { name: 'Shopping', emoji: '🛍️', color: '#f59e0b' },
      { name: 'Revenus', emoji: '💰', color: '#10b981' },
      { name: 'Autre', emoji: '📦', color: '#6b7280' },
    ];

    for (const cat of defaultCategories) {
      await new Promise((resolve, reject) => {
        this.db.run(
          'INSERT OR IGNORE INTO categories (name, emoji, color) VALUES (?, ?, ?)',
          [cat.name, cat.emoji, cat.color],
          (err) => {
            if (err) reject(err);
            else resolve();
          }
        );
      });
    }
  }

  async insertDefaultMember() {
    // Crée un membre principal par défaut s'il n'existe pas encore
    await new Promise((resolve, reject) => {
      this.db.run(
        `INSERT OR IGNORE INTO members (id, name, type, color, emoji, is_active) 
         VALUES (1, 'Moi', 'primary', '#8b5cf6', '👤', 1)`,
        (err) => {
          if (err) reject(err);
          else resolve();
        }
      );
    });
  }

  // Méthodes CRUD pour les transactions
  getAllTransactions(limit = 100, offset = 0) {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT * FROM transactions ORDER BY date DESC LIMIT ? OFFSET ?',
        [limit, offset],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  getTransactionById(id) {
    return new Promise((resolve, reject) => {
      this.db.get(
        'SELECT * FROM transactions WHERE id = ?',
        [id],
        (err, row) => {
          if (err) reject(err);
          else resolve(row);
        }
      );
    });
  }

  createTransaction(data) {
    return new Promise((resolve, reject) => {
      const { date, description, amount, category, type, account, notes } = data;
      this.db.run(
        'INSERT INTO transactions (date, description, amount, category, type, account, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
        [date, description, amount, category, type, account, notes],
        function(err) {
          if (err) reject(err);
          else resolve({ id: this.lastID, ...data });
        }
      );
    });
  }

  updateTransaction(id, data) {
    return new Promise((resolve, reject) => {
      const { date, description, amount, category, type, account, notes } = data;
      this.db.run(
        'UPDATE transactions SET date = ?, description = ?, amount = ?, category = ?, type = ?, account = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
        [date, description, amount, category, type, account, notes, id],
        (err) => {
          if (err) reject(err);
          else resolve({ id, ...data });
        }
      );
    });
  }

  deleteTransaction(id) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'DELETE FROM transactions WHERE id = ?',
        [id],
        (err) => {
          if (err) reject(err);
          else resolve({ success: true });
        }
      );
    });
  }

  // Statistiques
  getStatsByMonth(year, month) {
    return new Promise((resolve, reject) => {
      const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
      const endDate = `${year}-${String(month + 1).padStart(2, '0')}-01`;
      
      this.db.all(
        `SELECT 
          type,
          SUM(amount) as total,
          COUNT(*) as count
        FROM transactions 
        WHERE date >= ? AND date < ?
        GROUP BY type`,
        [startDate, endDate],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  getCategoriesStats(year, month) {
    return new Promise((resolve, reject) => {
      const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
      const endDate = `${year}-${String(month + 1).padStart(2, '0')}-01`;
      
      this.db.all(
        `SELECT 
          category,
          SUM(amount) as total,
          COUNT(*) as count
        FROM transactions 
        WHERE date >= ? AND date < ? AND type = 'expense'
        GROUP BY category
        ORDER BY total DESC`,
        [startDate, endDate],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  // Catégories
  getAllCategories() {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT * FROM categories ORDER BY name',
        [],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  // Méthodes CRUD pour les budgets
  getAllBudgets() {
    return new Promise((resolve, reject) => {
      this.db.all(
        'SELECT * FROM budgets ORDER BY category',
        [],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  createBudget(data) {
    return new Promise((resolve, reject) => {
      const { category, amount, period, year, month } = data;
      this.db.run(
        'INSERT INTO budgets (category, amount, period, year, month) VALUES (?, ?, ?, ?, ?)',
        [category, amount, period || 'monthly', year || null, month || null],
        function(err) {
          if (err) reject(err);
          else resolve({ id: this.lastID, ...data });
        }
      );
    });
  }

  updateBudget(id, data) {
    return new Promise((resolve, reject) => {
      const { category, amount, period, year, month } = data;
      this.db.run(
        'UPDATE budgets SET category = ?, amount = ?, period = ?, year = ?, month = ? WHERE id = ?',
        [category, amount, period || 'monthly', year || null, month || null, id],
        (err) => {
          if (err) reject(err);
          else resolve({ id, ...data });
        }
      );
    });
  }

  deleteBudget(id) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'DELETE FROM budgets WHERE id = ?',
        [id],
        (err) => {
          if (err) reject(err);
          else resolve({ success: true });
        }
      );
    });
  }

  getBudgetStatus(year, month) {
    return new Promise((resolve, reject) => {
      const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
      const endDate = `${year}-${String(month + 1).padStart(2, '0')}-01`;
      
      this.db.all(
        `SELECT 
          b.id,
          b.category,
          b.amount as budget_amount,
          b.period,
          b.year,
          b.month,
          COALESCE(SUM(t.amount), 0) as spent_amount,
          COUNT(t.id) as transaction_count
        FROM budgets b
        LEFT JOIN transactions t ON b.category = t.category 
          AND t.type = 'expense'
          AND t.date >= ? AND t.date < ?
        GROUP BY b.id, b.category, b.amount, b.period, b.year, b.month
        ORDER BY b.category`,
        [startDate, endDate],
        (err, rows) => {
          if (err) reject(err);
          else {
            // Calculer les pourcentages et statuts
            const result = rows.map(row => {
              const budgetAmount = row.budget_amount || 0;
              const spentAmount = row.spent_amount || 0;
              const remaining = budgetAmount - spentAmount;
              const percentage = budgetAmount > 0 ? (spentAmount / budgetAmount) * 100 : 0;
              
              return {
                ...row,
                spent_amount: spentAmount,
                remaining: remaining,
                percentage: Math.round(percentage * 100) / 100,
                status: percentage >= 100 ? 'exceeded' : percentage >= 80 ? 'warning' : 'ok'
              };
            });
            resolve(result);
          }
        }
      );
    });
  }

  // Récupère les transactions non catégorisées ou "Non catégorisé"
  getPendingTransactions() {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT * FROM transactions 
         WHERE category IS NULL 
         OR category = 'Non catégorisé' 
         OR category = ''
         ORDER BY date DESC`,
        [],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  // Met à jour plusieurs transactions avec la même catégorie
  updateMultipleTransactions(ids, category) {
    return new Promise((resolve, reject) => {
      if (!ids || ids.length === 0) {
        resolve({ success: true, updated: 0 });
        return;
      }

      const placeholders = ids.map(() => '?').join(',');
      this.db.run(
        `UPDATE transactions 
         SET category = ?, updated_at = CURRENT_TIMESTAMP 
         WHERE id IN (${placeholders})`,
        [category, ...ids],
        function(err) {
          if (err) reject(err);
          else resolve({ success: true, updated: this.changes });
        }
      );
    });
  }

  // Ignore des transactions (les marque comme "Ignoré")
  ignoreTransactions(ids) {
    return new Promise((resolve, reject) => {
      if (!ids || ids.length === 0) {
        resolve({ success: true, ignored: 0 });
        return;
      }

      const placeholders = ids.map(() => '?').join(',');
      this.db.run(
        `UPDATE transactions 
         SET category = 'Ignoré', updated_at = CURRENT_TIMESTAMP 
         WHERE id IN (${placeholders})`,
        ids,
        function(err) {
          if (err) reject(err);
          else resolve({ success: true, ignored: this.changes });
        }
      );
    });
  }

  // ========== LEARNING RULES METHODS ==========

  /**
   * Recherche une règle exacte par pattern
   */
  findRuleByPattern(pattern) {
    return new Promise((resolve, reject) => {
      this.db.get(
        'SELECT * FROM learning_rules WHERE pattern = ? COLLATE NOCASE',
        [pattern],
        (err, row) => {
          if (err) reject(err);
          else resolve(row || null);
        }
      );
    });
  }

  /**
   * Recherche des règles par correspondance partielle (LIKE)
   */
  findPartialRule(pattern, limit = 5) {
    return new Promise((resolve, reject) => {
      const searchPattern = `%${pattern}%`;
      this.db.all(
        `SELECT * FROM learning_rules 
         WHERE pattern LIKE ? COLLATE NOCASE 
         ORDER BY usage_count DESC, confidence DESC 
         LIMIT ?`,
        [searchPattern, limit],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  /**
   * Crée ou met à jour une règle d'apprentissage
   */
  createRule(pattern, category, confidence = 1.0, source = 'manual') {
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO learning_rules (pattern, category, confidence, source, usage_count) 
         VALUES (?, ?, ?, ?, 1)
         ON CONFLICT(pattern) DO UPDATE SET
           category = excluded.category,
           confidence = excluded.confidence,
           usage_count = usage_count + 1,
           updated_at = CURRENT_TIMESTAMP`,
        [pattern.toUpperCase().trim(), category, confidence, source],
        function(err) {
          if (err) reject(err);
          else resolve({ 
            id: this.lastID,
            pattern: pattern.toUpperCase().trim(),
            category,
            confidence,
            source
          });
        }
      );
    });
  }

  /**
   * Incrémente le compteur d'utilisation d'une règle
   */
  incrementRuleUsage(pattern) {
    return new Promise((resolve, reject) => {
      this.db.run(
        `UPDATE learning_rules 
         SET usage_count = usage_count + 1, updated_at = CURRENT_TIMESTAMP 
         WHERE pattern = ? COLLATE NOCASE`,
        [pattern],
        (err) => {
          if (err) reject(err);
          else resolve(true);
        }
      );
    });
  }

  /**
   * Récupère toutes les règles d'apprentissage
   */
  getAllRules(limit = 100, offset = 0) {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT * FROM learning_rules 
         ORDER BY usage_count DESC, updated_at DESC 
         LIMIT ? OFFSET ?`,
        [limit, offset],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  /**
   * Récupère les règles par catégorie
   */
  getRulesByCategory(category) {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT * FROM learning_rules 
         WHERE category = ? COLLATE NOCASE
         ORDER BY usage_count DESC`,
        [category],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  // ========== AI SETTINGS METHODS ==========

  /**
   * Récupère les paramètres IA
   */
  getAISettings() {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT * FROM ai_settings', [], (err, rows) => {
        if (err) {
          reject(err);
          return;
        }
        
        // Convertir en objet
        const settings = {
          provider: 'gemini',
          apiKey: '',
          model: 'gemini-2.0-flash',
          enabled: false,
          autoCategorize: false,
        };
        
        for (const row of rows) {
          try {
            settings[row.key] = JSON.parse(row.value);
          } catch {
            settings[row.key] = row.value;
          }
        }
        
        resolve(settings);
      });
    });
  }

  /**
   * Sauvegarde les paramètres IA
   */
  saveAISettings(settings) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare(
        `INSERT INTO ai_settings (key, value) VALUES (?, ?)
         ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = CURRENT_TIMESTAMP`
      );
      
      const keys = ['provider', 'apiKey', 'model', 'enabled', 'autoCategorize'];
      
      for (const key of keys) {
        if (settings[key] !== undefined) {
          const value = typeof settings[key] === 'boolean' || typeof settings[key] === 'object' 
            ? JSON.stringify(settings[key]) 
            : settings[key];
          stmt.run(key, value);
        }
      }
      
      stmt.finalize((err) => {
        if (err) reject(err);
        else resolve(true);
      });
    });
  }

  // ========== MEMBERS METHODS ==========

  /**
   * Récupère tous les membres actifs
   */
  getAllMembers() {
    return new Promise((resolve, reject) => {
      this.db.all(
        `SELECT * FROM members 
         WHERE is_active = 1 
         ORDER BY CASE type WHEN 'primary' THEN 0 ELSE 1 END, name`,
        [],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  /**
   * Récupère un membre par son ID
   */
  getMemberById(id) {
    return new Promise((resolve, reject) => {
      this.db.get(
        'SELECT * FROM members WHERE id = ? AND is_active = 1',
        [id],
        (err, row) => {
          if (err) reject(err);
          else resolve(row);
        }
      );
    });
  }

  /**
   * Crée un nouveau membre
   */
  createMember(data) {
    return new Promise((resolve, reject) => {
      const { name, type = 'secondary', color = '#10b981', emoji = '👤', email } = data;
      this.db.run(
        `INSERT INTO members (name, type, color, emoji, email) 
         VALUES (?, ?, ?, ?, ?)`,
        [name, type, color, emoji, email],
        function(err) {
          if (err) reject(err);
          else resolve({ id: this.lastID, name, type, color, emoji, email });
        }
      );
    });
  }

  /**
   * Met à jour un membre
   */
  updateMember(id, data) {
    return new Promise((resolve, reject) => {
      const { name, type, color, emoji, email, is_active } = data;
      this.db.run(
        `UPDATE members 
         SET name = COALESCE(?, name), 
             type = COALESCE(?, type), 
             color = COALESCE(?, color), 
             emoji = COALESCE(?, emoji), 
             email = COALESCE(?, email),
             is_active = COALESCE(?, is_active)
         WHERE id = ?`,
        [name, type, color, emoji, email, is_active, id],
        (err) => {
          if (err) reject(err);
          else resolve({ id, ...data });
        }
      );
    });
  }

  /**
   * Supprime (désactive) un membre
   */
  deleteMember(id) {
    return new Promise((resolve, reject) => {
      // Vérifier que ce n'est pas le membre principal
      this.db.get(
        'SELECT type FROM members WHERE id = ?',
        [id],
        (err, row) => {
          if (err) {
            reject(err);
            return;
          }
          if (row && row.type === 'primary') {
            reject(new Error('Cannot delete primary member'));
            return;
          }

          // Soft delete - marquer comme inactif
          this.db.run(
            'UPDATE members SET is_active = 0 WHERE id = ?',
            [id],
            (err) => {
              if (err) reject(err);
              else resolve({ success: true });
            }
          );
        }
      );
    });
  }

  /**
   * Récupère les transactions d'un membre avec le montant réparti
   */
  getTransactionsByMember(memberId, year, month) {
    return new Promise((resolve, reject) => {
      let sql = `
        SELECT 
          t.*,
          tm.split_amount,
          m.name as member_name,
          m.color as member_color,
          m.emoji as member_emoji
        FROM transactions t
        JOIN transaction_members tm ON t.id = tm.transaction_id
        JOIN members m ON tm.member_id = m.id
        WHERE tm.member_id = ? AND t.type = 'expense'
      `;
      const params = [memberId];

      if (year && month) {
        const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
        const endDate = `${year}-${String(month + 1).padStart(2, '0')}-01`;
        sql += ` AND t.date >= ? AND t.date < ?`;
        params.push(startDate, endDate);
      }

      sql += ` ORDER BY t.date DESC`;

      this.db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }

  /**
   * Assigne une transaction à un membre
   */
  assignTransactionToMember(transactionId, memberId, splitAmount = null) {
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT OR REPLACE INTO transaction_members (transaction_id, member_id, split_amount) 
         VALUES (?, ?, ?)`,
        [transactionId, memberId, splitAmount],
        function(err) {
          if (err) reject(err);
          else resolve({ transaction_id: transactionId, member_id: memberId, split_amount: splitAmount });
        }
      );
    });
  }

  /**
   * Supprime l'assignation d'une transaction à un membre
   */
  removeTransactionMember(transactionId, memberId) {
    return new Promise((resolve, reject) => {
      this.db.run(
        'DELETE FROM transaction_members WHERE transaction_id = ? AND member_id = ?',
        [transactionId, memberId],
        (err) => {
          if (err) reject(err);
          else resolve({ success: true });
        }
      );
    });
  }

  /**
   * Récupère les statistiques par membre pour un mois donné
   */
  getMemberStats(year, month) {
    return new Promise((resolve, reject) => {
      const startDate = `${year}-${String(month).padStart(2, '0')}-01`;
      const endDate = `${year}-${String(month + 1).padStart(2, '0')}-01`;

      this.db.all(
        `SELECT 
          m.id,
          m.name,
          m.color,
          m.emoji,
          m.type,
          COALESCE(SUM(COALESCE(tm.split_amount, t.amount)), 0) as total,
          COUNT(t.id) as transaction_count
        FROM members m
        LEFT JOIN transaction_members tm ON m.id = tm.member_id
        LEFT JOIN transactions t ON tm.transaction_id = t.id 
          AND t.type = 'expense'
          AND t.date >= ? AND t.date < ?
        WHERE m.is_active = 1
        GROUP BY m.id, m.name, m.color, m.emoji, m.type
        ORDER BY CASE m.type WHEN 'primary' THEN 0 ELSE 1 END, m.name`,
        [startDate, endDate],
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        }
      );
    });
  }

  /**
   * Récupère le membre assigné à une transaction
   */
  getTransactionMember(transactionId) {
    return new Promise((resolve, reject) => {
      this.db.get(
        `SELECT m.*, tm.split_amount 
         FROM transaction_members tm
         JOIN members m ON tm.member_id = m.id
         WHERE tm.transaction_id = ?`,
        [transactionId],
        (err, row) => {
          if (err) reject(err);
          else resolve(row || null);
        }
      );
    });
  }

  // Ferme la connexion
  close() {
    if (this.db) {
      this.db.close((err) => {
        if (err) console.error('[DB] Error closing database:', err);
        else console.log('[DB] Database closed');
      });
    }
  }
}

module.exports = { DatabaseService };
