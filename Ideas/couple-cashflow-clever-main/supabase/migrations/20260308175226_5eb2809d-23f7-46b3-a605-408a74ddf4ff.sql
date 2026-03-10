
-- Table for savings goals
CREATE TABLE public.savings_goals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  household_id uuid NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
  name text NOT NULL,
  target_amount numeric NOT NULL DEFAULT 0,
  current_amount numeric NOT NULL DEFAULT 0,
  deadline date,
  icon text,
  color text DEFAULT '#3b82f6',
  is_completed boolean NOT NULL DEFAULT false,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  updated_at timestamp with time zone NOT NULL DEFAULT now()
);

ALTER TABLE public.savings_goals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "View household goals" ON public.savings_goals
  FOR SELECT TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Create household goals" ON public.savings_goals
  FOR INSERT TO authenticated
  WITH CHECK (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Update household goals" ON public.savings_goals
  FOR UPDATE TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Delete household goals" ON public.savings_goals
  FOR DELETE TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));
