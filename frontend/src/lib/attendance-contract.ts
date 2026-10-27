// Contract subset for the separately proposed protected staging table; no API is activated here.
export type Json =
  string | number | boolean | null | Json[] | { [key: string]: Json };
export type StagedAttendanceEvidence = {
  id: string;
  source_record_id: string;
  source_file: string;
  source_sheet: string;
  native_sheet_key: string;
  source_row: number;
  source_column: string;
  original_mark: Json;
  original_header: Json;
  recorded_child_identifier: Json;
  recorded_child_name: Json;
  parsed_date: string | null;
  verified_child_id: string | null;
  candidate_child_ids: string[];
  identity_status: "VERIFIED" | "PROVISIONAL_MATCH" | "AMBIGUOUS" | "UNMATCHED";
  date_status:
    | "VERIFIED"
    | "MISSING"
    | "FORMULA_UNRESOLVED"
    | "SANITIZED_UNTRUSTED"
    | "UNPARSED";
  code_status: "VERIFIED" | "PENDING";
  review_status: "pending" | "reviewed" | "excluded";
  flags: string[];
  review_notes: string;
};
// Preserve false/zero and opaque values. Display formatting never assigns attendance meaning.
export function formatEvidence(value: Json): string {
  return value === null
    ? "Not recorded"
    : typeof value === "string"
      ? value
      : JSON.stringify(value);
}
