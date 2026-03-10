
-- Add exclude_from_income column to categories
ALTER TABLE public.categories ADD COLUMN exclude_from_income boolean NOT NULL DEFAULT false;

-- Insert "Contribution Partenaire" as a default category
INSERT INTO public.categories (name, color, icon, is_default, exclude_from_income)
VALUES ('Contribution Partenaire', '#a855f7', 'users', true, true);
