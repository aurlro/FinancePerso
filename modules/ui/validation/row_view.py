
import streamlit as st
from modules.ui.components.avatar_selector import render_avatar_selector
from modules.ui.components.chip_selector import render_chip_selector
from modules.utils import clean_label
from modules.db.categories import get_categories_with_emojis

def render_validation_row(
    row_data: dict,
    all_members: list,
    all_categories: list,
    cat_emoji_map: dict,
    on_validate: callable,
    key_prefix: str
):
    """
    Render a single transaction row in 'Apple Card' style.
    """
    # Start container
    # We use a custom container class for hover effects (via CSS)
    # Since we can't inject classes easily to st.container, we wrap content or use st.markdown with unsafe_html for the box?
    # Actually, standard Streamlit columns are cleanest. We just style the blocks.
    
    with st.container():
        # Layout: Date | Label | Amount | Category | Member | Actions
        c_date, c_label, c_amount, c_cat, c_mem, c_act = st.columns([1, 3, 1.5, 2, 1.5, 1])
        
        row_id = row_data['id']
        label = clean_label(row_data['label'])
        date_str = row_data['date'] # "DD/MM/YYYY" or similar
        amount = row_data['total_amount']
        
        # State Management
        # Pre-fill defaults
        cat_key = f"{key_prefix}_cat_{row_id}"
        mem_key = f"{key_prefix}_mem_{row_id}"
        
        # Date
        with c_date:
            st.caption(date_str)
            
        # Label
        with c_label:
            st.markdown(f"**{label}**")
            # Show small count if grouped?
            if row_data.get('count', 1) > 1:
                st.caption(f"{row_data['count']} opérations")
                
        # Amount
        with c_amount:
            color = "red" if amount < 0 else "green"
            st.markdown(f":{color}[**{amount:,.2f} €**]")
            
        # Category (Pill/Selectbox)
        with c_cat:
            current_cat = st.session_state.get(cat_key, row_data.get('category', 'Inconnu'))
            # Use selectbox for simplicity and robustness
            idx = 0
            if current_cat in all_categories:
                idx = all_categories.index(current_cat)
                
            new_cat = st.selectbox(
                "Catégorie", 
                all_categories, 
                index=idx, 
                key=cat_key, 
                label_visibility="collapsed",
                format_func=lambda x: f"{cat_emoji_map.get(x, '🏷️')} {x}"
            )
            
        # Member (Avatar)
        with c_mem:
            current_mem = st.session_state.get(mem_key, row_data.get('member', ''))
            
            # Use our new Avatar Selector
            # We need a callback or just read the key on validate
            render_avatar_selector(
                label="", # No label to save space
                options=["Aurélien", "Élise", "Maison", "Famille"], # Top options
                current_value=current_mem,
                key=mem_key
            )
            
        # Action (Validate CTA)
        with c_act:
            if st.button("✅", key=f"{key_prefix}_btn_{row_id}", type="primary", use_container_width=True):
                # Trigger validation logic
                # Capture current state from widgets
                final_cat = st.session_state[cat_key]
                final_mem = st.session_state.get(mem_key, current_mem) # Avatar might store in its own key or return
                # NOTE: The avatar selector writes to key `mem_key`. Wait, if it has a list inside?
                # The render_avatar_selector returns the value but doesn't auto-write to session_state unless loop?
                # Actually my implementation of avatar_selector re-runs on click.
                # So the value should be updating `current_mem` on pass-through?
                # Wait, render_avatar_selector uses st.button which triggers rerun. 
                # Ideally it shouldn't be inside a form.
                
                on_validate(row_id, final_cat, final_mem)
                
        st.markdown("---")
