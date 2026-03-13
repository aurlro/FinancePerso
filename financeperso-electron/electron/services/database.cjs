/**
 * Database Service - better-sqlite3
 * Gestion de la base de données SQLite locale
 */

const Database = require('better-sqlite3');
const fs = require('node:fs');
const path = require('node:path');

class DatabaseService {
  constructor(dbPath) {
    this.dbPath = dbPath;
    this.db = null;
    
    // S'assurer que le répertoire existe
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
  }

  async initialize() {
    try {
      this.db = new Database(this.dbPath);
      
      // Mode WAL pour meilleures performances
      this.db.pragma('journal_mode = WAL');
      this.db.pragma('foreign_keys = ON');
      
      // Créer les tables
      this.createTables();
      
      console.log('[Database] Initialized:', this.dbPath);
      return true;
    } catch (error) {
      console.error('[Database] Initialization error:', error);
      throw error;
    }
  }

  createTables() {
    // Transactions
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        label TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        subcategory TEXT,
        type TEXT CHECK(type IN ('debit', 'credit')),
        account TEXT,
        notes TEXT,
        beneficiary TEXT,
        member_id INTEGER,
        is_recurring BOOLEAN DEFAULT 0,
        is_validated BOOLEAN DEFAULT 0,
        sync_status TEXT DEFAULT 'pending',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);
      CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category);
      CREATE INDEX IF NOT EXISTS idx_transactions_sync ON transactions(sync_status);
    `);

    // Categories
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        emoji TEXT DEFAULT '📁',
        color TEXT DEFAULT '#64748B',
        type TEXT CHECK(type IN ('fixed', 'variable', 'income', 'savings')),
        budget_amount REAL,
        is_active BOOLEAN DEFAULT 1
      );
      
      -- Insert categories par défaut
      INSERT OR IGNORE INTO categories (name, emoji, color, type) VALUES
        ('Alimentation', '🍽️', '#10B981', 'variable'),
        ('Transport', '🚗', '#3B82F6', 'variable'),
        ('Logement', '🏠', '#8B5CF6', 'fixed'),
        ('Santé', '⚕️', '#EF4444', 'variable'),
        ('Loisirs', '🎮', '#F59E0B', 'variable'),
        ('Revenus', '💰', '#10B981', 'income'),
        ('Épargne', '🐷', '#EC4899', 'savings'),
        ('Inconnu', '❓', '#6B7280', 'variable');
    `);

    // Members
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT CHECK(type IN ('primary', 'secondary')),
        email TEXT,
        color TEXT,
        is_active BOOLEAN DEFAULT 1
      );
      
      -- Insert member par défaut
      INSERT OR IGNORE INTO members (name, type, color) VALUES
        ('Moi', 'primary', '#3B82F6');
    `);

    // Budgets
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        period TEXT DEFAULT 'monthly',
        year INTEGER,
        month INTEGER,
        UNIQUE(category, year, month)
      );
    `);

    // Settings
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
    `);

    // Learning Rules - Règles d'apprentissage IA
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS learning_rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pattern TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        confidence REAL DEFAULT 1.0,
        usage_count INTEGER DEFAULT 0,
        source TEXT DEFAULT 'manual',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      );
      CREATE INDEX IF NOT EXISTS idx_learning_rules_pattern ON learning_rules(pattern);
      CREATE INDEX IF NOT EXISTS idx_learning_rules_category ON learning_rules(category);
    `);
  }

  query(sql, params = []) {
    if (!this.db) throw new Error('Database not initialized');
    
    const stmt = this.db.prepare(sql);
    
    if (sql.trim().toLowerCase().startsWith('select')) {
      return params.length > 0 ? stmt.all(...params) : stmt.all();
    } else {
      return params.length > 0 ? stmt.run(...params) : stmt.run();
    }
  }

  transaction(operations) {
    if (!this.db) throw new Error('Database not initialized');
    
    const transaction = this.db.transaction((ops) => {
      const results = [];
      for (const op of ops) {
        const stmt = this.db.prepare(op.sql);
        results.push(op.params ? stmt.run(...op.params) : stmt.run());
      }
      return results;
    });
    
    return transaction(operations);
  }

  // Méthodes utilitaires
  getTransactions(limit = 100, offset = 0) {
    return this.query(
      `SELECT t.*, c.emoji, c.color 
       FROM transactions t 
       LEFT JOIN categories c ON t.category = c.name 
       ORDER BY t.date DESC 
       LIMIT ? OFFSET ?`,
      [limit, offset]
    );
  }

  getTransactionsByMonth(year, month) {
    return this.query(
      `SELECT t.*, c.emoji, c.color 
       FROM transactions t 
       LEFT JOIN categories c ON t.category = c.name 
       WHERE strftime('%Y', t.date) = ? AND strftime('%m', t.date) = ?
       ORDER BY t.date DESC`,
      [year.toString(), month.toString().padStart(2, '0')]
    );
  }

  getDashboardStats(year, month) {
    const stats = this.query(`
      SELECT 
        COALESCE(SUM(CASE WHEN type = 'credit' THEN amount ELSE 0 END), 0) as total_income,
        COALESCE(SUM(CASE WHEN type = 'debit' THEN amount ELSE 0 END), 0) as total_expense,
        COALESCE(SUM(CASE WHEN type = 'credit' THEN amount ELSE -amount END), 0) as balance
      FROM transactions
      WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
    `, [year.toString(), month.toString().padStart(2, '0')]);
    
    const byCategory = this.query(`
      SELECT 
        category,
        COALESCE(SUM(amount), 0) as total
      FROM transactions
      WHERE type = 'debit' 
        AND strftime('%Y', date) = ? 
        AND strftime('%m', date) = ?
      GROUP BY category
      ORDER BY total DESC
    `, [year.toString(), month.toString().padStart(2, '0')]);
    
    return { stats: stats[0], byCategory };
  }

  insertTransaction(data) {
    const result = this.query(`
      INSERT INTO transactions (date, label, amount, category, type, account, notes, member_id, sync_status)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    `, [
      data.date,
      data.label,
      data.amount,
      data.category || 'Inconnu',
      data.type || (data.amount >= 0 ? 'credit' : 'debit'),
      data.account,
      data.notes,
      data.member_id || 1
    ]);
    
    return { id: result.lastInsertRowid, ...data };
  }

  updateTransaction(id, data) {
    this.query(`
      UPDATE transactions 
      SET date = ?, label = ?, amount = ?, category = ?, type = ?, 
          account = ?, notes = ?, updated_at = CURRENT_TIMESTAMP, sync_status = 'pending'
      WHERE id = ?
    `, [
      data.date, data.label, data.amount, data.category, data.type,
      data.account, data.notes, id
    ]);
    
    return { id, ...data };
  }

  deleteTransaction(id) {
    return this.query('DELETE FROM transactions WHERE id = ?', [id]);
  }

  getCategories() {
    return this.query('SELECT * FROM categories WHERE is_active = 1 ORDER BY name');
  }

  // ========== LEARNING RULES METHODS ==========

  /**
   * Recherche une règle exacte par pattern
   * @param {string} pattern - Le pattern exact à rechercher
   * @returns {Object|null} La règle trouvée ou null
   */
  findRuleByPattern(pattern) {
    try {
      const result = this.query(
        'SELECT * FROM learning_rules WHERE pattern = ? COLLATE NOCASE',
        [pattern]
      );
      return result.length > 0 ? result[0] : null;
    } catch (error) {
      console.error('[Database] Error finding rule by pattern:', error);
      return null;
    }
  }

  /**
   * Recherche des règles par correspondance partielle (LIKE)
   * @param {string} pattern - Le pattern partiel à rechercher
   * @param {number} limit - Nombre maximum de résultats
   * @returns {Array} Liste des règles correspondantes
   */
  findPartialRule(pattern, limit = 5) {
    try {
      const searchPattern = `%${pattern}%`;
      return this.query(
        `SELECT * FROM learning_rules 
         WHERE pattern LIKE ? COLLATE NOCASE 
         ORDER BY usage_count DESC, confidence DESC 
         LIMIT ?`,
        [searchPattern, limit]
      );
    } catch (error) {
      console.error('[Database] Error finding partial rule:', error);
      return [];
    }
  }

  /**
   * Crée une nouvelle règle d'apprentissage
   * @param {string} pattern - Le pattern à reconnaître
   * @param {string} category - La catégorie associée
   * @param {number} confidence - Le niveau de confiance (0-1)
   * @param {string} source - La source de la règle ('manual', 'ai', 'import')
   * @returns {Object} La règle créée
   */
  createRule(pattern, category, confidence = 1.0, source = 'manual') {
    try {
      const result = this.query(
        `INSERT INTO learning_rules (pattern, category, confidence, source, usage_count) 
         VALUES (?, ?, ?, ?, 1)
         ON CONFLICT(pattern) DO UPDATE SET
           category = excluded.category,
           confidence = excluded.confidence,
           usage_count = usage_count + 1,
           updated_at = CURRENT_TIMESTAMP`,
        [pattern.toUpperCase().trim(), category, confidence, source]
      );
      
      return { 
        id: result.lastInsertRowid || result.changes,
        pattern: pattern.toUpperCase().trim(),
        category,
        confidence,
        source
      };
    } catch (error) {
      console.error('[Database] Error creating rule:', error);
      throw error;
    }
  }

  /**
   * Incrémente le compteur d'utilisation d'une règle
   * @param {string} pattern - Le pattern de la règle
   * @returns {boolean} Succès de l'opération
   */
  incrementRuleUsage(pattern) {
    try {
      this.query(
        `UPDATE learning_rules 
         SET usage_count = usage_count + 1, updated_at = CURRENT_TIMESTAMP 
         WHERE pattern = ? COLLATE NOCASE`,
        [pattern]
      );
      return true;
    } catch (error) {
      console.error('[Database] Error incrementing rule usage:', error);
      return false;
    }
  }

  /**
   * Récupère toutes les règles d'apprentissage
   * @param {number} limit - Nombre maximum de résultats
   * @param {number} offset - Offset pour la pagination
   * @returns {Array} Liste des règles
   */
  getAllRules(limit = 100, offset = 0) {
    try {
      return this.query(
        `SELECT * FROM learning_rules 
         ORDER BY usage_count DESC, updated_at DESC 
         LIMIT ? OFFSET ?`,
        [limit, offset]
      );
    } catch (error) {
      console.error('[Database] Error getting all rules:', error);
      return [];
    }
  }

  /**
   * Récupère les règles par catégorie
   * @param {string} category - La catégorie filtrée
   * @returns {Array} Liste des règles
   */
  getRulesByCategory(category) {
    try {
      return this.query(
        `SELECT * FROM learning_rules 
         WHERE category = ? COLLATE NOCASE
         ORDER BY usage_count DESC`,
        [category]
      );
    } catch (error) {
      console.error('[Database] Error getting rules by category:', error);
      return [];
    }
  }

  /**
   * Supprime une règle d'apprentissage
   * @param {number} id - L'ID de la règle
   * @returns {boolean} Succès de l'opération
   */
  deleteRule(id) {
    try {
      this.query('DELETE FROM learning_rules WHERE id = ?', [id]);
      return true;
    } catch (error) {
      console.error('[Database] Error deleting rule:', error);
      return false;
    }
  }

  /**
   * Récupère les statistiques des règles
   * @returns {Object} Statistiques
   */
  getRulesStats() {
    try {
      const stats = this.query(`
        SELECT 
          COUNT(*) as total_rules,
          COUNT(CASE WHEN source = 'ai' THEN 1 END) as ai_rules,
          COUNT(CASE WHEN source = 'manual' THEN 1 END) as manual_rules,
          SUM(usage_count) as total_usage
        FROM learning_rules
      `);
      return stats[0];
    } catch (error) {
      console.error('[Database] Error getting rules stats:', error);
      return { total_rules: 0, ai_rules: 0, manual_rules: 0, total_usage: 0 };
    }
  }

  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
    }
  }
}

module.exports = { DatabaseService };
