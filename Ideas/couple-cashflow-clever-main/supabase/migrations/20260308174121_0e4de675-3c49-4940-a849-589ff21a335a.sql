
-- 1. Create household_members table
CREATE TABLE public.household_members (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  household_id uuid NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
  user_id uuid REFERENCES public.profiles(id) ON DELETE SET NULL,
  display_name text NOT NULL,
  card_identifier text,
  is_active boolean NOT NULL DEFAULT false,
  created_at timestamp with time zone NOT NULL DEFAULT now()
);

-- 2. Enable RLS
ALTER TABLE public.household_members ENABLE ROW LEVEL SECURITY;

-- 3. RLS policies
CREATE POLICY "View household members" ON public.household_members
  FOR SELECT TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Create household members" ON public.household_members
  FOR INSERT TO authenticated
  WITH CHECK (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Update household members" ON public.household_members
  FOR UPDATE TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Delete household members" ON public.household_members
  FOR DELETE TO authenticated
  USING (household_id = get_user_household_id(auth.uid()));

-- 4. Migrate existing profiles into household_members
INSERT INTO public.household_members (household_id, user_id, display_name, card_identifier, is_active)
SELECT p.household_id, p.id, COALESCE(p.display_name, 'Membre'), p.card_identifier, true
FROM public.profiles p
WHERE p.household_id IS NOT NULL;

-- 5. Drop old FK on transactions.attributed_to, add new FK to household_members
ALTER TABLE public.transactions DROP CONSTRAINT IF EXISTS transactions_attributed_to_fkey;

-- Migrate attributed_to values from profile IDs to household_member IDs
UPDATE public.transactions t
SET attributed_to = hm.id
FROM public.household_members hm
WHERE t.attributed_to IS NOT NULL
  AND t.attributed_to = hm.user_id;

ALTER TABLE public.transactions
  ADD CONSTRAINT transactions_attributed_to_fkey
  FOREIGN KEY (attributed_to) REFERENCES public.household_members(id) ON DELETE SET NULL;

-- 6. Trigger: auto-create household_member when a profile is inserted
CREATE OR REPLACE FUNCTION public.sync_profile_to_household_member()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
BEGIN
  IF NEW.household_id IS NOT NULL THEN
    INSERT INTO public.household_members (household_id, user_id, display_name, card_identifier, is_active)
    VALUES (NEW.household_id, NEW.id, COALESCE(NEW.display_name, 'Membre'), NEW.card_identifier, true)
    ON CONFLICT DO NOTHING;
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER on_profile_created
  AFTER INSERT ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.sync_profile_to_household_member();

-- 7. Trigger: sync profile updates (display_name, card_identifier, household_id) to household_members
CREATE OR REPLACE FUNCTION public.sync_profile_update_to_household_member()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path TO 'public'
AS $$
BEGIN
  UPDATE public.household_members
  SET display_name = COALESCE(NEW.display_name, 'Membre'),
      card_identifier = NEW.card_identifier
  WHERE user_id = NEW.id;
  
  -- If household changed, update that too
  IF OLD.household_id IS DISTINCT FROM NEW.household_id AND NEW.household_id IS NOT NULL THEN
    UPDATE public.household_members
    SET household_id = NEW.household_id
    WHERE user_id = NEW.id;
  END IF;
  
  RETURN NEW;
END;
$$;

CREATE TRIGGER on_profile_updated
  AFTER UPDATE ON public.profiles
  FOR EACH ROW
  EXECUTE FUNCTION public.sync_profile_update_to_household_member();
