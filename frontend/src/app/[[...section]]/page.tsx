import { notFound } from "next/navigation";
import Workspace from "@/components/workspace";
export const dynamic = "force-dynamic";
export default async function Page({
  params,
}: {
  params: Promise<{ section?: string[] }>;
}) {
  const { section = [] } = await params;
  const route = "/" + section.join("/");
  if (
    ![
      "/",
      "/children",
      "/caregivers",
      "/relationships",
      "/questionnaires",
      "/attendance",
      "/attendance/pending",
      "/adl",
      "/support",
      "/data-quality",
      "/login",
      "/access-pending",
    ].includes(route)
  )
    notFound();
  return <Workspace route={route} />;
}
