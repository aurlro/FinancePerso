ALTER TABLE public.households ADD COLUMN currency text NOT NULL DEFAULT 'EUR';
ALTER TABLE public.households ADD COLUMN start_date date;
ALTER TABLE public.categories ADD COLUMN exclude_from_expenses boolean NOT NULL DEFAULT false;