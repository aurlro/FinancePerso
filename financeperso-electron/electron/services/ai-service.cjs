/**
 * AI Service - Gestion de la catégorisation automatique par IA
 * Supporte Gemini (Google) et OpenAI avec fallback sur règles simples
 */

class AIService {
  constructor(settings = {}) {
    this.provider = settings.provider || 'gemini';
    this.apiKey = settings.apiKey || '';
    this.model = settings.model || 'gemini-2.0-flash';
    this.openaiModel = settings.openaiModel || 'gpt-3.5-turbo';
    this.enabled = settings.enabled !== false;
    
    // Règles de fallback par défaut (marchands connus)
    this.fallbackRules = [
      { pattern: /CARREFOUR|LECLERC|AUCHAN|INTERMARCHE|LIDL|ALDI/i, category: 'Alimentation', confidence: 0.95 },
      { pattern: /TOTAL|ELF|SHELL|BP|ESSO|AVIA/i, category: 'Transport', confidence: 0.95 },
      { pattern: /EDF|GAZ|EAU|ENGIE|VEOLIA|SUEZ/i, category: 'Logement', confidence: 0.9 },
      { pattern: /PHARMACIE|PARAPHARMACIE/i, category: 'Santé', confidence: 0.9 },
      { pattern: /NETFLIX|SPOTIFY|DISNEY|AMAZON PRIME|YOUTUBE/i, category: 'Loisirs', confidence: 0.9 },
      { pattern: /AMAZON|CDISCOUNT|FNAC|DARTY/i, category: 'Shopping', confidence: 0.85 },
      { pattern: /SALAIRE|VIREMENT|PAIE|PAYE/i, category: 'Revenus', confidence: 0.9 },
      { pattern: /LOYER|CHARGES|COPRO/i, category: 'Logement', confidence: 0.9 },
      { pattern: /RESTAURANT|MCDONALD|BURGER|PIZZA|SUSHI/i, category: 'Restauration', confidence: 0.85 },
      { pattern: /SNCF|RATP|TRAIN|BUS|METRO/i, category: 'Transport', confidence: 0.9 },
      { pattern: /MEDECIN|DENTISTE|LABORATOIRE|CLINIQUE/i, category: 'Santé', confidence: 0.9 },
      { pattern: /ASSURANCE|MUTUELLE|MAAF|MACIF|MAIF/i, category: 'Assurances', confidence: 0.85 },
      { pattern: /BANQUE|CARTE|RETRAIT|FRAIS/i, category: 'Banque', confidence: 0.8 },
      { pattern: /IMPOTS|TAXE|FISCAL/i, category: 'Impôts', confidence: 0.95 },
      { pattern: /TELEPHONE|MOBILE|ORANGE|SFR|FREE|BOUYGUES/i, category: 'Télécom', confidence: 0.85 },
      { pattern: /INTERNET|BOX|FAI/i, category: 'Télécom', confidence: 0.85 },
    ];
    
    // Catégories disponibles
    this.categories = [
      'Alimentation',
      'Transport', 
      'Logement',
      'Santé',
      'Loisirs',
      'Shopping',
      'Restauration',
      'Revenus',
      'Assurances',
      'Banque',
      'Impôts',
      'Télécom',
      'Épargne',
      'Inconnu'
    ];
  }

  /**
   * Met à jour la configuration du service IA
   */
  updateConfig(settings) {
    this.provider = settings.provider || this.provider;
    this.apiKey = settings.apiKey || this.apiKey;
    this.model = settings.model || this.model;
    this.openaiModel = settings.openaiModel || this.openaiModel;
    this.enabled = settings.enabled !== undefined ? settings.enabled : this.enabled;
  }

  /**
   * Catégorise une transaction par IA ou fallback
   * @param {string} label - Libellé de la transaction
   * @param {number} amount - Montant de la transaction
   * @returns {Promise<{category: string, confidence: number, source: string}>}
   */
  async categorize(label, amount = 0) {
    if (!label) {
      return { category: 'Inconnu', confidence: 0, source: 'fallback' };
    }

    const normalizedLabel = label.toString().toUpperCase().trim();
    
    // 1. Essayer d'abord les règles de fallback (rapide, offline)
    const fallbackResult = this._applyFallbackRules(normalizedLabel);
    if (fallbackResult.confidence >= 0.9) {
      return { ...fallbackResult, source: 'fallback' };
    }

    // 2. Si IA désactivée ou pas de clé API, retourner le fallback
    if (!this.enabled || !this.apiKey) {
      return { ...fallbackResult, source: 'fallback' };
    }

    // 3. Essayer l'IA
    try {
      const aiResult = await this._callAI(normalizedLabel, amount);
      return { ...aiResult, source: 'ai' };
    } catch (error) {
      console.error('[AIService] AI categorization failed:', error.message);
      // Fallback en cas d'erreur IA
      return { ...fallbackResult, source: 'fallback_error' };
    }
  }

  /**
   * Catégorise plusieurs transactions en batch
   * @param {Array<{label: string, amount: number}>} transactions
   * @returns {Promise<Array<{category: string, confidence: number, source: string}>>}
   */
  async categorizeBatch(transactions) {
    const results = [];
    
    // Traiter en parallèle par petits groupes pour éviter de surcharger l'API
    const batchSize = 5;
    for (let i = 0; i < transactions.length; i += batchSize) {
      const batch = transactions.slice(i, i + batchSize);
      const batchPromises = batch.map(tx => this.categorize(tx.label, tx.amount));
      const batchResults = await Promise.all(batchPromises);
      results.push(...batchResults);
      
      // Petit délai entre les batchs pour respecter les rate limits
      if (i + batchSize < transactions.length) {
        await this._sleep(100);
      }
    }
    
    return results;
  }

  /**
   * Teste la connexion à l'API IA
   * @returns {Promise<{success: boolean, message: string}>}
   */
  async testConnection() {
    if (!this.apiKey) {
      return { success: false, message: 'Clé API non configurée' };
    }

    try {
      if (this.provider === 'gemini') {
        return await this._testGeminiConnection();
      } else if (this.provider === 'openai') {
        return await this._testOpenAIConnection();
      } else {
        return { success: false, message: `Provider ${this.provider} non supporté` };
      }
    } catch (error) {
      return { success: false, message: error.message };
    }
  }

  /**
   * Applique les règles de fallback sur un libellé
   * @private
   */
  _applyFallbackRules(label) {
    for (const rule of this.fallbackRules) {
      if (rule.pattern.test(label)) {
        return {
          category: rule.category,
          confidence: rule.confidence
        };
      }
    }
    
    // Si c'est un montant positif, c'est probablement un revenu
    if (label.includes('VIREMENT') || label.includes('REMBOURSEMENT')) {
      return { category: 'Revenus', confidence: 0.6 };
    }
    
    return { category: 'Inconnu', confidence: 0.3 };
  }

  /**
   * Appelle l'API IA pour la catégorisation
   * @private
   */
  async _callAI(label, amount) {
    if (this.provider === 'gemini') {
      return await this._callGemini(label, amount);
    } else if (this.provider === 'openai') {
      return await this._callOpenAI(label, amount);
    } else {
      throw new Error(`Provider ${this.provider} non supporté`);
    }
  }

  /**
   * Appelle l'API Gemini
   * @private
   */
  async _callGemini(label, amount) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${this.apiKey}`;
    
    const prompt = `Catégorise cette transaction bancaire:
Libellé: "${label}"
Montant: ${amount}€

Réponds UNIQUEMENT avec un objet JSON au format exact suivant (sans markdown, sans code block):
{"category": "NOM_CATEGORIE", "confidence": 0.XX}

Catégories possibles: ${this.categories.join(', ')}

Règles:
- Si montant > 0 et contient "VIREMENT", "SALAIRE", "REMBOURSEMENT" → Revenus
- Si contient "CARREFOUR", "LECLERC", "AUCHAN" → Alimentation
- Si contient "TOTAL", "SHELL", "ESSO" → Transport
- Si contient "PHARMACIE", "MEDECIN" → Santé
- confidence entre 0 et 1 selon la certitude

Réponse JSON uniquement:`;

    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: prompt }]
        }],
        generationConfig: {
          temperature: 0.1,
          maxOutputTokens: 100
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Gemini API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const text = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
    
    return this._parseAIResponse(text);
  }

  /**
   * Appelle l'API OpenAI
   * @private
   */
  async _callOpenAI(label, amount) {
    const url = 'https://api.openai.com/v1/chat/completions';
    
    const prompt = `Catégorise cette transaction bancaire:
Libellé: "${label}"
Montant: ${amount}€

Réponds UNIQUEMENT avec un objet JSON au format exact suivant:
{"category": "NOM_CATEGORIE", "confidence": 0.XX}

Catégories possibles: ${this.categories.join(', ')}

Réponse JSON uniquement, sans markdown.`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`
      },
      body: JSON.stringify({
        model: this.openaiModel,
        messages: [{ role: 'user', content: prompt }],
        temperature: 0.1,
        max_tokens: 100
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`OpenAI API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const text = data.choices?.[0]?.message?.content || '';
    
    return this._parseAIResponse(text);
  }

  /**
   * Parse la réponse de l'IA
   * @private
   */
  _parseAIResponse(text) {
    try {
      // Nettoyer le texte (enlever markdown code blocks si présents)
      const cleanText = text
        .replace(/```json\s*/g, '')
        .replace(/```\s*/g, '')
        .trim();
      
      const parsed = JSON.parse(cleanText);
      
      // Valider et normaliser
      let category = parsed.category || 'Inconnu';
      let confidence = parseFloat(parsed.confidence) || 0.5;
      
      // S'assurer que la catégorie est dans la liste
      if (!this.categories.includes(category)) {
        // Chercher la catégorie la plus proche
        const normalized = this.categories.find(c => 
          c.toLowerCase() === category.toLowerCase()
        );
        category = normalized || 'Inconnu';
      }
      
      // Normaliser la confidence
      confidence = Math.max(0, Math.min(1, confidence));
      
      return { category, confidence };
    } catch (error) {
      console.error('[AIService] Failed to parse AI response:', text, error);
      // Essayer d'extraire la catégorie du texte brut
      for (const cat of this.categories) {
        if (text.toLowerCase().includes(cat.toLowerCase())) {
          return { category: cat, confidence: 0.5 };
        }
      }
      return { category: 'Inconnu', confidence: 0.3 };
    }
  }

  /**
   * Teste la connexion Gemini
   * @private
   */
  async _testGeminiConnection() {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${this.model}:generateContent?key=${this.apiKey}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: 'Dis "OK"' }] }]
      })
    });

    if (!response.ok) {
      const error = await response.json();
      return { 
        success: false, 
        message: `Erreur Gemini: ${error.error?.message || response.statusText}` 
      };
    }

    return { success: true, message: 'Connexion Gemini réussie' };
  }

  /**
   * Teste la connexion OpenAI
   * @private
   */
  async _testOpenAIConnection() {
    const url = 'https://api.openai.com/v1/models';
    
    const response = await fetch(url, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` }
    });

    if (!response.ok) {
      const error = await response.json();
      return { 
        success: false, 
        message: `Erreur OpenAI: ${error.error?.message || response.statusText}` 
      };
    }

    return { success: true, message: 'Connexion OpenAI réussie' };
  }

  /**
   * Pause utilitaire
   * @private
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

module.exports = { AIService };
