
-- Household invitations table
CREATE TABLE public.household_invitations (
  id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
  household_id UUID NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
  invited_by UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
  invited_email TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'declined', 'expired')),
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (now() + interval '7 days')
);

ALTER TABLE public.household_invitations ENABLE ROW LEVEL SECURITY;

-- Owner can create invitations for their household
CREATE POLICY "Owner can create invitations"
ON public.household_invitations FOR INSERT
WITH CHECK (household_id = get_user_household_id(auth.uid()));

-- Owner can view invitations for their household
CREATE POLICY "Owner can view household invitations"
ON public.household_invitations FOR SELECT
USING (household_id = get_user_household_id(auth.uid()) OR invited_email = (SELECT email FROM auth.users WHERE id = auth.uid()));

-- Owner can delete invitations
CREATE POLICY "Owner can delete invitations"
ON public.household_invitations FOR DELETE
USING (household_id = get_user_household_id(auth.uid()));

-- Invited user can update status (accept/decline)
CREATE POLICY "Invited user can update invitation"
ON public.household_invitations FOR UPDATE
USING (invited_email = (SELECT email FROM auth.users WHERE id = auth.uid()));

-- Function to accept an invitation and join household
CREATE OR REPLACE FUNCTION public.accept_invitation(invitation_id UUID)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  inv RECORD;
  user_email TEXT;
BEGIN
  SELECT email INTO user_email FROM auth.users WHERE id = auth.uid();
  
  SELECT * INTO inv FROM public.household_invitations 
  WHERE id = invitation_id AND invited_email = user_email AND status = 'pending' AND expires_at > now();
  
  IF NOT FOUND THEN
    RAISE EXCEPTION 'Invitation not found or expired';
  END IF;
  
  -- Update user's profile to join the household
  UPDATE public.profiles SET household_id = inv.household_id WHERE id = auth.uid();
  
  -- Mark invitation as accepted
  UPDATE public.household_invitations SET status = 'accepted' WHERE id = invitation_id;
END;
$$;
