
-- ============================================
-- TABLE: households
-- ============================================
CREATE TABLE public.households (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  name TEXT NOT NULL DEFAULT 'Mon foyer',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.households ENABLE ROW LEVEL SECURITY;

-- ============================================
-- TABLE: profiles
-- ============================================
CREATE TABLE public.profiles (
  id UUID NOT NULL PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  household_id UUID REFERENCES public.households(id) ON DELETE SET NULL,
  display_name TEXT,
  role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('owner', 'member')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- ============================================
-- HELPER FUNCTION: get_user_household_id (after profiles exists)
-- ============================================
CREATE OR REPLACE FUNCTION public.get_user_household_id(user_uuid uuid)
RETURNS uuid
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT household_id FROM public.profiles WHERE id = user_uuid LIMIT 1;
$$;

-- ============================================
-- TABLE: categories
-- ============================================
CREATE TABLE public.categories (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  household_id UUID REFERENCES public.households(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  icon TEXT,
  color TEXT,
  is_default BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;

-- ============================================
-- TABLE: bank_accounts
-- ============================================
CREATE TYPE public.account_type AS ENUM ('perso_a', 'perso_b', 'joint');

CREATE TABLE public.bank_accounts (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  household_id UUID NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
  owner_user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  bank_name TEXT,
  account_type public.account_type NOT NULL DEFAULT 'joint',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.bank_accounts ENABLE ROW LEVEL SECURITY;

-- ============================================
-- TABLE: transactions
-- ============================================
CREATE TABLE public.transactions (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  bank_account_id UUID NOT NULL REFERENCES public.bank_accounts(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  label TEXT NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
  is_internal_transfer BOOLEAN NOT NULL DEFAULT false,
  matched_transfer_id UUID REFERENCES public.transactions(id) ON DELETE SET NULL,
  notes TEXT,
  import_hash TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.transactions ENABLE ROW LEVEL SECURITY;

CREATE INDEX idx_transactions_account ON public.transactions(bank_account_id);
CREATE INDEX idx_transactions_date ON public.transactions(date);
CREATE INDEX idx_transactions_hash ON public.transactions(import_hash);

-- ============================================
-- TABLE: categorization_rules
-- ============================================
CREATE TABLE public.categorization_rules (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  household_id UUID NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  regex_pattern TEXT NOT NULL,
  category_id UUID NOT NULL REFERENCES public.categories(id) ON DELETE CASCADE,
  priority INTEGER NOT NULL DEFAULT 0,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.categorization_rules ENABLE ROW LEVEL SECURITY;

-- ============================================
-- TRIGGER: auto-create profile on signup
-- ============================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  new_household_id UUID;
BEGIN
  INSERT INTO public.households (name) VALUES ('Mon foyer') RETURNING id INTO new_household_id;
  INSERT INTO public.profiles (id, household_id, display_name, role)
  VALUES (NEW.id, new_household_id, COALESCE(NEW.raw_user_meta_data->>'display_name', NEW.email), 'owner');
  RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- ============================================
-- TRIGGER: updated_at
-- ============================================
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
SET search_path = public
AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER update_households_updated_at BEFORE UPDATE ON public.households FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER update_bank_accounts_updated_at BEFORE UPDATE ON public.bank_accounts FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();
CREATE TRIGGER update_rules_updated_at BEFORE UPDATE ON public.categorization_rules FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- ============================================
-- RLS POLICIES: households
-- ============================================
CREATE POLICY "Users can view own household" ON public.households FOR SELECT USING (id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Users can update own household" ON public.households FOR UPDATE USING (id = public.get_user_household_id(auth.uid()));

-- ============================================
-- RLS POLICIES: profiles
-- ============================================
CREATE POLICY "Users can view household members" ON public.profiles FOR SELECT USING (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (id = auth.uid());

-- ============================================
-- RLS POLICIES: categories
-- ============================================
CREATE POLICY "View default and household categories" ON public.categories FOR SELECT USING (household_id IS NULL OR household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Create household categories" ON public.categories FOR INSERT WITH CHECK (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Update household categories" ON public.categories FOR UPDATE USING (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Delete household categories" ON public.categories FOR DELETE USING (household_id = public.get_user_household_id(auth.uid()));

-- ============================================
-- RLS POLICIES: bank_accounts
-- ============================================
CREATE POLICY "View household accounts" ON public.bank_accounts FOR SELECT USING (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Create household accounts" ON public.bank_accounts FOR INSERT WITH CHECK (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Update household accounts" ON public.bank_accounts FOR UPDATE USING (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Delete household accounts" ON public.bank_accounts FOR DELETE USING (household_id = public.get_user_household_id(auth.uid()));

-- ============================================
-- RLS POLICIES: transactions
-- ============================================
CREATE POLICY "View household transactions" ON public.transactions FOR SELECT USING (bank_account_id IN (SELECT id FROM public.bank_accounts WHERE household_id = public.get_user_household_id(auth.uid())));
CREATE POLICY "Create household transactions" ON public.transactions FOR INSERT WITH CHECK (bank_account_id IN (SELECT id FROM public.bank_accounts WHERE household_id = public.get_user_household_id(auth.uid())));
CREATE POLICY "Update household transactions" ON public.transactions FOR UPDATE USING (bank_account_id IN (SELECT id FROM public.bank_accounts WHERE household_id = public.get_user_household_id(auth.uid())));
CREATE POLICY "Delete household transactions" ON public.transactions FOR DELETE USING (bank_account_id IN (SELECT id FROM public.bank_accounts WHERE household_id = public.get_user_household_id(auth.uid())));

-- ============================================
-- RLS POLICIES: categorization_rules
-- ============================================
CREATE POLICY "View household rules" ON public.categorization_rules FOR SELECT USING (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Create household rules" ON public.categorization_rules FOR INSERT WITH CHECK (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Update household rules" ON public.categorization_rules FOR UPDATE USING (household_id = public.get_user_household_id(auth.uid()));
CREATE POLICY "Delete household rules" ON public.categorization_rules FOR DELETE USING (household_id = public.get_user_household_id(auth.uid()));

-- ============================================
-- SEED: 15 default categories (global, no household)
-- ============================================
INSERT INTO public.categories (name, icon, color, is_default) VALUES
  ('Alimentation', 'shopping-cart', '160 84% 39%', true),
  ('Transport', 'car', '217 91% 60%', true),
  ('Logement', 'home', '38 92% 50%', true),
  ('Loisirs', 'gamepad-2', '280 65% 60%', true),
  ('Santé', 'heart-pulse', '0 72% 51%', true),
  ('Habillement', 'shirt', '200 70% 50%', true),
  ('Éducation', 'graduation-cap', '240 60% 55%', true),
  ('Restaurants', 'utensils', '25 85% 55%', true),
  ('Abonnements', 'repeat', '300 60% 50%', true),
  ('Assurances', 'shield', '180 50% 45%', true),
  ('Impôts & Taxes', 'receipt', '0 0% 45%', true),
  ('Épargne', 'piggy-bank', '160 60% 50%', true),
  ('Revenus', 'trending-up', '120 60% 40%', true),
  ('Remboursement', 'undo', '200 50% 55%', true),
  ('Autre', 'help-circle', '220 10% 50%', true);
