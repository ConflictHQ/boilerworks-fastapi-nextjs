import { PageHeader } from "@calliopelabs/ui";
import { Suspense } from "react";
import { Separator } from "@/ui-app/primitives/separator";
import { DataTable1 } from "@/components/DataTable1";
import { DataTableItems } from "@/components/DataTableItems";

export default function TablePage() {
  return (
    <div className="flex flex-1 flex-col gap-6 p-6">
      <PageHeader title="Items" description="Browse and manage your item inventory." />
      <Separator />
      <DataTable1 />
      <Separator />
      <div>
        <h2 className="text-lg font-semibold">Server-side paginated (GraphQL)</h2>
        <p className="text-muted-foreground mt-1 text-sm">
          Live data from the GraphQL API with server-side pagination and search.
        </p>
      </div>
      <Suspense>
        <DataTableItems />
      </Suspense>
    </div>
  );
}
