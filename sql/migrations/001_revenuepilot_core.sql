begin;

create extension if not exists pgcrypto;

create table if not exists public.schema_migrations (
  version text primary key,
  applied_at timestamptz not null default now()
);

create table if not exists public.business_projects (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  name text not null,
  description text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.skill_runs (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete set null,
  skill_name text not null,
  skill_version text not null default 'v1',
  status text not null default 'queued',
  input_payload jsonb not null default '{}'::jsonb,
  output_payload jsonb not null default '{}'::jsonb,
  related_entity_type text,
  related_entity_id uuid,
  error_message text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.ai_generations (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete set null,
  skill_run_id uuid references public.skill_runs(id) on delete set null,
  generation_type text not null,
  title text,
  content_json jsonb not null default '{}'::jsonb,
  related_entity_type text,
  related_entity_id uuid,
  created_at timestamptz not null default now()
);

create table if not exists public.workflow_runs (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete set null,
  workflow_name text not null,
  workflow_version text not null default 'v1',
  status text not null default 'queued',
  input_payload jsonb not null default '{}'::jsonb,
  output_payload jsonb not null default '{}'::jsonb,
  skill_run_ids jsonb not null default '[]'::jsonb,
  created_entities jsonb not null default '[]'::jsonb,
  error_message text,
  started_at timestamptz,
  finished_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.founder_profiles (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  skills jsonb not null default '[]'::jsonb,
  work_experience jsonb not null default '[]'::jsonb,
  domain_expertise jsonb not null default '[]'::jsonb,
  technical_ability jsonb not null default '{}'::jsonb,
  sales_experience jsonb not null default '{}'::jsonb,
  existing_content jsonb not null default '[]'::jsonb,
  audience_assets jsonb not null default '{}'::jsonb,
  personal_network jsonb not null default '{}'::jsonb,
  time_available_per_week integer,
  monthly_income_goal numeric,
  preferred_customer_type text,
  constraints jsonb not null default '[]'::jsonb,
  values_or_mission text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.business_ideas (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  title text not null,
  description text,
  target_customer text,
  pain_point text,
  possible_offer text,
  scores jsonb not null default '{}'::jsonb,
  risks jsonb not null default '[]'::jsonb,
  validation_steps jsonb not null default '[]'::jsonb,
  status text not null default 'generated',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.market_hypotheses (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  business_idea_id uuid references public.business_ideas(id) on delete set null,
  selected_niche text,
  suspected_pain text,
  proposed_offer text,
  validation_plan jsonb not null default '{}'::jsonb,
  status text not null default 'draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.customer_personas (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  business_idea_id uuid references public.business_ideas(id) on delete set null,
  name text,
  role text,
  business_type text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.pain_interviews (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  customer_persona_id uuid references public.customer_personas(id) on delete set null,
  interview_goal text,
  questions jsonb not null default '[]'::jsonb,
  scoring_rubric jsonb not null default '{}'::jsonb,
  summary jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.offers (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  business_idea_id uuid references public.business_ideas(id) on delete set null,
  offer_name text not null,
  one_line_promise text,
  target_customer text,
  pain text,
  desired_result text,
  deliverables jsonb not null default '[]'::jsonb,
  timeline text,
  pricing jsonb not null default '{}'::jsonb,
  guarantee text,
  scope_boundaries jsonb not null default '[]'::jsonb,
  client_requirements jsonb not null default '[]'::jsonb,
  upsell_path jsonb not null default '[]'::jsonb,
  retainer_path text,
  status text not null default 'draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.landing_pages (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  offer_id uuid references public.offers(id) on delete set null,
  title text,
  payload jsonb not null default '{}'::jsonb,
  published boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.outreach_assets (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  offer_id uuid references public.offers(id) on delete set null,
  channel text,
  payload jsonb not null default '{}'::jsonb,
  human_approval_required boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.leads (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  name text,
  company text,
  email text,
  source text,
  status text not null default 'new',
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.crm_deals (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  lead_id uuid references public.leads(id) on delete set null,
  offer_id uuid references public.offers(id) on delete set null,
  stage text not null default 'new',
  expected_value numeric,
  probability integer,
  expected_close_date date,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.proposals (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  deal_id uuid references public.crm_deals(id) on delete set null,
  title text,
  payload jsonb not null default '{}'::jsonb,
  status text not null default 'draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.delivery_projects (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  deal_id uuid references public.crm_deals(id) on delete set null,
  proposal_id uuid references public.proposals(id) on delete set null,
  title text,
  client_name text,
  payload jsonb not null default '{}'::jsonb,
  status text not null default 'todo',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.revenue_records (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  deal_id uuid references public.crm_deals(id) on delete set null,
  offer_id uuid references public.offers(id) on delete set null,
  customer_name text,
  amount numeric not null default 0,
  currency text not null default 'USD',
  received_at date,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.retention_plans (
  id uuid primary key default gen_random_uuid(),
  user_id text not null,
  project_id uuid references public.business_projects(id) on delete cascade,
  customer_name text,
  payload jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists business_projects_updated_at on public.business_projects;
create trigger business_projects_updated_at
before update on public.business_projects
for each row execute function public.set_updated_at();

drop trigger if exists skill_runs_updated_at on public.skill_runs;
create trigger skill_runs_updated_at
before update on public.skill_runs
for each row execute function public.set_updated_at();

drop trigger if exists workflow_runs_updated_at on public.workflow_runs;
create trigger workflow_runs_updated_at
before update on public.workflow_runs
for each row execute function public.set_updated_at();

drop trigger if exists founder_profiles_updated_at on public.founder_profiles;
create trigger founder_profiles_updated_at
before update on public.founder_profiles
for each row execute function public.set_updated_at();

drop trigger if exists business_ideas_updated_at on public.business_ideas;
create trigger business_ideas_updated_at
before update on public.business_ideas
for each row execute function public.set_updated_at();

drop trigger if exists market_hypotheses_updated_at on public.market_hypotheses;
create trigger market_hypotheses_updated_at
before update on public.market_hypotheses
for each row execute function public.set_updated_at();

drop trigger if exists customer_personas_updated_at on public.customer_personas;
create trigger customer_personas_updated_at
before update on public.customer_personas
for each row execute function public.set_updated_at();

drop trigger if exists pain_interviews_updated_at on public.pain_interviews;
create trigger pain_interviews_updated_at
before update on public.pain_interviews
for each row execute function public.set_updated_at();

drop trigger if exists offers_updated_at on public.offers;
create trigger offers_updated_at
before update on public.offers
for each row execute function public.set_updated_at();

drop trigger if exists landing_pages_updated_at on public.landing_pages;
create trigger landing_pages_updated_at
before update on public.landing_pages
for each row execute function public.set_updated_at();

drop trigger if exists outreach_assets_updated_at on public.outreach_assets;
create trigger outreach_assets_updated_at
before update on public.outreach_assets
for each row execute function public.set_updated_at();

drop trigger if exists leads_updated_at on public.leads;
create trigger leads_updated_at
before update on public.leads
for each row execute function public.set_updated_at();

drop trigger if exists crm_deals_updated_at on public.crm_deals;
create trigger crm_deals_updated_at
before update on public.crm_deals
for each row execute function public.set_updated_at();

drop trigger if exists proposals_updated_at on public.proposals;
create trigger proposals_updated_at
before update on public.proposals
for each row execute function public.set_updated_at();

drop trigger if exists delivery_projects_updated_at on public.delivery_projects;
create trigger delivery_projects_updated_at
before update on public.delivery_projects
for each row execute function public.set_updated_at();

drop trigger if exists revenue_records_updated_at on public.revenue_records;
create trigger revenue_records_updated_at
before update on public.revenue_records
for each row execute function public.set_updated_at();

drop trigger if exists retention_plans_updated_at on public.retention_plans;
create trigger retention_plans_updated_at
before update on public.retention_plans
for each row execute function public.set_updated_at();

create index if not exists business_projects_user_id_idx on public.business_projects(user_id);
create index if not exists skill_runs_user_id_idx on public.skill_runs(user_id);
create index if not exists skill_runs_project_id_idx on public.skill_runs(project_id);
create index if not exists skill_runs_skill_name_idx on public.skill_runs(skill_name);
create index if not exists skill_runs_status_idx on public.skill_runs(status);
create index if not exists ai_generations_user_id_idx on public.ai_generations(user_id);
create index if not exists ai_generations_project_id_idx on public.ai_generations(project_id);
create index if not exists workflow_runs_user_id_idx on public.workflow_runs(user_id);
create index if not exists workflow_runs_project_id_idx on public.workflow_runs(project_id);
create index if not exists workflow_runs_workflow_name_idx on public.workflow_runs(workflow_name);
create index if not exists workflow_runs_status_idx on public.workflow_runs(status);

create index if not exists founder_profiles_user_id_idx on public.founder_profiles(user_id);
create index if not exists business_ideas_project_id_idx on public.business_ideas(project_id);
create index if not exists market_hypotheses_project_id_idx on public.market_hypotheses(project_id);
create index if not exists customer_personas_project_id_idx on public.customer_personas(project_id);
create index if not exists pain_interviews_project_id_idx on public.pain_interviews(project_id);
create index if not exists offers_project_id_idx on public.offers(project_id);
create index if not exists landing_pages_offer_id_idx on public.landing_pages(offer_id);
create index if not exists outreach_assets_offer_id_idx on public.outreach_assets(offer_id);
create index if not exists leads_project_id_idx on public.leads(project_id);
create index if not exists crm_deals_project_id_idx on public.crm_deals(project_id);
create index if not exists proposals_deal_id_idx on public.proposals(deal_id);
create index if not exists delivery_projects_deal_id_idx on public.delivery_projects(deal_id);
create index if not exists revenue_records_project_id_idx on public.revenue_records(project_id);
create index if not exists retention_plans_project_id_idx on public.retention_plans(project_id);

insert into public.schema_migrations(version)
values ('001_revenuepilot_core')
on conflict (version) do nothing;

commit;
