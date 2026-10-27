"use client";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import {
  ArrowDown,
  ArrowUp,
  ArrowUpRight,
  CalendarDays,
  Check,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  FileQuestion,
  Flag,
  HeartHandshake,
  LayoutDashboard,
  Link2,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Search,
  ShieldCheck,
  Users,
  UserRound,
  View,
  Workflow,
  X,
  AlertTriangle,
  Activity,
  LockKeyhole,
  Clock3,
  CheckCircle2,
  FileSpreadsheet,
} from "lucide-react";
import * as demo from "@/lib/fixtures";
type Row = {
  id: string;
  title: string;
  subtitle: string;
  program: string;
  state: string;
  date?: string | null;
  source?: string;
  mark?: string;
  flags?: string[];
  kind?: string;
  childId?: string;
  caregiverId?: string;
};
type DialogState = { group: string; row?: Row };
const navigation = [
  { path: "/", name: "Overview", icon: LayoutDashboard },
  { path: "/children", name: "Children", icon: UserRound },
  { path: "/caregivers", name: "Caregivers", icon: Users },
  { path: "/relationships", name: "Relationships", icon: Link2 },
  { path: "/questionnaires", name: "Questionnaires", icon: FileQuestion },
  { path: "/attendance", name: "Attendance", icon: CalendarDays },
  { path: "/adl", name: "ADL visits", icon: Activity },
  { path: "/support", name: "Support observations", icon: HeartHandshake },
  { path: "/data-quality", name: "Data quality", icon: ShieldCheck },
];
const descriptions: Record<
  string,
  { title: string; description: string; action: string }
> = {
  children: {
    title: "Children",
    description: "A clear view of each child and their connected records.",
    action: "Add child",
  },
  caregivers: {
    title: "Caregivers",
    description: "Caregiver profiles and the children they support.",
    action: "Add caregiver",
  },
  relationships: {
    title: "Child–caregiver relationships",
    description:
      "Explicit links keep people connected without guessing identities.",
    action: "Add relationship",
  },
  questionnaires: {
    title: "Questionnaires",
    description:
      "Explore responses and literal answers. Scoring remains separate.",
    action: "Record questionnaire",
  },
  attendance: {
    title: "Attendance",
    description:
      "Approved records and unresolved source evidence, clearly separated.",
    action: "Record attendance",
  },
  adl: {
    title: "ADL visits",
    description: "Track visits while keeping missing information visible.",
    action: "Record visit",
  },
  support: {
    title: "Support observations",
    description: "Review support events with their context and evidence.",
    action: "Record observation",
  },
  "data-quality": {
    title: "Data-quality review",
    description:
      "Keep uncertainty visible, traceable and ready for an authorized review.",
    action: "Review workflow",
  },
};
const readable = (s: string) =>
  ({
    accepted: "Approved",
    pending: "Pending",
    PROVISIONAL_MATCH: "Provisional match",
    AMBIGUOUS: "Ambiguous",
    UNMATCHED: "Unmatched",
    DATE_PENDING: "Date pending",
    CODE_PENDING: "Code pending",
  })[s] ?? s.replaceAll("_", " ").toLowerCase();
function Badge({ state }: { state: string }) {
  return (
    <span
      className={
        "badge " +
        (state === "accepted"
          ? "success"
          : state === "UNMATCHED"
            ? "muted"
            : state === "AMBIGUOUS"
              ? "warning"
              : "pending")
      }
    >
      {state === "accepted" ? (
        <Check size={12} />
      ) : (
        <span className="badge-dot" />
      )}
      {readable(state)}
    </span>
  );
}
function DemoDialog({
  state,
  onClose,
  onSave,
  childrenOptions,
  caregiverOptions,
  note,
  pendingRecord,
}: {
  state: DialogState;
  onClose: () => void;
  onSave: (data: FormData) => void;
  childrenOptions: demo.Child[];
  caregiverOptions: typeof demo.caregivers;
  note: string;
  pendingRecord?: demo.PendingAttendance;
}) {
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    ref.current?.showModal();
  }, []);
  const isReview = state.group === "review";
  return (
    <dialog
      aria-labelledby="dialog-title"
      ref={ref}
      className="form-dialog"
      onCancel={(e) => {
        e.preventDefault();
        onClose();
      }}
    >
      <form
        onSubmit={(e: FormEvent<HTMLFormElement>) => {
          e.preventDefault();
          onSave(new FormData(e.currentTarget));
        }}
      >
        <div className="dialog-heading">
          <div>
            <span className="eyebrow">SYNTHETIC PREVIEW</span>
            <h2 id="dialog-title">
              {isReview
                ? "Review source evidence"
                : state.row
                  ? state.group === "attendance"
                    ? "Propose a demo correction"
                    : "Edit demo record"
                  : (descriptions[state.group]?.action ?? "Add demo record")}
            </h2>
          </div>
          <button
            type="button"
            className="icon-button"
            aria-label="Close dialog"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>
        {isReview ? (
          <>
            <div className="evidence-box">
              <span>Immutable source reference</span>
              <strong>{state.row?.source}</strong>
              <div>
                Original value: <b>{state.row?.mark ?? "Not recorded"}</b>
              </div>
              <p>
                Candidate identity, date and code remain unverified. A note does
                not approve an attendance record.
              </p>
              <dl className="evidence-details">
                <dt>Source record</dt>
                <dd>{pendingRecord?.source_record_id ?? "Demo reference"}</dd>
                <dt>Original header</dt>
                <dd>{pendingRecord?.original_header ?? "Missing header"}</dd>
                <dt>Date verification</dt>
                <dd>
                  {pendingRecord?.date_status
                    .replaceAll("_", " ")
                    .toLowerCase()}
                </dd>
              </dl>
              <div className="candidate-list">
                <span>Possible matches · not verified</span>
                {pendingRecord?.candidate_child_ids.length ? (
                  pendingRecord.candidate_child_ids.map((id) => (
                    <div key={id}>
                      <UserRound size={15} />
                      <span>
                        {childrenOptions.find((c) => c.id === id)
                          ?.display_name ?? "Unknown demo candidate"}
                        <small>{id}</small>
                      </span>
                    </div>
                  ))
                ) : (
                  <p>No supported candidate identity is available.</p>
                )}
              </div>
            </div>
            <label>
              Review note
              <textarea
                name="notes"
                defaultValue={note}
                rows={4}
                placeholder="Describe the evidence or next step…"
              />
            </label>
            <button
              className="button secondary"
              type="button"
              disabled
              title="Requires an approved crosswalk and authorized backend review"
            >
              Approve identity — unavailable
            </button>
          </>
        ) : (
          <>
            {[
              "relationships",
              "attendance",
              "questionnaires",
              "adl",
              "support",
            ].includes(state.group) ? (
              <label>
                Child
                <select
                  name="child"
                  required
                  defaultValue={state.row?.childId ?? ""}
                >
                  <option value="" disabled>
                    Select a synthetic child
                  </option>
                  {childrenOptions.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.display_name} · {c.child_business_id}
                    </option>
                  ))}
                </select>
              </label>
            ) : (
              <label>
                Display name
                <input
                  name="name"
                  autoFocus
                  required
                  defaultValue={state.row?.title ?? ""}
                  placeholder={
                    state.group === "children"
                      ? "e.g. Demo child 29"
                      : "e.g. Demo caregiver 37"
                  }
                />
              </label>
            )}
            {state.group === "relationships" && (
              <label>
                Caregiver
                <select
                  name="caregiver"
                  required
                  defaultValue={state.row?.caregiverId ?? ""}
                >
                  <option value="" disabled>
                    Select a synthetic caregiver
                  </option>
                  {caregiverOptions.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.display_name}
                    </option>
                  ))}
                </select>
              </label>
            )}
            {state.group === "children" && (
              <label>
                Programme
                <select
                  name="programme"
                  defaultValue={state.row?.program ?? "Demo programme A"}
                >
                  <option>Demo programme A</option>
                  <option>Demo programme B</option>
                </select>
              </label>
            )}
            {["attendance", "adl", "support"].includes(state.group) && (
              <label>
                Reported date{" "}
                <span className="field-hint">
                  Optional · never filled automatically
                </span>
                <input name="date" type="date" />
              </label>
            )}
            {state.group === "attendance" && (
              <label>
                Original attendance value
                <input
                  name="mark"
                  required
                  placeholder="Enter a demo source value, e.g. P"
                />
              </label>
            )}
            {["questionnaires", "adl", "support"].includes(state.group) && (
              <label>
                Note
                <textarea
                  name="notes"
                  rows={3}
                  placeholder="Synthetic record note"
                />
              </label>
            )}
          </>
        )}
        <p className="form-caption">
          <LockKeyhole size={14} /> Demo memory only. No live database write or
          approval.
        </p>
        <div className="dialog-footer">
          <button className="button secondary" type="button" onClick={onClose}>
            Cancel
          </button>
          <button className="button primary" type="submit">
            {isReview ? "Save demo note" : "Save demo record"}
          </button>
        </div>
      </form>
    </dialog>
  );
}
export default function Workspace({ route }: { route: string }) {
  const [collapsed, setCollapsed] = useState(false),
    [mobileOpen, setMobileOpen] = useState(false),
    [search, setSearch] = useState(""),
    [programme, setProgramme] = useState("All programmes"),
    [status, setStatus] = useState("All statuses"),
    [from, setFrom] = useState(""),
    [to, setTo] = useState(""),
    [page, setPage] = useState(1),
    [sort, setSort] = useState<"title" | "date">("title"),
    [ascending, setAscending] = useState(true),
    [dialog, setDialog] = useState<DialogState | null>(null),
    [toast, setToast] = useState("");
  const [children, setChildren] = useState(demo.children),
    [caregivers, setCaregivers] = useState(demo.caregivers),
    [links, setLinks] = useState(demo.relationships),
    [pending, setPending] = useState(demo.pendingAttendance),
    [extras, setExtras] = useState<Record<string, Row[]>>({}),
    [overrides, setOverrides] = useState<Record<string, Row>>({});
  const key = route.split("/")[1] || "overview";
  const pendingView = route === "/attendance/pending";
  const detail = descriptions[key];
  const childName = (id: string) =>
    children.find((c) => c.id === id)?.display_name ?? "Not assigned";
  const childProgram = (id: string) =>
    children.find((c) => c.id === id)?.program ?? "Not assigned";
  useEffect(() => {
    setPage(1);
  }, [search, programme, status, from, to, route]);
  useEffect(() => {
    setSearch("");
    setProgramme("All programmes");
    setStatus("All statuses");
    setMobileOpen(false);
  }, [route]);
  useEffect(() => {
    if (toast) {
      const id = setTimeout(() => setToast(""), 5000);
      return () => clearTimeout(id);
    }
  }, [toast]);
  const pendingRows: Row[] = pending.map((p) => ({
    id: p.id,
    title:
      p.candidate_child_ids.length === 1
        ? childName(p.candidate_child_ids[0])
        : p.candidate_child_ids.length
          ? "Multiple candidates"
          : "Unmatched source row",
    subtitle: p.candidate_child_ids.length
      ? `${p.candidate_child_ids.length} unapproved candidate${p.candidate_child_ids.length > 1 ? "s" : ""}`
      : "No supported child match",
    program: "Not verified",
    state: p.identity_status,
    date: null,
    source: p.source_reference + "/" + p.source_column,
    mark: p.original_mark,
    flags: p.flags,
    kind: "review",
  }));
  let rows: Row[] = [];
  if (key === "children")
    rows = children.map((c) => ({
      id: c.id,
      title: c.display_name,
      subtitle: c.child_business_id,
      program: c.program,
      state: c.review_state,
    }));
  if (key === "caregivers")
    rows = caregivers.map((c) => ({
      id: c.id,
      title: c.display_name,
      subtitle: c.caregiver_business_id,
      program: "Restricted profile",
      state: c.review_state,
    }));
  if (key === "relationships")
    rows = links.map((l) => ({
      id: l.id,
      childId: l.child_id,
      caregiverId: l.caregiver_id,
      title: childName(l.child_id),
      subtitle:
        caregivers.find((g) => g.id === l.caregiver_id)?.display_name ??
        "Not assigned",
      program: childProgram(l.child_id),
      state: l.review_state,
    }));
  if (key === "questionnaires")
    rows = demo.questionnaires.map((q) => {
      const pair = links.find((l) => l.id === q.child_caregiver_id);
      return {
        id: q.id,
        childId: pair?.child_id,
        title: pair ? childName(pair.child_id) : "Not assigned",
        subtitle: "31 literal answer slots · scoring not configured",
        program: pair ? childProgram(pair.child_id) : "",
        state: q.review_state,
        date: q.assessment_date,
        source: "DEMO-INSTRUMENT",
      };
    });
  if (key === "attendance")
    rows = pendingView
      ? pendingRows
      : demo.attendance
          .filter((a) => a.review_state === "accepted")
          .map((a) => ({
            id: a.id,
            childId: a.child_id,
            title: childName(a.child_id),
            subtitle:
              a.mark_code === "DEMO_PRESENT"
                ? "Present · synthetic approved code"
                : "Absent · synthetic approved code",
            program: childProgram(a.child_id),
            state: a.review_state,
            date: a.attendance_date,
            mark: a.mark_code,
          }));
  if (key === "adl")
    rows = demo.adl.map((v) => ({
      id: v.id,
      childId: v.child_id,
      title: childName(v.child_id),
      subtitle: "Synthetic checked visit slot",
      program: childProgram(v.child_id),
      state: v.review_state,
      date: v.visit_date,
    }));
  if (key === "support")
    rows = demo.support.map((v) => ({
      id: v.id,
      childId: v.child_id,
      title: childName(v.child_id),
      subtitle: v.text_value,
      program: childProgram(v.child_id),
      state: v.review_state,
      date: v.event_date,
      source: v.event_reference,
    }));
  if (key === "data-quality")
    rows = pendingRows.map((r) => ({
      ...r,
      subtitle: "Attendance · identity, date and code review",
    }));
  rows = [...rows, ...(extras[pendingView ? "review" : key] ?? [])].map(
    (r) => overrides[r.id] ?? r,
  );
  const filtered = useMemo(
    () =>
      rows
        .filter(
          (r) =>
            (
              r.title +
              " " +
              r.subtitle +
              " " +
              r.id +
              " " +
              r.source +
              " " +
              r.mark
            )
              .toLowerCase()
              .includes(search.toLowerCase()) &&
            (programme === "All programmes" || r.program === programme) &&
            (status === "All statuses" || r.state === status) &&
            (!from || (!!r.date && r.date >= from)) &&
            (!to || (!!r.date && r.date <= to)),
        )
        .sort(
          (a, b) =>
            String(a[sort] ?? "").localeCompare(String(b[sort] ?? "")) *
            (ascending ? 1 : -1),
        ),
    [rows, search, programme, status, from, to, sort, ascending],
  );
  const pageSize = 8,
    pageCount = Math.max(1, Math.ceil(filtered.length / pageSize)),
    visible = filtered.slice(
      (Math.min(page, pageCount) - 1) * pageSize,
      Math.min(page, pageCount) * pageSize,
    );
  function save(data: FormData) {
    if (!dialog) return;
    const group = dialog.group,
      id = dialog.row?.id ?? `demo-new-${crypto.randomUUID()}`,
      name = String(data.get("name") ?? ""),
      program = String(data.get("programme") ?? ""),
      child = String(data.get("child") ?? "");
    if (group === "review") {
      setPending((p) =>
        p.map((r) =>
          r.id === id
            ? { ...r, review_notes: String(data.get("notes") ?? "") }
            : r,
        ),
      );
    } else if (group === "children") {
      setChildren((cs) =>
        dialog.row
          ? cs.map((c) =>
              c.id === id ? { ...c, display_name: name, program } : c,
            )
          : [
              ...cs,
              {
                id,
                child_business_id: `DEMO-C${cs.length + 1}`,
                display_name: name,
                program,
                review_state: "pending",
              },
            ],
      );
    } else if (group === "caregivers") {
      setCaregivers((cs) =>
        dialog.row
          ? cs.map((c) => (c.id === id ? { ...c, display_name: name } : c))
          : [
              ...cs,
              {
                id,
                caregiver_business_id: `DEMO-G${cs.length + 1}`,
                display_name: name,
                review_state: "pending",
              },
            ],
      );
    } else if (group === "relationships") {
      const caregiver = String(data.get("caregiver"));
      if (
        links.some(
          (l) =>
            l.id !== id && l.child_id === child && l.caregiver_id === caregiver,
        )
      ) {
        setToast("This demo relationship already exists.");
        return;
      }
      setLinks((ls) =>
        dialog.row
          ? ls.map((l) =>
              l.id === id
                ? { ...l, child_id: child, caregiver_id: caregiver }
                : l,
            )
          : [
              ...ls,
              {
                id,
                child_id: child,
                caregiver_id: caregiver,
                review_state: "pending",
              },
            ],
      );
    } else if (group === "attendance") {
      setPending((ps) => [
        ...ps,
        {
          id,
          source_record_id: "DEMO-MANUAL",
          source_reference: "DEMO-MANUAL/RECORD",
          source_column: "G",
          original_mark: String(data.get("mark")),
          original_header: String(data.get("date")) || null,
          candidate_child_ids: [child],
          identity_status: "PROVISIONAL_MATCH",
          date_status: data.get("date") ? "SANITIZED_UNTRUSTED" : "MISSING",
          code_status: "PENDING",
          review_status: "pending",
          review_notes: "Manual synthetic entry; not an identity approval",
          flags: ["DATE_PENDING", "CODE_PENDING"],
        },
      ]);
    } else if (dialog.row) {
      setOverrides((x) => ({
        ...x,
        [id]: {
          ...dialog.row!,
          childId: child,
          title: childName(child),
          subtitle: String(
            data.get("notes") ?? dialog.row?.subtitle ?? "Synthetic record",
          ),
          date: String(data.get("date")) || null,
        },
      }));
    } else {
      setExtras((x) => ({
        ...x,
        [group]: [
          ...(x[group] ?? []),
          {
            id,
            title: childName(child),
            subtitle: String(data.get("notes") ?? "Synthetic record"),
            program: childProgram(child),
            state: "pending",
            date: String(data.get("date")) || null,
          },
        ],
      }));
    }
    setDialog(null);
    setToast(
      group === "attendance"
        ? "Demo record added to Pending Attendance Review. Nothing was approved."
        : "Saved in demo memory only. No live database changes.",
    );
  }
  const cards = [
    {
      name: "Children",
      value: children.length,
      caption: "Synthetic directory",
      icon: UserRound,
    },
    {
      name: "Caregiver links",
      value: links.length,
      caption: "Explicit demo relationships",
      icon: Link2,
    },
    {
      name: "Approved attendance",
      value: demo.attendance.length,
      caption: "Synthetic approved records only",
      icon: CheckCircle2,
    },
    {
      name: "Awaiting review",
      value: pending.length,
      caption: "Kept outside verified reporting",
      icon: Flag,
    },
  ];
  return (
    <div
      className={`workspace ${collapsed ? "collapsed" : ""} ${mobileOpen ? "mobile-open" : ""}`}
    >
      <header className="topbar">
        <Link className="brand" href="/">
          <span className="brand-symbol">
            <Workflow size={23} />
          </span>
          <span className="brand-name">
            goalkeep<span className="brand-period">.</span>
          </span>
        </Link>
        <button
          className="icon-button desktop-toggle"
          aria-label={collapsed ? "Expand navigation" : "Collapse navigation"}
          onClick={() => setCollapsed(!collapsed)}
        >
          {collapsed ? (
            <PanelLeftOpen size={19} />
          ) : (
            <PanelLeftClose size={19} />
          )}
        </button>
        <button
          className="icon-button mobile-toggle"
          aria-label="Open navigation"
          onClick={() => setMobileOpen(!mobileOpen)}
        >
          <Menu size={20} />
        </button>
        <div className="topbar-context">
          KC-2 <span>/</span> Integrated Data System
        </div>
        <div className="topbar-right">
          <span className="preview-pill">
            <span />
            Local fixture preview
          </span>
          <Link
            href="/login"
            className="account"
            title="Authentication foundation; activation pending"
          >
            <span className="avatar">GK</span>
            <span>
              Preview visitor<small>No application role</small>
            </span>
          </Link>
        </div>
      </header>
      {mobileOpen && (
        <button
          className="nav-backdrop"
          aria-label="Close navigation"
          onClick={() => setMobileOpen(false)}
        />
      )}
      <aside className="sidebar">
        <div className="nav-section-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {navigation.map((n, i) => {
            const Icon = n.icon;
            const active =
              n.path === "/" ? route === "/" : route.startsWith(n.path);
            return (
              <div key={n.path}>
                {i === 5 && <div className="nav-divider" />}
                <Link
                  aria-label={n.name}
                  title={n.name}
                  aria-current={active ? "page" : undefined}
                  className={"nav-link " + (active ? "active" : "")}
                  href={n.path}
                >
                  <Icon size={19} />
                  <span className="nav-label">{n.name}</span>
                  {n.path === "/data-quality" && (
                    <span className="nav-count">{pending.length}</span>
                  )}
                </Link>
              </div>
            );
          })}
        </nav>
        <div className="sidebar-bottom">
          <ShieldCheck size={20} />
          <div>
            <b>Protected pilot</b>
            <span>Synthetic data only</span>
          </div>
        </div>
      </aside>
      <main className="main">
        <div className="preview-banner">
          <span>
            <LockKeyhole size={14} />
            <strong>Safe preview</strong> · All people, records and dates below
            are synthetic.
          </span>
          <span className="banner-detail">
            Live access & OAuth not activated
          </span>
        </div>
        {route === "/login" || route === "/access-pending" ? (
          <section className="auth-card">
            <span className="large-icon">
              <ShieldCheck size={32} />
            </span>
            <span className="eyebrow">GOALKEEP WORKSPACE</span>
            <h1>
              {route === "/access-pending"
                ? "Application access pending"
                : "One workspace. Secure access."}
            </h1>
            <p>
              Google authentication is prepared for verified Goalkeep Workspace
              identities. A matching email domain alone never grants access; an
              approved membership and database permissions are also required.
            </p>
            <form action="/auth/sign-in" method="post">
              <button disabled className="button primary">
                <LockKeyhole size={17} /> Continue with Google · not activated
              </button>
            </form>
            <p className="small">
              No separate application password. No role or user access has been
              activated in this preview.
            </p>
            <Link className="text-link" href="/">
              Return to synthetic workspace <ArrowUpRight size={15} />
            </Link>
          </section>
        ) : key === "overview" ? (
          <>
            <div className="page-heading">
              <div>
                <span className="eyebrow">YOUR WORKSPACE AT A GLANCE</span>
                <h1>Overview</h1>
                <p>
                  A connected view of people, observations and the evidence
                  behind them.
                </p>
              </div>
              <button
                className="button primary"
                onClick={() => setDialog({ group: "children" })}
              >
                <Plus size={17} /> Add child
              </button>
            </div>
            <div className="metric-grid">
              {cards.map((c) => {
                const Icon = c.icon;
                return (
                  <article className="metric-card" key={c.name}>
                    <div>
                      <span>{c.name}</span>
                      <Icon size={19} />
                    </div>
                    <strong>{c.value}</strong>
                    <small>{c.caption}</small>
                  </article>
                );
              })}
            </div>
            <div className="overview-grid">
              <section className="panel activity-panel">
                <div className="panel-heading">
                  <div>
                    <h2>Attendance activity</h2>
                    <p>Illustrative session activity · synthetic fixtures</p>
                  </div>
                  <span className="subtle-chip">Demo week</span>
                </div>
                <div
                  className="bar-chart"
                  aria-label="Illustrative synthetic weekly activity"
                >
                  {[8, 12, 10, 16, 13, 7, 11].map((n, i) => (
                    <div key={i}>
                      <span className="bar-value">{n}</span>
                      <div
                        className="chart-bar"
                        style={{ height: `${n * 9}px` }}
                      />
                      <small>
                        {["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][i]}
                      </small>
                    </div>
                  ))}
                </div>
                <div className="chart-note">
                  <span className="legend-dot" /> Demonstration only · not
                  derived from NGO attendance
                </div>
              </section>
              <section className="panel review-panel">
                <span className="large-icon amber">
                  <Flag size={23} />
                </span>
                <h2>Uncertainty stays visible.</h2>
                <p>
                  Source observations stay available for review, even when
                  identities, dates or codes cannot be confirmed.
                </p>
                <div className="review-stat">
                  <strong>
                    {
                      pending.filter((p) => p.identity_status === "UNMATCHED")
                        .length
                    }
                  </strong>
                  <span>unmatched demo rows</span>
                </div>
                <Link className="button primary" href="/attendance/pending">
                  Open pending review <ArrowUpRight size={16} />
                </Link>
              </section>
            </div>
            <section className="panel">
              <div className="panel-heading">
                <div>
                  <h2>Review queue</h2>
                  <p>A few synthetic examples requiring attention</p>
                </div>
                <Link href="/data-quality" className="text-link">
                  View all <ArrowUpRight size={15} />
                </Link>
              </div>
              <div className="queue-list">
                {pendingRows.slice(0, 3).map((r) => (
                  <button
                    key={r.id}
                    onClick={() => setDialog({ group: "review", row: r })}
                  >
                    <span className="queue-icon">
                      <FileSpreadsheet size={19} />
                    </span>
                    <div>
                      <strong>{r.title}</strong>
                      <span>{r.source}</span>
                    </div>
                    <Badge state={r.state} />
                    <ChevronRight size={17} />
                  </button>
                ))}
              </div>
            </section>
          </>
        ) : (
          <>
            <div className="breadcrumb">
              Workspace <ChevronRight size={13} /> {detail?.title}
            </div>
            <div className="page-heading">
              <div>
                <div className="title-line">
                  <h1>{detail?.title}</h1>
                  {["caregivers", "data-quality"].includes(key) && (
                    <span className="restricted-label">
                      <LockKeyhole size={12} /> Restricted in live system
                    </span>
                  )}
                </div>
                <p>{detail?.description}</p>
              </div>
              <button
                className="button primary"
                onClick={() =>
                  key === "data-quality"
                    ? setToast(
                        "Review a source row to inspect evidence. Live decisions require approved authorization.",
                      )
                    : setDialog({ group: key })
                }
              >
                {key === "data-quality" ? (
                  <Workflow size={17} />
                ) : (
                  <Plus size={17} />
                )}{" "}
                {detail?.action}
              </button>
            </div>
            {key === "attendance" && (
              <>
                <div className="attendance-tabs">
                  <Link
                    className={!pendingView ? "selected" : ""}
                    href="/attendance"
                  >
                    <CheckCircle2 size={17} /> Verified Attendance{" "}
                    <b>{demo.attendance.length}</b>
                  </Link>
                  <Link
                    className={pendingView ? "selected" : ""}
                    href="/attendance/pending"
                  >
                    <Clock3 size={17} /> Pending Attendance Review{" "}
                    <b>{pending.length}</b>
                  </Link>
                </div>
                <div
                  className={
                    "notice " +
                    (pendingView ? "warning-notice" : "success-notice")
                  }
                >
                  {pendingView ? (
                    <AlertTriangle size={18} />
                  ) : (
                    <ShieldCheck size={18} />
                  )}
                  <span>
                    {pendingView
                      ? "Unverified source evidence. Candidate matches and date headers are not approved attendance."
                      : "Only accepted operational records belong here. All displayed examples are synthetic."}
                  </span>
                </div>
              </>
            )}
            {key === "questionnaires" && (
              <div className="notice">
                <FileQuestion size={18} />
                <span>
                  Literal answers and form versions are separate from
                  interpretation. No questionnaire score is calculated.
                </span>
              </div>
            )}
            <section className="panel records-panel">
              <div className="panel-heading">
                <div>
                  <h2>
                    {pendingView
                      ? "Source observations"
                      : key === "data-quality"
                        ? "Open review items"
                        : "All " +
                          (key === "relationships"
                            ? "relationships"
                            : detail?.title.toLowerCase())}{" "}
                    <span className="total-count">{rows.length}</span>
                  </h2>
                  <p>
                    {pendingView
                      ? "Keep the original value and source trace intact."
                      : "Synthetic records for local interface testing."}
                  </p>
                </div>
                <span className="subtle-chip">
                  <View size={13} /> Fixture data
                </span>
              </div>
              <div className="table-toolbar">
                <label className="search-field">
                  <Search size={17} />
                  <input
                    aria-label="Search records"
                    placeholder={
                      pendingView
                        ? "Search source, value or candidate…"
                        : "Search records…"
                    }
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                  />
                  {search && (
                    <button
                      aria-label="Clear search"
                      onClick={() => setSearch("")}
                    >
                      <X size={14} />
                    </button>
                  )}
                </label>
                <select
                  aria-label="Filter programme"
                  value={programme}
                  onChange={(e) => setProgramme(e.target.value)}
                >
                  <option>All programmes</option>
                  {[...new Set(rows.map((r) => r.program))].map((p) => (
                    <option key={p}>{p}</option>
                  ))}
                </select>
                <select
                  aria-label="Filter status"
                  value={status}
                  onChange={(e) => setStatus(e.target.value)}
                >
                  <option>All statuses</option>
                  {[...new Set(rows.map((r) => r.state))].map((s) => (
                    <option key={s} value={s}>
                      {readable(s)}
                    </option>
                  ))}
                </select>
                {key === "attendance" && !pendingView && (
                  <>
                    <input
                      className="date-filter"
                      aria-label="Attendance from date"
                      type="date"
                      value={from}
                      onChange={(e) => setFrom(e.target.value)}
                    />
                    <input
                      className="date-filter"
                      aria-label="Attendance to date"
                      type="date"
                      value={to}
                      onChange={(e) => setTo(e.target.value)}
                    />
                  </>
                )}
              </div>
              <div className="table-scroll">
                <table data-testid="records-table">
                  <thead>
                    <tr>
                      <th
                        aria-sort={
                          sort === "title"
                            ? ascending
                              ? "ascending"
                              : "descending"
                            : "none"
                        }
                      >
                        <button
                          onClick={() => {
                            setSort("title");
                            setAscending(sort === "title" ? !ascending : true);
                          }}
                        >
                          {pendingView || key === "data-quality"
                            ? "Identity / candidates"
                            : "Name / record"}
                          {sort === "title" ? (
                            ascending ? (
                              <ArrowUp size={12} />
                            ) : (
                              <ArrowDown size={12} />
                            )
                          ) : (
                            <ArrowDown size={12} />
                          )}
                        </button>
                      </th>
                      <th>
                        {pendingView
                          ? "Original mark / source header"
                          : key === "relationships"
                            ? "Relationship"
                            : "Programme / context"}
                      </th>
                      <th>
                        {pendingView || key === "data-quality" ? (
                          "Review flags"
                        ) : (
                          <button
                            onClick={() => {
                              setSort("date");
                              setAscending(sort === "date" ? !ascending : true);
                            }}
                          >
                            Date <ArrowDown size={12} />
                          </button>
                        )}
                      </th>
                      <th>Status</th>
                      <th className="action-column">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visible.map((r) => (
                      <tr key={r.id}>
                        <td>
                          <div className="cell-identity">
                            <span
                              className={
                                "person-icon " +
                                (r.kind === "review" ? "source-icon" : "")
                              }
                            >
                              {r.kind === "review" ? (
                                <FileSpreadsheet size={18} />
                              ) : (
                                <UserRound size={18} />
                              )}
                            </span>
                            <div>
                              <strong>{r.title}</strong>
                              <small>
                                {pendingView ? r.subtitle : r.subtitle}
                              </small>
                              {r.source && (
                                <span className="source-ref">{r.source}</span>
                              )}
                            </div>
                          </div>
                        </td>
                        <td>
                          {pendingView ? (
                            <>
                              <code className="raw-mark">{r.mark}</code>
                              <small className="cell-caption">
                                {pending.find((p) => p.id === r.id)
                                  ?.original_header ?? "Missing header"}
                              </small>
                            </>
                          ) : key === "relationships" ? (
                            <span className="subtle-chip">
                              <Link2 size={13} /> Explicit demo IDs
                            </span>
                          ) : (
                            r.program
                          )}
                        </td>
                        <td>
                          {r.kind === "review" ? (
                            <div className="flags">
                              {r.flags?.map((f) => (
                                <span key={f}>
                                  <AlertTriangle size={11} />
                                  {readable(f)}
                                </span>
                              ))}
                            </div>
                          ) : (
                            (r.date ?? (
                              <span className="missing-date">Not recorded</span>
                            ))
                          )}
                        </td>
                        <td>
                          <Badge state={r.state} />
                        </td>
                        <td>
                          <button
                            className="row-action"
                            aria-label={
                              (r.kind === "review" ? "Review " : "Edit ") +
                              r.title
                            }
                            onClick={() =>
                              setDialog({
                                group: r.kind === "review" ? "review" : key,
                                row: r,
                              })
                            }
                          >
                            {r.kind === "review" ? "Review" : "Edit"}
                            <ArrowUpRight size={13} />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!visible.length && (
                  <div className="empty-state">
                    <Search size={25} />
                    <h3>No matching records</h3>
                    <p>Try a different search or clear your filters.</p>
                    <button
                      className="button secondary"
                      onClick={() => {
                        setSearch("");
                        setProgramme("All programmes");
                        setStatus("All statuses");
                        setFrom("");
                        setTo("");
                      }}
                    >
                      Clear filters
                    </button>
                  </div>
                )}
              </div>
              <footer className="pagination">
                <span>
                  Showing{" "}
                  {filtered.length
                    ? (Math.min(page, pageCount) - 1) * pageSize + 1
                    : 0}
                  –
                  {Math.min(
                    Math.min(page, pageCount) * pageSize,
                    filtered.length,
                  )}{" "}
                  of {filtered.length} records
                </span>
                <div>
                  <button
                    aria-label="Previous page"
                    disabled={page <= 1}
                    onClick={() => setPage((p) => p - 1)}
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <span>
                    Page {Math.min(page, pageCount)} of {pageCount}
                  </span>
                  <button
                    aria-label="Next page"
                    disabled={page >= pageCount}
                    onClick={() => setPage((p) => p + 1)}
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              </footer>
            </section>
            {["adl", "support", "caregivers"].includes(key) && (
              <p className="page-footnote">
                <LockKeyhole size={13} /> Live restricted access has not been
                activated. This view contains synthetic examples only.
              </p>
            )}
          </>
        )}
        <footer className="workspace-footer">
          <span>Goalkeep · Kickstarter Cohort 2</span>
          <span>Local preview · no remote writes</span>
        </footer>
      </main>
      {toast && (
        <div role="status" className="toast">
          <CheckCircle2 size={18} />
          {toast}
          <button
            aria-label="Dismiss notification"
            onClick={() => setToast("")}
          >
            <X size={15} />
          </button>
        </div>
      )}
      {dialog && (
        <DemoDialog
          state={dialog}
          onClose={() => setDialog(null)}
          onSave={save}
          childrenOptions={children}
          caregiverOptions={caregivers}
          note={
            pending.find((p) => p.id === dialog.row?.id)?.review_notes ?? ""
          }
          pendingRecord={pending.find((p) => p.id === dialog.row?.id)}
        />
      )}
    </div>
  );
}
