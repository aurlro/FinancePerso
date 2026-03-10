
-- Table attribution_rules (mirror of categorization_rules but maps to member_id)
CREATE TABLE public.attribution_rules (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  household_id uuid NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
  member_id uuid NOT NULL REFERENCES public.household_members(id) ON DELETE CASCADE,
  name text NOT NULL,
  regex_pattern text NOT NULL,
  priority integer NOT NULL DEFAULT 0,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.attribution_rules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "View household attribution rules" ON public.attribution_rules
  FOR SELECT TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Create household attribution rules" ON public.attribution_rules
  FOR INSERT TO authenticated
  WITH CHECK (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Update household attribution rules" ON public.attribution_rules
  FOR UPDATE TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Delete household attribution rules" ON public.attribution_rules
  FOR DELETE TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));
