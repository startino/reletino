create type "public"."categories" as enum ('find-leads', 'find-competition');

alter table "public"."projects" add column "category" categories not null default 'find-leads'::categories;

alter table "public"."projects" add column "context" jsonb not null default '{}'::jsonb;


