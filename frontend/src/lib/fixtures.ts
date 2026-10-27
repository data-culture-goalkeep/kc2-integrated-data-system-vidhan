// SYNTHETIC DEMONSTRATION ONLY. No source snapshot, private work/ data or real identities are imported.
export type Child = {
  id: string;
  child_business_id: string;
  display_name: string;
  program: string;
  review_state: "pending" | "accepted";
};
export const children: Child[] = Array.from({ length: 28 }, (_, i) => ({
  id: `demo-child-${i + 1}`,
  child_business_id: `DEMO-C${String(i + 1).padStart(3, "0")}`,
  display_name: `Demo child ${String(i + 1).padStart(2, "0")}`,
  program: i % 2 ? "Demo programme B" : "Demo programme A",
  review_state: i % 5 ? "pending" : "accepted",
}));
export const caregivers = Array.from({ length: 36 }, (_, i) => ({
  id: `demo-caregiver-${i + 1}`,
  caregiver_business_id: `DEMO-G${String(i + 1).padStart(3, "0")}`,
  display_name: `Demo caregiver ${String(i + 1).padStart(2, "0")}`,
  review_state: "pending",
}));
export const relationships = caregivers.map((g, i) => ({
  id: `demo-pair-${i + 1}`,
  child_id: children[i % children.length].id,
  caregiver_id: g.id,
  review_state: "pending",
}));
export type Attendance = {
  id: string;
  child_id: string;
  attendance_date: string;
  mark_code: string;
  review_state: "accepted" | "pending";
};
export const attendance: Attendance[] = Array.from({ length: 16 }, (_, i) => ({
  id: `demo-attendance-${i + 1}`,
  child_id: children[i % children.length].id,
  attendance_date: `2025-08-${String(12 + i).padStart(2, "0")}`,
  mark_code: i % 4 ? "DEMO_PRESENT" : "DEMO_ABSENT",
  review_state: "accepted",
}));
export type PendingAttendance = {
  id: string;
  source_record_id: string;
  source_reference: string;
  source_column: string;
  original_mark: string;
  original_header: string | null;
  candidate_child_ids: string[];
  identity_status: "PROVISIONAL_MATCH" | "AMBIGUOUS" | "UNMATCHED";
  date_status: string;
  code_status: "PENDING";
  review_status: "pending";
  review_notes: string;
  flags: string[];
};
export const pendingAttendance: PendingAttendance[] = Array.from(
  { length: 15 },
  (_, i) => ({
    id: `demo-staging-${i + 1}`,
    source_record_id: `demo-source-${i + 1}`,
    source_reference: `DEMO-FILE/T01/R${i + 12}`,
    source_column: i % 2 ? "H" : "G",
    original_mark: ["P", "A", "-", "M", "[FORMULA]"][i % 5],
    original_header:
      i % 3 ? `2025-08-${String(10 + i).padStart(2, "0")}` : null,
    candidate_child_ids:
      i % 3 === 0
        ? []
        : i % 3 === 1
          ? [children[i].id]
          : [children[i].id, children[i + 1].id],
    identity_status:
      i % 3 === 0
        ? "UNMATCHED"
        : i % 3 === 1
          ? "PROVISIONAL_MATCH"
          : "AMBIGUOUS",
    date_status: i % 3 ? "SANITIZED_UNTRUSTED" : "MISSING",
    code_status: "PENDING",
    review_status: "pending",
    review_notes: "",
    flags: ["DATE_PENDING", "CODE_PENDING"],
  }),
);
export const questionnaires = Array.from({ length: 12 }, (_, i) => ({
  id: `demo-response-${i + 1}`,
  child_caregiver_id: relationships[i].id,
  definition_key: "DEMO-INSTRUMENT",
  assessment_date: null,
  review_state: "pending",
  answer_slots: 31,
}));
export const adl = [
  {
    id: "demo-adl-1",
    child_id: children[1].id,
    visit_date: null,
    visit_flag: true,
    review_state: "pending",
  },
  {
    id: "demo-adl-2",
    child_id: children[3].id,
    visit_date: "2025-08-20",
    visit_flag: true,
    review_state: "pending",
  },
];
export const support = [
  {
    id: "demo-support-1",
    child_id: children[2].id,
    event_reference: "DEMO-EVENT-001",
    event_date: null,
    text_value: "Synthetic observation for interface testing",
    review_state: "pending",
  },
];
export function childName(id: string) {
  return children.find((c) => c.id === id)?.display_name ?? "Not assigned";
}
export function caregiverName(id: string) {
  return caregivers.find((c) => c.id === id)?.display_name ?? "Not assigned";
}
