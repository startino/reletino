create table "public"."environments" (
    "id" uuid not null default gen_random_uuid(),
    "created_at" timestamp with time zone not null default now(),
    "name" text not null,
    "slug" text not null,
    "critino_key" text
);


create table "public"."environments_profiles" (
    "created_at" timestamp with time zone not null default now(),
    "environment_id" uuid not null default gen_random_uuid(),
    "profile_id" uuid not null default gen_random_uuid()
);


alter table "public"."environments_profiles" enable row level security;

create table "public"."projects" (
    "created_at" timestamp with time zone not null default now(),
    "profile_id" uuid not null,
    "title" text not null default 'Untitled Project'::text,
    "prompt" text not null default 'No prompt given yet.'::text,
    "running" boolean not null default false,
    "id" uuid not null default gen_random_uuid(),
    "subreddits" text[] not null default '{saas}'::text[],
    "use_case" text,
    "dm_style_prompt" text not null default ''::text,
    "comment_style_prompt" text not null default ''::text
);


create table "public"."submissions" (
    "created_at" timestamp with time zone not null default now(),
    "author" text not null,
    "submission_created_utc" timestamp with time zone not null,
    "reddit_id" text not null,
    "subreddit" text not null,
    "title" text not null,
    "selftext" text not null default ''::text,
    "url" text not null,
    "is_relevant" boolean not null,
    "reasoning" text not null,
    "id" uuid not null default gen_random_uuid(),
    "done" boolean not null default false,
    "project_id" uuid not null default gen_random_uuid(),
    "profile_id" uuid not null
);


create table "public"."usage" (
    "profile_id" uuid not null,
    "credits" integer not null default 1000
);


alter table "public"."usage" enable row level security;

CREATE UNIQUE INDEX credits_pkey ON public.usage USING btree (profile_id);

CREATE UNIQUE INDEX environments_name_key ON public.environments USING btree (name);

CREATE UNIQUE INDEX environments_pkey ON public.environments USING btree (id);

CREATE UNIQUE INDEX environments_profiles_pkey ON public.environments_profiles USING btree (environment_id, profile_id);

CREATE UNIQUE INDEX environments_slug_key ON public.environments USING btree (slug);

CREATE UNIQUE INDEX projects_pkey ON public.projects USING btree (id);

CREATE UNIQUE INDEX submissions_pkey ON public.submissions USING btree (id);

alter table "public"."environments" add constraint "environments_pkey" PRIMARY KEY using index "environments_pkey";

alter table "public"."environments_profiles" add constraint "environments_profiles_pkey" PRIMARY KEY using index "environments_profiles_pkey";

alter table "public"."projects" add constraint "projects_pkey" PRIMARY KEY using index "projects_pkey";

alter table "public"."submissions" add constraint "submissions_pkey" PRIMARY KEY using index "submissions_pkey";

alter table "public"."usage" add constraint "credits_pkey" PRIMARY KEY using index "credits_pkey";

alter table "public"."environments" add constraint "environments_name_key" UNIQUE using index "environments_name_key";

alter table "public"."environments" add constraint "environments_slug_key" UNIQUE using index "environments_slug_key";

alter table "public"."environments_profiles" add constraint "environments_profiles_environment_id_fkey" FOREIGN KEY (environment_id) REFERENCES environments(id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."environments_profiles" validate constraint "environments_profiles_environment_id_fkey";

alter table "public"."environments_profiles" add constraint "environments_profiles_profile_id_fkey" FOREIGN KEY (profile_id) REFERENCES profiles(id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."environments_profiles" validate constraint "environments_profiles_profile_id_fkey";

alter table "public"."projects" add constraint "projects_profile_id_fkey" FOREIGN KEY (profile_id) REFERENCES profiles(id) not valid;

alter table "public"."projects" validate constraint "projects_profile_id_fkey";

alter table "public"."submissions" add constraint "submissions_profile_id_fkey" FOREIGN KEY (profile_id) REFERENCES profiles(id) not valid;

alter table "public"."submissions" validate constraint "submissions_profile_id_fkey";

alter table "public"."submissions" add constraint "submissions_project_id_fkey" FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE not valid;

alter table "public"."submissions" validate constraint "submissions_project_id_fkey";

alter table "public"."usage" add constraint "credits_profile_id_fkey" FOREIGN KEY (profile_id) REFERENCES profiles(id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."usage" validate constraint "credits_profile_id_fkey";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.handle_new_user()
 RETURNS trigger
 LANGUAGE plpgsql
 SECURITY DEFINER
 SET search_path TO ''
AS $function$
begin
  -- Insert into public.profiles
  insert into public.profiles (id, full_name)
  values (new.id, new.raw_user_meta_data ->> 'full_name');

  -- Insert into public.usage with default credits value (e.g., 0)
  insert into public.usage (profile_id)
  values (new.id);  -- Assuming you want to start with 0 credits

  return new;
end;
$function$
;

grant delete on table "public"."environments" to "anon";

grant insert on table "public"."environments" to "anon";

grant references on table "public"."environments" to "anon";

grant select on table "public"."environments" to "anon";

grant trigger on table "public"."environments" to "anon";

grant truncate on table "public"."environments" to "anon";

grant update on table "public"."environments" to "anon";

grant delete on table "public"."environments" to "authenticated";

grant insert on table "public"."environments" to "authenticated";

grant references on table "public"."environments" to "authenticated";

grant select on table "public"."environments" to "authenticated";

grant trigger on table "public"."environments" to "authenticated";

grant truncate on table "public"."environments" to "authenticated";

grant update on table "public"."environments" to "authenticated";

grant delete on table "public"."environments" to "service_role";

grant insert on table "public"."environments" to "service_role";

grant references on table "public"."environments" to "service_role";

grant select on table "public"."environments" to "service_role";

grant trigger on table "public"."environments" to "service_role";

grant truncate on table "public"."environments" to "service_role";

grant update on table "public"."environments" to "service_role";

grant delete on table "public"."environments_profiles" to "anon";

grant insert on table "public"."environments_profiles" to "anon";

grant references on table "public"."environments_profiles" to "anon";

grant select on table "public"."environments_profiles" to "anon";

grant trigger on table "public"."environments_profiles" to "anon";

grant truncate on table "public"."environments_profiles" to "anon";

grant update on table "public"."environments_profiles" to "anon";

grant delete on table "public"."environments_profiles" to "authenticated";

grant insert on table "public"."environments_profiles" to "authenticated";

grant references on table "public"."environments_profiles" to "authenticated";

grant select on table "public"."environments_profiles" to "authenticated";

grant trigger on table "public"."environments_profiles" to "authenticated";

grant truncate on table "public"."environments_profiles" to "authenticated";

grant update on table "public"."environments_profiles" to "authenticated";

grant delete on table "public"."environments_profiles" to "service_role";

grant insert on table "public"."environments_profiles" to "service_role";

grant references on table "public"."environments_profiles" to "service_role";

grant select on table "public"."environments_profiles" to "service_role";

grant trigger on table "public"."environments_profiles" to "service_role";

grant truncate on table "public"."environments_profiles" to "service_role";

grant update on table "public"."environments_profiles" to "service_role";

grant delete on table "public"."projects" to "anon";

grant insert on table "public"."projects" to "anon";

grant references on table "public"."projects" to "anon";

grant select on table "public"."projects" to "anon";

grant trigger on table "public"."projects" to "anon";

grant truncate on table "public"."projects" to "anon";

grant update on table "public"."projects" to "anon";

grant delete on table "public"."projects" to "authenticated";

grant insert on table "public"."projects" to "authenticated";

grant references on table "public"."projects" to "authenticated";

grant select on table "public"."projects" to "authenticated";

grant trigger on table "public"."projects" to "authenticated";

grant truncate on table "public"."projects" to "authenticated";

grant update on table "public"."projects" to "authenticated";

grant delete on table "public"."projects" to "service_role";

grant insert on table "public"."projects" to "service_role";

grant references on table "public"."projects" to "service_role";

grant select on table "public"."projects" to "service_role";

grant trigger on table "public"."projects" to "service_role";

grant truncate on table "public"."projects" to "service_role";

grant update on table "public"."projects" to "service_role";

grant delete on table "public"."submissions" to "anon";

grant insert on table "public"."submissions" to "anon";

grant references on table "public"."submissions" to "anon";

grant select on table "public"."submissions" to "anon";

grant trigger on table "public"."submissions" to "anon";

grant truncate on table "public"."submissions" to "anon";

grant update on table "public"."submissions" to "anon";

grant delete on table "public"."submissions" to "authenticated";

grant insert on table "public"."submissions" to "authenticated";

grant references on table "public"."submissions" to "authenticated";

grant select on table "public"."submissions" to "authenticated";

grant trigger on table "public"."submissions" to "authenticated";

grant truncate on table "public"."submissions" to "authenticated";

grant update on table "public"."submissions" to "authenticated";

grant delete on table "public"."submissions" to "service_role";

grant insert on table "public"."submissions" to "service_role";

grant references on table "public"."submissions" to "service_role";

grant select on table "public"."submissions" to "service_role";

grant trigger on table "public"."submissions" to "service_role";

grant truncate on table "public"."submissions" to "service_role";

grant update on table "public"."submissions" to "service_role";

grant delete on table "public"."usage" to "anon";

grant insert on table "public"."usage" to "anon";

grant references on table "public"."usage" to "anon";

grant select on table "public"."usage" to "anon";

grant trigger on table "public"."usage" to "anon";

grant truncate on table "public"."usage" to "anon";

grant update on table "public"."usage" to "anon";

grant delete on table "public"."usage" to "authenticated";

grant insert on table "public"."usage" to "authenticated";

grant references on table "public"."usage" to "authenticated";

grant select on table "public"."usage" to "authenticated";

grant trigger on table "public"."usage" to "authenticated";

grant truncate on table "public"."usage" to "authenticated";

grant update on table "public"."usage" to "authenticated";

grant delete on table "public"."usage" to "service_role";

grant insert on table "public"."usage" to "service_role";

grant references on table "public"."usage" to "service_role";

grant select on table "public"."usage" to "service_role";

grant trigger on table "public"."usage" to "service_role";

grant truncate on table "public"."usage" to "service_role";

grant update on table "public"."usage" to "service_role";

create policy "Authenticated users can read environments"
on "public"."environments"
as permissive
for select
to authenticated
using (true);


create policy "Authenticated users can read environments_profiles"
on "public"."environments_profiles"
as permissive
for select
to authenticated
using (true);


create policy "Enable insert for users based on user_id"
on "public"."projects"
as permissive
for insert
to public
with check ((( SELECT auth.uid() AS uid) = profile_id));


create policy "Enable read access for all users"
on "public"."projects"
as permissive
for select
to public
using (true);


create policy "Enable users to view their own data only"
on "public"."projects"
as permissive
for select
to public
using ((( SELECT auth.uid() AS uid) = profile_id));


create policy "read_credits"
on "public"."usage"
as permissive
for select
to authenticated
using ((profile_id = ( SELECT auth.uid() AS uid)));



