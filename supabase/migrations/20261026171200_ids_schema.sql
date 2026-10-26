-- PREPARED ONLY. Do not apply without verified exact project identity and explicit migration approval.
-- Authorized pilot: kc2-integrated-data-system; Tokyo ap-northeast-1. No NGO data is seeded.
BEGIN;
SET LOCAL lock_timeout = '5s';
SET LOCAL statement_timeout = '60s';
CREATE SCHEMA gk_private;
REVOKE ALL ON SCHEMA gk_private FROM PUBLIC, anon;
CREATE TABLE "public"."reference_values" (
  "vocabulary" text NOT NULL,
  "code" text NOT NULL,
  "label" text NOT NULL,
  "active" boolean DEFAULT false NOT NULL,
  "sort_order" integer,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  "permissions" jsonb DEFAULT '{}'::jsonb NOT NULL,
  "approval_reference" text,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  CONSTRAINT "pk_reference_values" PRIMARY KEY ("vocabulary", "code"),
  CONSTRAINT "ck_reference_values_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_reference_values_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_reference_values_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL)),
  CONSTRAINT "ck_reference_values_3" CHECK (btrim(vocabulary) <> '' AND btrim(code) <> ''),
  CONSTRAINT "ck_reference_values_4" CHECK (jsonb_typeof(permissions) = 'object'),
  CONSTRAINT "ck_reference_values_5" CHECK (vocabulary = 'access_role' OR permissions = '{}'::jsonb),
  CONSTRAINT "ck_reference_values_6" CHECK (review_state <> 'accepted' OR vocabulary <> 'access_role' OR approval_reference IS NOT NULL)
);
REVOKE ALL ON TABLE "public"."reference_values" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."reference_values" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "public"."children" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "display_name" text,
  "current_program_code" text,
  "admitted_program_code" text,
  "child_status_code" text,
  "program_vocabulary" text GENERATED ALWAYS AS ('program'::text) STORED NOT NULL,
  "status_vocabulary" text GENERATED ALWAYS AS ('child_status'::text) STORED NOT NULL,
  "joining_date" date,
  "dropout_date" date,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  "child_business_id" text COLLATE "C" NOT NULL,
  CONSTRAINT "pk_children" PRIMARY KEY ("id"),
  CONSTRAINT "uq_children_0" UNIQUE ("child_business_id"),
  CONSTRAINT "ck_children_0" CHECK (btrim("child_business_id") <> '' AND "child_business_id" = btrim("child_business_id")),
  CONSTRAINT "ck_children_1" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_children_2" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_children_3" CHECK ((archived_at IS NULL) = (archived_by IS NULL))
);
REVOKE ALL ON TABLE "public"."children" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."children" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."child_private_profiles" (
  "child_id" uuid NOT NULL,
  "birth_date" date,
  "gender_reported" text,
  "child_national_id" text,
  "blood_group_reported" text,
  "contact_address" text,
  "sibling_count_reported" text,
  "diagnosis_1" text,
  "diagnosis_2" text,
  "udid_number" text,
  "udid_disability_reported" text,
  "udid_validity_reported" text,
  "udid_percentage_reported" text,
  "insurance_number" text,
  "assessment_date" date,
  "assessment_age_reported" text,
  "family_income_reported" text,
  "economic_category_reported" text,
  "assessment_fee" numeric,
  "monthly_fee" numeric,
  "monthly_fee_remarks" text,
  "concession_reported" text,
  "social_category_reported" text,
  "religion_reported" text,
  "consent_reported" text,
  "dropout_reason_reported" text,
  "transition_date" date,
  "comments" text,
  "severity_reported" text,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_child_private_profiles" PRIMARY KEY ("child_id"),
  CONSTRAINT "ck_child_private_profiles_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_child_private_profiles_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_child_private_profiles_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL))
);
REVOKE ALL ON TABLE "gk_private"."child_private_profiles" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."child_private_profiles" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."caregivers" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "display_name" text,
  "birth_date" date,
  "contact_phone" text,
  "contact_email" text,
  "national_id" text,
  "employment_reported" text,
  "education_reported" text,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  "caregiver_business_id" text COLLATE "C" NOT NULL,
  CONSTRAINT "pk_caregivers" PRIMARY KEY ("id"),
  CONSTRAINT "uq_caregivers_0" UNIQUE ("caregiver_business_id"),
  CONSTRAINT "ck_caregivers_0" CHECK (btrim("caregiver_business_id") <> '' AND "caregiver_business_id" = btrim("caregiver_business_id")),
  CONSTRAINT "ck_caregivers_1" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_caregivers_2" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_caregivers_3" CHECK ((archived_at IS NULL) = (archived_by IS NULL))
);
REVOKE ALL ON TABLE "gk_private"."caregivers" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."caregivers" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "public"."child_caregivers" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "child_id" uuid NOT NULL,
  "caregiver_id" uuid NOT NULL,
  "role_code" text,
  "role_vocabulary" text GENERATED ALWAYS AS ('caregiver_role'::text) STORED NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_child_caregivers" PRIMARY KEY ("id"),
  CONSTRAINT "uq_child_caregivers_0" UNIQUE ("id", "child_id"),
  CONSTRAINT "uq_child_caregivers_1" UNIQUE ("child_id", "caregiver_id"),
  CONSTRAINT "ck_child_caregivers_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_child_caregivers_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_child_caregivers_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL))
);
REVOKE ALL ON TABLE "public"."child_caregivers" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."child_caregivers" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "public"."program_changes" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "child_id" uuid NOT NULL,
  "program_code" text,
  "program_vocabulary" text GENERATED ALWAYS AS ('program'::text) STORED NOT NULL,
  "promotion_date" date,
  "source_slot" integer,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_program_changes" PRIMARY KEY ("id"),
  CONSTRAINT "ck_program_changes_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_program_changes_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_program_changes_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL)),
  CONSTRAINT "ck_program_changes_3" CHECK (source_slot IS NULL OR source_slot > 0)
);
REVOKE ALL ON TABLE "public"."program_changes" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."program_changes" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "public"."questionnaire_responses" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "child_caregiver_id" uuid NOT NULL,
  "definition_key" text NOT NULL,
  "definition_vocabulary" text GENERATED ALWAYS AS ('questionnaire_definition'::text) STORED NOT NULL,
  "assessment_date" date,
  "program_code" text,
  "program_vocabulary" text GENERATED ALWAYS AS ('program'::text) STORED NOT NULL,
  "centre_code" text,
  "centre_vocabulary" text GENERATED ALWAYS AS ('centre'::text) STORED NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_questionnaire_responses" PRIMARY KEY ("id"),
  CONSTRAINT "uq_questionnaire_responses_0" UNIQUE ("id", "definition_key"),
  CONSTRAINT "ck_questionnaire_responses_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_questionnaire_responses_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_questionnaire_responses_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL))
);
REVOKE ALL ON TABLE "public"."questionnaire_responses" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."questionnaire_responses" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "public"."questionnaire_items" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "definition_key" text NOT NULL,
  "definition_vocabulary" text GENERATED ALWAYS AS ('questionnaire_definition'::text) STORED NOT NULL,
  "item_key" text NOT NULL,
  "prompt" text NOT NULL,
  "section_label" text,
  "value_kind" text NOT NULL,
  "ordinal" integer NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_questionnaire_items" PRIMARY KEY ("id"),
  CONSTRAINT "uq_questionnaire_items_0" UNIQUE ("definition_key", "item_key"),
  CONSTRAINT "uq_questionnaire_items_1" UNIQUE ("definition_key", "ordinal"),
  CONSTRAINT "uq_questionnaire_items_2" UNIQUE ("id", "definition_key"),
  CONSTRAINT "ck_questionnaire_items_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_questionnaire_items_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_questionnaire_items_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL)),
  CONSTRAINT "ck_questionnaire_items_3" CHECK (value_kind IN ('numeric','text','recommendation')),
  CONSTRAINT "ck_questionnaire_items_4" CHECK (ordinal > 0)
);
REVOKE ALL ON TABLE "public"."questionnaire_items" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."questionnaire_items" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."questionnaire_answers" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "response_id" uuid NOT NULL,
  "item_id" uuid NOT NULL,
  "definition_key" text NOT NULL,
  "numeric_value" numeric,
  "text_value" text,
  "answer_state" text DEFAULT 'missing' NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_questionnaire_answers" PRIMARY KEY ("id"),
  CONSTRAINT "uq_questionnaire_answers_0" UNIQUE ("response_id", "item_id"),
  CONSTRAINT "ck_questionnaire_answers_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_questionnaire_answers_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_questionnaire_answers_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL)),
  CONSTRAINT "ck_questionnaire_answers_3" CHECK (answer_state IN ('recorded','missing','needs_review')),
  CONSTRAINT "ck_questionnaire_answers_4" CHECK (num_nonnulls(numeric_value,text_value) <= 1),
  CONSTRAINT "ck_questionnaire_answers_5" CHECK ((answer_state = 'missing' AND numeric_value IS NULL AND text_value IS NULL) OR (answer_state <> 'missing' AND num_nonnulls(numeric_value,text_value) = 1))
);
REVOKE ALL ON TABLE "gk_private"."questionnaire_answers" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."questionnaire_answers" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "public"."attendance_observations" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "child_id" uuid NOT NULL,
  "service_code" text NOT NULL,
  "service_vocabulary" text GENERATED ALWAYS AS ('service_context'::text) STORED NOT NULL,
  "attendance_date" date NOT NULL,
  "mark_code" text NOT NULL,
  "mark_vocabulary" text GENERATED ALWAYS AS ('attendance_mark'::text) STORED NOT NULL,
  "program_code" text,
  "program_vocabulary" text GENERATED ALWAYS AS ('program'::text) STORED NOT NULL,
  "batch_reported" text,
  "child_status_reported" text,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_attendance_observations" PRIMARY KEY ("id"),
  CONSTRAINT "ck_attendance_observations_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_attendance_observations_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_attendance_observations_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL))
);
REVOKE ALL ON TABLE "public"."attendance_observations" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."attendance_observations" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "public"."support_observations" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "child_id" uuid NOT NULL,
  "participant_link_id" uuid,
  "event_reference" text NOT NULL,
  "event_date" date,
  "program_code" text,
  "program_vocabulary" text GENERATED ALWAYS AS ('program'::text) STORED NOT NULL,
  "numeric_value" numeric,
  "text_value" text,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_support_observations" PRIMARY KEY ("id"),
  CONSTRAINT "ck_support_observations_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_support_observations_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_support_observations_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL)),
  CONSTRAINT "ck_support_observations_3" CHECK (num_nonnulls(numeric_value,text_value) = 1)
);
REVOKE ALL ON TABLE "public"."support_observations" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."support_observations" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "public"."adl_visits" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "child_id" uuid NOT NULL,
  "program_code" text,
  "program_vocabulary" text GENERATED ALWAYS AS ('program'::text) STORED NOT NULL,
  "visit_flag" boolean NOT NULL,
  "visit_date" date,
  "source_slot" integer,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "origin_kind" text DEFAULT 'manual' NOT NULL,
  "review_state" text DEFAULT 'pending' NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  CONSTRAINT "pk_adl_visits" PRIMARY KEY ("id"),
  CONSTRAINT "ck_adl_visits_0" CHECK (origin_kind IN ('manual','import')),
  CONSTRAINT "ck_adl_visits_1" CHECK (review_state IN ('pending','accepted','needs_review')),
  CONSTRAINT "ck_adl_visits_2" CHECK ((archived_at IS NULL) = (archived_by IS NULL)),
  CONSTRAINT "ck_adl_visits_3" CHECK (visit_flag IS TRUE),
  CONSTRAINT "ck_adl_visits_4" CHECK (visit_date IS NOT NULL OR (origin_kind = 'import' AND review_state <> 'accepted')),
  CONSTRAINT "ck_adl_visits_5" CHECK (source_slot IS NULL OR source_slot > 0)
);
REVOKE ALL ON TABLE "public"."adl_visits" FROM PUBLIC, anon, authenticated;
ALTER TABLE "public"."adl_visits" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."source_artifacts" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "source_namespace" text NOT NULL,
  "file_code" text NOT NULL,
  "version_sha256" text NOT NULL,
  "source_locator" text,
  "worksheet_manifest" jsonb DEFAULT '{}'::jsonb NOT NULL,
  "captured_at" timestamptz DEFAULT now() NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  CONSTRAINT "pk_source_artifacts" PRIMARY KEY ("id"),
  CONSTRAINT "uq_source_artifacts_0" UNIQUE ("source_namespace", "file_code", "version_sha256"),
  CONSTRAINT "ck_source_artifacts_0" CHECK (version_sha256 ~ '^[a-f0-9]{64}$'),
  CONSTRAINT "ck_source_artifacts_1" CHECK (jsonb_typeof(worksheet_manifest) = 'object')
);
REVOKE ALL ON TABLE "gk_private"."source_artifacts" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."source_artifacts" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."source_records" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "artifact_id" uuid NOT NULL,
  "native_sheet_key" text NOT NULL,
  "source_row" integer NOT NULL,
  "cell_payload" jsonb DEFAULT '{}'::jsonb NOT NULL,
  "processing_state" text DEFAULT 'staged' NOT NULL,
  "diagnostics" jsonb DEFAULT '{}'::jsonb,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  CONSTRAINT "pk_source_records" PRIMARY KEY ("id"),
  CONSTRAINT "uq_source_records_0" UNIQUE ("artifact_id", "native_sheet_key", "source_row"),
  CONSTRAINT "ck_source_records_0" CHECK (source_row > 0),
  CONSTRAINT "ck_source_records_1" CHECK (processing_state IN ('staged','blocked','resolved','reference_only')),
  CONSTRAINT "ck_source_records_2" CHECK (jsonb_typeof(cell_payload) = 'object')
);
REVOKE ALL ON TABLE "gk_private"."source_records" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."source_records" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."source_provenance" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "source_record_id" uuid NOT NULL,
  "source_columns" text[] NOT NULL,
  "target_fields" text[] NOT NULL,
  "rule_reference" text NOT NULL,
  "contribution_state" text NOT NULL,
  "child_id" uuid,
  "private_profile_child_id" uuid,
  "caregiver_id" uuid,
  "child_caregiver_id" uuid,
  "program_change_id" uuid,
  "response_id" uuid,
  "item_id" uuid,
  "answer_id" uuid,
  "attendance_id" uuid,
  "support_id" uuid,
  "adl_id" uuid,
  "reference_vocabulary" text,
  "reference_code" text,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  CONSTRAINT "pk_source_provenance" PRIMARY KEY ("id"),
  CONSTRAINT "ck_source_provenance_0" CHECK (num_nonnulls(child_id,private_profile_child_id,caregiver_id,child_caregiver_id,program_change_id,response_id,item_id,answer_id,attendance_id,support_id,adl_id) + CASE WHEN reference_vocabulary IS NOT NULL AND reference_code IS NOT NULL THEN 1 ELSE 0 END = 1),
  CONSTRAINT "ck_source_provenance_1" CHECK ((reference_vocabulary IS NULL) = (reference_code IS NULL)),
  CONSTRAINT "ck_source_provenance_2" CHECK (cardinality(source_columns) > 0 AND cardinality(target_fields) > 0),
  CONSTRAINT "ck_source_provenance_3" CHECK (contribution_state IN ('selected','supporting','conflict_evidence')),
  CONSTRAINT "ck_source_provenance_4" CHECK (btrim(rule_reference) <> '')
);
REVOKE ALL ON TABLE "gk_private"."source_provenance" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."source_provenance" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."access_memberships" (
  "user_id" uuid NOT NULL,
  "approved_email_domain" text NOT NULL,
  "role_code" text NOT NULL,
  "role_vocabulary" text GENERATED ALWAYS AS ('access_role'::text) STORED NOT NULL,
  "active" boolean DEFAULT false NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  "archived_at" timestamptz,
  "archived_by" uuid,
  "private_read" boolean DEFAULT false NOT NULL,
  "private_write" boolean DEFAULT false NOT NULL,
  "approval_reference" text,
  CONSTRAINT "pk_access_memberships" PRIMARY KEY ("user_id"),
  CONSTRAINT "ck_access_memberships_0" CHECK ((archived_at IS NULL) = (archived_by IS NULL)),
  CONSTRAINT "ck_access_memberships_1" CHECK (approved_email_domain = 'goalkeep.net'),
  CONSTRAINT "ck_access_memberships_2" CHECK (NOT private_write OR private_read),
  CONSTRAINT "ck_access_memberships_3" CHECK (NOT active OR approval_reference IS NOT NULL)
);
REVOKE ALL ON TABLE "gk_private"."access_memberships" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."access_memberships" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."identity_candidates" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "source_record_id" uuid NOT NULL,
  "child_id" uuid,
  "caregiver_id" uuid,
  "match_method" text NOT NULL,
  "resolution_status" text NOT NULL,
  "evidence" jsonb DEFAULT '{}'::jsonb NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  CONSTRAINT "pk_identity_candidates" PRIMARY KEY ("id"),
  CONSTRAINT "ck_identity_candidates_0" CHECK (num_nonnulls(child_id,caregiver_id) = 1),
  CONSTRAINT "ck_identity_candidates_1" CHECK (match_method IN ('exact_identifier','verified_relationship','name_candidate','name_context','computed_identifier')),
  CONSTRAINT "ck_identity_candidates_2" CHECK (resolution_status IN ('verified','candidate','rejected')),
  CONSTRAINT "ck_identity_candidates_3" CHECK (resolution_status <> 'verified' OR match_method IN ('exact_identifier','verified_relationship')),
  CONSTRAINT "ck_identity_candidates_4" CHECK (jsonb_typeof(evidence) = 'object')
);
REVOKE ALL ON TABLE "gk_private"."identity_candidates" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."identity_candidates" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."recovery_actions" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "source_record_id" uuid NOT NULL,
  "donor_source_record_id" uuid,
  "child_id" uuid,
  "caregiver_id" uuid,
  "source_column" text NOT NULL,
  "field_key" text NOT NULL,
  "original_value" jsonb NOT NULL,
  "recovered_value" jsonb,
  "method" text NOT NULL,
  "validation_status" text NOT NULL,
  "identity_verified" boolean DEFAULT false NOT NULL,
  "authoritative_source" boolean DEFAULT false NOT NULL,
  "meaning_equivalent" boolean DEFAULT false NOT NULL,
  "has_conflict" boolean DEFAULT false NOT NULL,
  "evidence" jsonb DEFAULT '{}'::jsonb NOT NULL,
  "run_id" uuid NOT NULL,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  CONSTRAINT "pk_recovery_actions" PRIMARY KEY ("id"),
  CONSTRAINT "ck_recovery_actions_0" CHECK (num_nonnulls(child_id,caregiver_id) <= 1),
  CONSTRAINT "ck_recovery_actions_1" CHECK (validation_status IN ('auto_recovered','suggested','blocked_conflict','blocked_untrusted','no_recovery')),
  CONSTRAINT "ck_recovery_actions_2" CHECK (validation_status <> 'auto_recovered' OR (identity_verified AND authoritative_source AND meaning_equivalent AND NOT has_conflict AND donor_source_record_id IS NOT NULL AND recovered_value IS NOT NULL AND num_nonnulls(child_id,caregiver_id) = 1)),
  CONSTRAINT "ck_recovery_actions_3" CHECK (jsonb_typeof(evidence) = 'object')
);
REVOKE ALL ON TABLE "gk_private"."recovery_actions" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."recovery_actions" ENABLE ROW LEVEL SECURITY;
CREATE TABLE "gk_private"."record_audit_events" (
  "id" uuid DEFAULT gen_random_uuid() NOT NULL,
  "schema_name" text NOT NULL,
  "table_name" text NOT NULL,
  "record_key" jsonb DEFAULT '{}'::jsonb NOT NULL,
  "operation" text NOT NULL,
  "before_value" jsonb,
  "after_value" jsonb,
  "created_at" timestamptz DEFAULT now() NOT NULL,
  "updated_at" timestamptz DEFAULT now() NOT NULL,
  "created_by" uuid,
  "updated_by" uuid,
  "actor_ref" text DEFAULT ('db:' || CURRENT_USER) NOT NULL,
  CONSTRAINT "pk_record_audit_events" PRIMARY KEY ("id")
);
REVOKE ALL ON TABLE "gk_private"."record_audit_events" FROM PUBLIC, anon, authenticated;
ALTER TABLE "gk_private"."record_audit_events" ENABLE ROW LEVEL SECURITY;
ALTER TABLE "public"."reference_values" ADD CONSTRAINT "fk_reference_values_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."reference_values" ADD CONSTRAINT "fk_reference_values_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."reference_values" ADD CONSTRAINT "fk_reference_values_2" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."children" ADD CONSTRAINT "fk_children_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."children" ADD CONSTRAINT "fk_children_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."children" ADD CONSTRAINT "fk_children_2" FOREIGN KEY ("program_vocabulary", "current_program_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."children" ADD CONSTRAINT "fk_children_3" FOREIGN KEY ("program_vocabulary", "admitted_program_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."children" ADD CONSTRAINT "fk_children_4" FOREIGN KEY ("status_vocabulary", "child_status_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."children" ADD CONSTRAINT "fk_children_5" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_children_0" ON "public"."children" ("program_vocabulary", "current_program_code");
CREATE INDEX "ix_children_1" ON "public"."children" ("program_vocabulary", "admitted_program_code");
CREATE INDEX "ix_children_2" ON "public"."children" ("status_vocabulary", "child_status_code");
ALTER TABLE "gk_private"."child_private_profiles" ADD CONSTRAINT "fk_child_private_profiles_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."child_private_profiles" ADD CONSTRAINT "fk_child_private_profiles_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."child_private_profiles" ADD CONSTRAINT "fk_child_private_profiles_2" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."child_private_profiles" ADD CONSTRAINT "fk_child_private_profiles_3" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."caregivers" ADD CONSTRAINT "fk_caregivers_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."caregivers" ADD CONSTRAINT "fk_caregivers_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."caregivers" ADD CONSTRAINT "fk_caregivers_2" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."child_caregivers" ADD CONSTRAINT "fk_child_caregivers_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."child_caregivers" ADD CONSTRAINT "fk_child_caregivers_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."child_caregivers" ADD CONSTRAINT "fk_child_caregivers_2" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."child_caregivers" ADD CONSTRAINT "fk_child_caregivers_3" FOREIGN KEY ("caregiver_id") REFERENCES "gk_private"."caregivers" ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."child_caregivers" ADD CONSTRAINT "fk_child_caregivers_4" FOREIGN KEY ("role_vocabulary", "role_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."child_caregivers" ADD CONSTRAINT "fk_child_caregivers_5" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_child_caregivers_0" ON "public"."child_caregivers" ("child_id");
CREATE INDEX "ix_child_caregivers_1" ON "public"."child_caregivers" ("caregiver_id");
CREATE INDEX "ix_child_caregivers_2" ON "public"."child_caregivers" ("role_vocabulary", "role_code");
ALTER TABLE "public"."program_changes" ADD CONSTRAINT "fk_program_changes_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."program_changes" ADD CONSTRAINT "fk_program_changes_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."program_changes" ADD CONSTRAINT "fk_program_changes_2" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."program_changes" ADD CONSTRAINT "fk_program_changes_3" FOREIGN KEY ("program_vocabulary", "program_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."program_changes" ADD CONSTRAINT "fk_program_changes_4" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_program_changes_0" ON "public"."program_changes" ("program_vocabulary", "program_code");
CREATE INDEX "ix_program_changes_1" ON "public"."program_changes" ("child_id", "promotion_date");
ALTER TABLE "public"."questionnaire_responses" ADD CONSTRAINT "fk_questionnaire_responses_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_responses" ADD CONSTRAINT "fk_questionnaire_responses_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_responses" ADD CONSTRAINT "fk_questionnaire_responses_2" FOREIGN KEY ("child_caregiver_id") REFERENCES "public"."child_caregivers" ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_responses" ADD CONSTRAINT "fk_questionnaire_responses_3" FOREIGN KEY ("definition_vocabulary", "definition_key") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_responses" ADD CONSTRAINT "fk_questionnaire_responses_4" FOREIGN KEY ("program_vocabulary", "program_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_responses" ADD CONSTRAINT "fk_questionnaire_responses_5" FOREIGN KEY ("centre_vocabulary", "centre_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_responses" ADD CONSTRAINT "fk_questionnaire_responses_6" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_questionnaire_responses_0" ON "public"."questionnaire_responses" ("definition_vocabulary", "definition_key");
CREATE INDEX "ix_questionnaire_responses_1" ON "public"."questionnaire_responses" ("program_vocabulary", "program_code");
CREATE INDEX "ix_questionnaire_responses_2" ON "public"."questionnaire_responses" ("centre_vocabulary", "centre_code");
CREATE INDEX "ix_questionnaire_responses_3" ON "public"."questionnaire_responses" ("child_caregiver_id", "assessment_date");
ALTER TABLE "public"."questionnaire_items" ADD CONSTRAINT "fk_questionnaire_items_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_items" ADD CONSTRAINT "fk_questionnaire_items_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_items" ADD CONSTRAINT "fk_questionnaire_items_2" FOREIGN KEY ("definition_vocabulary", "definition_key") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."questionnaire_items" ADD CONSTRAINT "fk_questionnaire_items_3" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_questionnaire_items_0" ON "public"."questionnaire_items" ("definition_vocabulary", "definition_key");
ALTER TABLE "gk_private"."questionnaire_answers" ADD CONSTRAINT "fk_questionnaire_answers_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."questionnaire_answers" ADD CONSTRAINT "fk_questionnaire_answers_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."questionnaire_answers" ADD CONSTRAINT "fk_questionnaire_answers_2" FOREIGN KEY ("response_id", "definition_key") REFERENCES "public"."questionnaire_responses" ("id", "definition_key") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."questionnaire_answers" ADD CONSTRAINT "fk_questionnaire_answers_3" FOREIGN KEY ("item_id", "definition_key") REFERENCES "public"."questionnaire_items" ("id", "definition_key") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."questionnaire_answers" ADD CONSTRAINT "fk_questionnaire_answers_4" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_questionnaire_answers_0" ON "gk_private"."questionnaire_answers" ("response_id", "definition_key");
CREATE INDEX "ix_questionnaire_answers_1" ON "gk_private"."questionnaire_answers" ("item_id", "definition_key");
ALTER TABLE "public"."attendance_observations" ADD CONSTRAINT "fk_attendance_observations_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."attendance_observations" ADD CONSTRAINT "fk_attendance_observations_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."attendance_observations" ADD CONSTRAINT "fk_attendance_observations_2" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."attendance_observations" ADD CONSTRAINT "fk_attendance_observations_3" FOREIGN KEY ("service_vocabulary", "service_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."attendance_observations" ADD CONSTRAINT "fk_attendance_observations_4" FOREIGN KEY ("mark_vocabulary", "mark_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."attendance_observations" ADD CONSTRAINT "fk_attendance_observations_5" FOREIGN KEY ("program_vocabulary", "program_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."attendance_observations" ADD CONSTRAINT "fk_attendance_observations_6" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_attendance_observations_0" ON "public"."attendance_observations" ("service_vocabulary", "service_code");
CREATE INDEX "ix_attendance_observations_1" ON "public"."attendance_observations" ("mark_vocabulary", "mark_code");
CREATE INDEX "ix_attendance_observations_2" ON "public"."attendance_observations" ("program_vocabulary", "program_code");
CREATE INDEX "ix_attendance_observations_3" ON "public"."attendance_observations" ("child_id", "attendance_date");
ALTER TABLE "public"."support_observations" ADD CONSTRAINT "fk_support_observations_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."support_observations" ADD CONSTRAINT "fk_support_observations_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."support_observations" ADD CONSTRAINT "fk_support_observations_2" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."support_observations" ADD CONSTRAINT "fk_support_observations_3" FOREIGN KEY ("participant_link_id", "child_id") REFERENCES "public"."child_caregivers" ("id", "child_id") ON DELETE RESTRICT;
ALTER TABLE "public"."support_observations" ADD CONSTRAINT "fk_support_observations_4" FOREIGN KEY ("program_vocabulary", "program_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."support_observations" ADD CONSTRAINT "fk_support_observations_5" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_support_observations_0" ON "public"."support_observations" ("child_id");
CREATE INDEX "ix_support_observations_1" ON "public"."support_observations" ("participant_link_id", "child_id");
CREATE INDEX "ix_support_observations_2" ON "public"."support_observations" ("program_vocabulary", "program_code");
ALTER TABLE "public"."adl_visits" ADD CONSTRAINT "fk_adl_visits_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."adl_visits" ADD CONSTRAINT "fk_adl_visits_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."adl_visits" ADD CONSTRAINT "fk_adl_visits_2" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "public"."adl_visits" ADD CONSTRAINT "fk_adl_visits_3" FOREIGN KEY ("program_vocabulary", "program_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "public"."adl_visits" ADD CONSTRAINT "fk_adl_visits_4" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_adl_visits_0" ON "public"."adl_visits" ("program_vocabulary", "program_code");
CREATE INDEX "ix_adl_visits_1" ON "public"."adl_visits" ("child_id", "visit_date");
ALTER TABLE "gk_private"."source_artifacts" ADD CONSTRAINT "fk_source_artifacts_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_artifacts" ADD CONSTRAINT "fk_source_artifacts_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_records" ADD CONSTRAINT "fk_source_records_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_records" ADD CONSTRAINT "fk_source_records_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_records" ADD CONSTRAINT "fk_source_records_2" FOREIGN KEY ("artifact_id") REFERENCES "gk_private"."source_artifacts" ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_source_records_0" ON "gk_private"."source_records" ("processing_state", "artifact_id");
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_2" FOREIGN KEY ("source_record_id") REFERENCES "gk_private"."source_records" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_3" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_4" FOREIGN KEY ("private_profile_child_id") REFERENCES "gk_private"."child_private_profiles" ("child_id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_5" FOREIGN KEY ("caregiver_id") REFERENCES "gk_private"."caregivers" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_6" FOREIGN KEY ("child_caregiver_id") REFERENCES "public"."child_caregivers" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_7" FOREIGN KEY ("program_change_id") REFERENCES "public"."program_changes" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_8" FOREIGN KEY ("response_id") REFERENCES "public"."questionnaire_responses" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_9" FOREIGN KEY ("item_id") REFERENCES "public"."questionnaire_items" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_10" FOREIGN KEY ("answer_id") REFERENCES "gk_private"."questionnaire_answers" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_11" FOREIGN KEY ("attendance_id") REFERENCES "public"."attendance_observations" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_12" FOREIGN KEY ("support_id") REFERENCES "public"."support_observations" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_13" FOREIGN KEY ("adl_id") REFERENCES "public"."adl_visits" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."source_provenance" ADD CONSTRAINT "fk_source_provenance_14" FOREIGN KEY ("reference_vocabulary", "reference_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
CREATE INDEX "ix_source_provenance_0" ON "gk_private"."source_provenance" ("source_record_id");
CREATE INDEX "ix_source_provenance_1" ON "gk_private"."source_provenance" ("child_id");
CREATE INDEX "ix_source_provenance_2" ON "gk_private"."source_provenance" ("private_profile_child_id");
CREATE INDEX "ix_source_provenance_3" ON "gk_private"."source_provenance" ("caregiver_id");
CREATE INDEX "ix_source_provenance_4" ON "gk_private"."source_provenance" ("child_caregiver_id");
CREATE INDEX "ix_source_provenance_5" ON "gk_private"."source_provenance" ("program_change_id");
CREATE INDEX "ix_source_provenance_6" ON "gk_private"."source_provenance" ("response_id");
CREATE INDEX "ix_source_provenance_7" ON "gk_private"."source_provenance" ("item_id");
CREATE INDEX "ix_source_provenance_8" ON "gk_private"."source_provenance" ("answer_id");
CREATE INDEX "ix_source_provenance_9" ON "gk_private"."source_provenance" ("attendance_id");
CREATE INDEX "ix_source_provenance_10" ON "gk_private"."source_provenance" ("support_id");
CREATE INDEX "ix_source_provenance_11" ON "gk_private"."source_provenance" ("adl_id");
CREATE INDEX "ix_source_provenance_12" ON "gk_private"."source_provenance" ("reference_vocabulary", "reference_code");
ALTER TABLE "gk_private"."access_memberships" ADD CONSTRAINT "fk_access_memberships_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."access_memberships" ADD CONSTRAINT "fk_access_memberships_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."access_memberships" ADD CONSTRAINT "fk_access_memberships_2" FOREIGN KEY ("user_id") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."access_memberships" ADD CONSTRAINT "fk_access_memberships_3" FOREIGN KEY ("role_vocabulary", "role_code") REFERENCES "public"."reference_values" ("vocabulary", "code") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."access_memberships" ADD CONSTRAINT "fk_access_memberships_4" FOREIGN KEY ("archived_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_access_memberships_0" ON "gk_private"."access_memberships" ("role_vocabulary", "role_code");
ALTER TABLE "gk_private"."identity_candidates" ADD CONSTRAINT "fk_identity_candidates_0" FOREIGN KEY ("source_record_id") REFERENCES "gk_private"."source_records" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."identity_candidates" ADD CONSTRAINT "fk_identity_candidates_1" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."identity_candidates" ADD CONSTRAINT "fk_identity_candidates_2" FOREIGN KEY ("caregiver_id") REFERENCES "gk_private"."caregivers" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."identity_candidates" ADD CONSTRAINT "fk_identity_candidates_3" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."identity_candidates" ADD CONSTRAINT "fk_identity_candidates_4" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_identity_candidates_0" ON "gk_private"."identity_candidates" ("source_record_id");
ALTER TABLE "gk_private"."recovery_actions" ADD CONSTRAINT "fk_recovery_actions_0" FOREIGN KEY ("source_record_id") REFERENCES "gk_private"."source_records" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."recovery_actions" ADD CONSTRAINT "fk_recovery_actions_1" FOREIGN KEY ("child_id") REFERENCES "public"."children" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."recovery_actions" ADD CONSTRAINT "fk_recovery_actions_2" FOREIGN KEY ("caregiver_id") REFERENCES "gk_private"."caregivers" ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."recovery_actions" ADD CONSTRAINT "fk_recovery_actions_3" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."recovery_actions" ADD CONSTRAINT "fk_recovery_actions_4" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."recovery_actions" ADD CONSTRAINT "fk_recovery_actions_5" FOREIGN KEY ("donor_source_record_id") REFERENCES "gk_private"."source_records" ("id") ON DELETE RESTRICT;
CREATE INDEX "ix_recovery_actions_0" ON "gk_private"."recovery_actions" ("source_record_id");
ALTER TABLE "gk_private"."record_audit_events" ADD CONSTRAINT "fk_record_audit_events_0" FOREIGN KEY ("created_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
ALTER TABLE "gk_private"."record_audit_events" ADD CONSTRAINT "fk_record_audit_events_1" FOREIGN KEY ("updated_by") REFERENCES auth.users ("id") ON DELETE RESTRICT;
CREATE UNIQUE INDEX uq_identity_candidate_child ON gk_private.identity_candidates (source_record_id, child_id, match_method) WHERE child_id IS NOT NULL;
CREATE UNIQUE INDEX uq_identity_candidate_caregiver ON gk_private.identity_candidates (source_record_id, caregiver_id, match_method) WHERE caregiver_id IS NOT NULL;
COMMIT;
