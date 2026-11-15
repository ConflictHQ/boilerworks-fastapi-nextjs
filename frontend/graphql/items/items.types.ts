// Manual types for the items domain.
// Once GraphQL Codegen is configured, replace these with imports from __generated__/graphql.ts

export type Item = {
  id: string;
  name: string;
  sku: string | null;
  /** A decimal, as the API returns it. */
  price: string;
  isActive: boolean;
  createdAt: string;
};

export type ItemEdge = {
  cursor: string;
  node: Item;
};

export type ItemsQueryData = {
  items: {
    edges: ItemEdge[];
    totalCount: number;
    pageInfo: {
      hasNextPage: boolean;
    };
  } | null;
};

export type ItemsQueryVariables = {
  first?: number;
  offset?: number;
  search?: string;
};
