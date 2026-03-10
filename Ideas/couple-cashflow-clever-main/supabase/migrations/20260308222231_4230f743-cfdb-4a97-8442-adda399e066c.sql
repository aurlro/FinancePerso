
-- 1. Table notifications
CREATE TABLE public.notifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  household_id uuid NOT NULL REFERENCES public.households(id) ON DELETE CASCADE,
  user_id uuid NOT NULL,
  type text NOT NULL,
  title text NOT NULL,
  body text,
  link text,
  is_read boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own notifications"
  ON public.notifications FOR SELECT TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can update own notifications"
  ON public.notifications FOR UPDATE TO authenticated
  USING (user_id = auth.uid());

CREATE POLICY "Users can insert notifications for household"
  ON public.notifications FOR INSERT TO authenticated
  WITH CHECK (household_id = get_user_household_id(auth.uid()));

CREATE POLICY "Users can delete own notifications"
  ON public.notifications FOR DELETE TO authenticated
  USING (user_id = auth.uid());

-- Enable realtime
ALTER PUBLICATION supabase_realtime ADD TABLE public.notifications;

-- 2. Table transaction_comments
CREATE TABLE public.transaction_comments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  transaction_id uuid NOT NULL REFERENCES public.transactions(id) ON DELETE CASCADE,
  user_id uuid NOT NULL,
  display_name text NOT NULL,
  content text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.transaction_comments ENABLE ROW LEVEL SECURITY;

CREATE POLICY "View comments for household transactions"
  ON public.transaction_comments FOR SELECT TO authenticated
  USING (transaction_id IN (
    SELECT t.id FROM public.transactions t
    JOIN public.bank_accounts ba ON t.bank_account_id = ba.id
    WHERE ba.household_id = get_user_household_id(auth.uid())
  ));

CREATE POLICY "Insert comments for household transactions"
  ON public.transaction_comments FOR INSERT TO authenticated
  WITH CHECK (
    user_id = auth.uid() AND
    transaction_id IN (
      SELECT t.id FROM public.transactions t
      JOIN public.bank_accounts ba ON t.bank_account_id = ba.id
      WHERE ba.household_id = get_user_household_id(auth.uid())
    )
  );

CREATE POLICY "Delete own comments"
  ON public.transaction_comments FOR DELETE TO authenticated
  USING (user_id = auth.uid());

-- 3. Colonne validation_status sur transactions
ALTER TABLE public.transactions ADD COLUMN validation_status text DEFAULT NULL;
ALTER TABLE public.transactions ADD COLUMN last_modified_by uuid DEFAULT NULL;
