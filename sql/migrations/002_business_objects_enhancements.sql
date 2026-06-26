begin;

-- Missing tables from Batch 2 spec

create table if not exists public.profiles (
  id uuid primary key default gen_random_uuid(),
  user_id text not null unique,
  display_name text,
  email text,
  avatar_url text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.delivery_tasks (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  delivery_project_id uuid references public.delivery_projects(id) on delete cascade,
  title text not null,
  description text,
  priority text not null default 'medium',
  status text not null default 'todo',
  due_date date,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.deliverables (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  delivery_project_id uuid references public.delivery_projects(id) on delete cascade,
  name text not null,
  description text,
  acceptance_criteria jsonb not null default '[]'::jsonb,
  status text not null default 'pending',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.customer_feedback (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  customer_name text,
  feedback_type text not null default 'general',
  content text,
  rating integer,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.knowledge_assets (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  title text not null,
  asset_type text,
  raw_text text,
  summary text,
  tags jsonb not null default '[]'::jsonb,
  embedding vector(1536),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Triggers for new tables
drop trigger if exists profiles_updated_at on public.profiles;
create trigger profiles_updated_at
before update on public.profiles
for each row execute function public.set_updated_at();

drop trigger if exists delivery_tasks_updated_at on public.delivery_tasks;
create trigger delivery_tasks_updated_at
before update on public.delivery_tasks
for each row execute function public.set_updated_at();

drop trigger if exists deliverables_updated_at on public.deliverables;
create trigger deliverables_updated_at
before update on public.deliverables
for each row execute function public.set_updated_at();

drop trigger if exists customer_feedback_updated_at on public.customer_feedback;
create trigger customer_feedback_updated_at
before update on public.customer_feedback
for each row execute function public.set_updated_at();

drop trigger if exists knowledge_assets_updated_at on public.knowledge_assets;
create trigger knowledge_assets_updated_at
before update on public.knowledge_assets
for each row execute function public.set_updated_at();

-- Indexes for new tables
create index if not exists profiles_user_id_idx on public.profiles(user_id);
create index if not exists delivery_tasks_delivery_project_id_idx on public.delivery_tasks(delivery_project_id);
create index if not exists delivery_tasks_user_id_idx on public.delivery_tasks(user_id);
create index if not exists deliverables_delivery_project_id_idx on public.deliverables(delivery_project_id);
create index if not exists deliverables_user_id_idx on public.deliverables(user_id);
create index if not exists customer_feedback_project_id_idx on public.customer_feedback(project_id);
create index if not exists customer_feedback_user_id_idx on public.customer_feedback(user_id);
create index if not exists knowledge_assets_user_id_idx on public.knowledge_assets(user_id);
create index if not exists knowledge_assets_project_id_idx on public.knowledge_assets(project_id);

-- Dashboard views
create or replace view public.project_revenue_summary as
select
  p.id as project_id,
  p.user_id,
  p.name as project_name,
  coalesce(sum(r.amount), 0) as total_revenue,
  coalesce(count(r.id), 0) as total_deals,
  coalesce(avg(r.amount), 0) as avg_deal_size
from public.business_projects p
left join public.revenue_records r on r.project_id = p.id
group by p.id, p.user_id, p.name;

create or replace view public.crm_pipeline_summary as
select
  d.project_id,
  d.user_id,
  d.stage,
  count(*) as deal_count,
  coalesce(sum(d.expected_value), 0) as total_expected_value,
  coalesce(avg(d.probability), 0) as avg_probability
from public.crm_deals d
group by d.project_id, d.user_id, d.stage;

create or replace view public.lead_followup_summary as
select
  l.project_id,
  l.user_id,
  l.status,
  count(*) as lead_count,
  max(l.updated_at) as last_activity
from public.leads l
group by l.project_id, l.user_id, l.status;

insert into public.schema_migrations(version)
values ('002_business_objects_enhancements')
on conflict (version) do nothing;

commit;
