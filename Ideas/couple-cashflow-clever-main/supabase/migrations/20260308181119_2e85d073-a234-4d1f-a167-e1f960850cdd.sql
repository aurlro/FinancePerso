
-- 1. CRITICAL: Create security definer function to get immutable profile fields
CREATE OR REPLACE FUNCTION public.get_profile_immutable_fields(uid uuid)
RETURNS TABLE(household_id uuid, role text)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = public AS $$
  SELECT p.household_id, p.role FROM profiles p WHERE p.id = uid LIMIT 1;
$$;

-- 2. CRITICAL: Drop old permissive UPDATE policy on profiles
DROP POLICY IF EXISTS "Users can update own profile" ON profiles;

-- 3. CRITICAL: Create restrictive UPDATE policy that blocks household_id and role changes
CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE TO authenticated
  USING (id = auth.uid())
  WITH CHECK (
    id = auth.uid()
    AND household_id IS NOT DISTINCT FROM (SELECT f.household_id FROM public.get_profile_immutable_fields(auth.uid()) f)
    AND role = (SELECT f.role FROM public.get_profile_immutable_fields(auth.uid()) f)
  );
