"use client";

import { StatusBadge, type Column } from "@calliopelabs/ui";
import { usePaginatedQuery } from "@/hooks/use-paginated-query";
import { getItems } from "./items.queries";
import type { Item, ItemEdge, ItemsQueryData, ItemsQueryVariables } from "./items.types";

// ─── columns ──────────────────────────────────────────────────────────────────

const price = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

export const itemColumns: Column<Item>[] = [
  { id: "name", header: "Name", cell: (row) => <span className="font-medium">{row.name}</span> },
  { id: "sku", header: "SKU", cell: (row) => <span className="font-mono">{row.sku ?? "-"}</span> },
  {
    id: "price",
    header: "Price",
    align: "right",
    cell: (row) => price.format(Number(row.price)),
  },
  {
    id: "status",
    header: "Status",
    cell: (row) => (
      <StatusBadge tone={row.isActive ? "ok" : "muted"}>
        {row.isActive ? "Active" : "Inactive"}
      </StatusBadge>
    ),
  },
];

// ─── hook ─────────────────────────────────────────────────────────────────────

/** The items query, paged and searched (by name) on the server, newest first. */
export const useItems = (perPage?: number) =>
  usePaginatedQuery<ItemsQueryVariables, ItemsQueryData, ItemEdge, Item>({
    query: getItems,
    variables: {},
    ancestor: "items",
    dataExtractor: (edges) => edges.map((e) => e.node),
    perPage,
    storageKey: "items-per-page",
    fetchPolicy: "cache-and-network",
    urlSync: "item",
  });
