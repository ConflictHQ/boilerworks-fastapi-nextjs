import { gql } from "@apollo/client";

export const getItems = gql`
  query Items($first: Int, $offset: Int, $search: String) {
    items(first: $first, offset: $offset, search: $search) {
      totalCount
      edges {
        cursor
        node {
          id
          name
          sku
          price
          isActive
          createdAt
        }
      }
      pageInfo {
        hasNextPage
      }
    }
  }
`;
