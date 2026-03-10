
-- Add attributed_to column on transactions (who made the transaction)
ALTER TABLE public.transactions ADD COLUMN attributed_to uuid REFERENCES public.profiles(id);

-- Add contribution_ratio on households (partner A's share, e.g. 0.5 = 50/50)
ALTER TABLE public.households ADD COLUMN contribution_ratio numeric NOT NULL DEFAULT 0.5;

-- Add card_identifier on profiles (pattern to match in transaction labels)
ALTER TABLE public.profiles ADD COLUMN card_identifier text;
