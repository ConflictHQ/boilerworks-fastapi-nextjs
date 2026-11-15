"use client";

import { DataTable } from "@calliopelabs/ui";
import { itemColumns, useItems } from "@/graphql/items/items.hooks";
import { paginatedController } from "@/ui-app/table/paginated-controller";

/** A server-paged table: GraphQL pages and searches, the library DataTable draws. */
export function DataTableItems() {
  const items = useItems();

  return (
    <DataTable
      label="Items"
      controller={paginatedController(items)}
      columns={itemColumns}
      getRowId={(row) => row.id}
      searchPlaceholder="Search items by name…"
      empty={{ title: "No items yet", description: "Create one through the API to see it here." }}
    />
  );
}
