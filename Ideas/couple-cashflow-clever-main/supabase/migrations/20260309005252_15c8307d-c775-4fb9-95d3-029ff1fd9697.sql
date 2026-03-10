-- Create a default attribution rule for joint account transactions to the "Couple" member
-- This rule will have low priority to allow specific rules to override it

DO $$
DECLARE 
  household RECORD;
  couple_member_id UUID;
  joint_account_id UUID;
BEGIN
  -- For each household that exists
  FOR household IN SELECT id FROM public.households LOOP
    -- Find the "Couple" member
    SELECT id INTO couple_member_id 
    FROM public.household_members 
    WHERE household_id = household.id AND is_couple = true
    LIMIT 1;
    
    -- Find a joint account for this household
    SELECT id INTO joint_account_id
    FROM public.bank_accounts 
    WHERE household_id = household.id AND account_type = 'joint'
    LIMIT 1;
    
    -- If both couple member and joint account exist, create the rule
    IF couple_member_id IS NOT NULL AND joint_account_id IS NOT NULL THEN
      INSERT INTO public.attribution_rules (
        household_id,
        name,
        regex_pattern,
        member_id,
        priority,
        is_active
      ) VALUES (
        household.id,
        'Attribution automatique au Couple (compte joint)',
        '.*', -- Match all transactions (low priority means this is a fallback)
        couple_member_id,
        -100, -- Very low priority so specific rules take precedence
        true
      )
      ON CONFLICT DO NOTHING; -- Don't create duplicates if rule already exists
    END IF;
  END LOOP;
  
  -- Also update existing unattributed joint account transactions to the couple
  FOR household IN SELECT id FROM public.households LOOP
    -- Find the "Couple" member
    SELECT id INTO couple_member_id 
    FROM public.household_members 
    WHERE household_id = household.id AND is_couple = true
    LIMIT 1;
    
    IF couple_member_id IS NOT NULL THEN
      -- Update unattributed transactions on joint accounts
      UPDATE public.transactions
      SET attributed_to = couple_member_id
      WHERE attributed_to IS NULL 
      AND bank_account_id IN (
        SELECT id FROM public.bank_accounts 
        WHERE household_id = household.id 
        AND account_type = 'joint'
      );
    END IF;
  END LOOP;
END $$;