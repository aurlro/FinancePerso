
CREATE TABLE public.category_budgets (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  household_id uuid NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
  category_id uuid NOT NULL REFERENCES public.categories(id) ON DELETE CASCADE,
  monthly_amount numeric NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (household_id, category_id)
);

ALTER TABLE public.category_budgets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "View household budgets" ON public.category_budgets FOR SELECT TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Create household budgets" ON public.category_budgets FOR INSERT TO authenticated
  WITH CHECK (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Update household budgets" ON public.category_budgets FOR UPDATE TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Delete household budgets" ON public.category_budgets FOR DELETE TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));
