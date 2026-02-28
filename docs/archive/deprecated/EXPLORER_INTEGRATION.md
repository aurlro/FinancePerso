# Guide d'Intégration de l'Explorateur

## 🚀 Intégration dans les Pages Existantes

### 1. Page Synthèse (3_Synthese.py)

Ajoutez dans les imports :
```python
from modules.ui.explorer import render_explore_button, render_category_pill
```

Dans la section des catégories (après le graphique) :
```python
# Liste des catégories avec boutons explorer
df_cat = prepare_expense_dataframe(df_current, cat_emoji_map)
if not df_cat.empty:
    st.subheader("📂 Explorer par Catégorie")
    cat_sums = df_cat.groupby(['raw_cat', 'Catégorie']).agg({
        'amount': ['sum', 'count']
    }).reset_index()
    
    for _, row in cat_sums.head(10).iterrows():
        render_category_pill(
            category=row['raw_cat'],
            amount=row[('amount', 'sum')],
            count=row[('amount', 'count')],
            emoji=cat_emoji_map.get(row['raw_cat'], '📂'),
            from_page='3_Synthese'
        )
```

### 2. Page Validation (2_Validation.py)

Ajoutez dans les imports :
```python
from modules.ui.explorer import render_explore_button
```

Dans chaque expander de catégorie :
```python
with st.expander(f"📂 {category} ({count} transactions)"):
    col1, col2 = st.columns([4, 1])
    with col2:
        render_explore_button(
            'category', 
            category, 
            from_page='2_Validation',
            label="📊 Voir tout",
            use_container_width=True
        )
    # ... reste du contenu
```

### 3. Page Assistant (5_Assistant.py)

Dans les insights de tendances :
```python
from modules.ui.explorer import launch_explorer

if st.button(f"🔍 Explorer {insight['category']}", use_container_width=True):
    launch_explorer('category', insight['category'], from_page='5_Assistant')
```

### 4. Tags - Intégration Globale

Pour afficher les tags cliquables depuis n'importe où :
```python
from modules.ui.explorer import render_tag_pill
from modules.db.tags import get_all_tags

tags = get_all_tags()
for tag in tags:
    # Calculer montant et count
    render_tag_pill(
        tag=tag['name'],
        amount=tag['total_amount'],
        count=tag['transaction_count'],
        from_page='current_page'
    )
```

## 📝 Exemple Complet - Composant Réutilisable

Créez un composant pour afficher les top catégories avec exploration :

```python
# modules/ui/components/category_list_explorer.py

from modules.ui.explorer import render_explore_button

def render_category_list_with_explore(
    df: pd.DataFrame, 
    cat_emoji_map: dict,
    limit: int = 10,
    from_page: str = '3_Synthese'
):
    '''Render list of categories with explore buttons.'''
    
    if df.empty:
        return
    
    # Group by category
    df_cat = df.groupby('category_validated').agg({
        'amount': ['sum', 'count', 'mean']
    }).reset_index()
    df_cat.columns = ['category', 'total', 'count', 'avg']
    
    # Sort by total amount
    df_cat = df_cat.sort_values('total', ascending=False).head(limit)
    
    # Render each category
    for _, row in df_cat.iterrows():
        cat = row['category']
        emoji = cat_emoji_map.get(cat, '🏷️')
        
        with st.container(border=True):
            cols = st.columns([0.5, 2.5, 1, 1, 1])
            
            cols[0].markdown(f"**{emoji}**")
            cols[1].markdown(f"**{cat}**")
            cols[2].markdown(f"{row['total']:,.2f} €")
            cols[3].caption(f"{row['count']} transactions")
            
            with cols[4]:
                render_explore_button(
                    'category',
                    cat,
                    from_page,
                    label="🔍",
                    use_container_width=True
                )
```

## 🎨 Style et UX

### Boutons Sous les Graphiques
```python
# Après un graphique de catégories
cols = st.columns(len(categories))
for i, cat in enumerate(categories):
    with cols[i]:
        st.button(f"📂 {cat}", key=f"cat_{i}", 
                 on_click=launch_explorer, 
                 args=('category', cat))
```

### Badges Clickables
```python
# Dans les tableaux ou listes
st.markdown(f"""
    <a href="/Explorer?type=category&value={category}&from={page}" 
       style="text-decoration: none;">
        <span style="background: #e0f2fe; padding: 4px 12px; border-radius: 12px;">
            📂 {category}
        </span>
    </a>
""", unsafe_allow_html=True)
```

## 🔗 URLs Directes

Vous pouvez aussi créer des liens directs :
```python
# Lien vers exploration d'une catégorie
st.markdown(f"[📂 Explorer {category}](/Explorer?type=category&value={category})")

# Lien vers exploration d'un tag
st.markdown(f"[🏷️ Explorer #{tag}](/Explorer?type=tag&value={tag})")
```

## 🧪 Test de l'Intégration

1. Lancez l'application
2. Allez sur la page Synthèse
3. Vérifiez que les boutons 🔍 apparaissent
4. Cliquez sur un bouton - vous devriez être redirigé vers `/Explorer`
5. Vérifiez que les filtres fonctionnent
6. Testez le bouton "Retour"

## 🐛 Dépannage

### Problème : Le bouton ne fait rien
- Vérifiez que `from_page` est correct (nom du fichier sans extension)
- Vérifiez dans les logs que la navigation est appelée

### Problème : Aucune transaction dans l'explorateur
- Vérifiez que la catégorie existe bien dans les transactions
- Vérifiez la casse (la comparaison est insensible à la casse)

### Problème : Les filtres ne fonctionnent pas
- Vérifiez que les colonnes existent dans le DataFrame
- Vérifiez les types de données (date, amount)
