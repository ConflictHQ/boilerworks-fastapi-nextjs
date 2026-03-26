"use client";

import { useEffect, useState } from "react";
import { getProducts, type Product } from "@/lib/api";
import Link from "next/link";

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      getProducts(search).then((res) => {
        if (res.ok && res.data) setProducts(res.data);
        setLoading(false);
      });
    }, 300);
    return () => clearTimeout(timer);
  }, [search]);

  return (
    <div className="max-w-6xl mx-auto p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Products</h1>
        <Link href="/" className="text-sm text-indigo-600 hover:text-indigo-800">&larr; Dashboard</Link>
      </div>

      <input
        type="search"
        placeholder="Search products..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="w-full max-w-md rounded-md border-gray-300 shadow-sm p-2 border mb-4"
      />

      {loading ? (
        <p className="text-gray-500">Loading...</p>
      ) : (
        <div className="overflow-hidden rounded-lg border bg-white shadow-sm">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">SKU</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase text-gray-500">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {products.map((p) => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-indigo-600">{p.name}</td>
                  <td className="px-6 py-4 text-sm text-gray-500">{p.sku || "—"}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">${p.price}</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`inline-flex rounded-full px-2 text-xs font-semibold ${p.is_active ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}`}>
                      {p.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                </tr>
              ))}
              {products.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-sm text-gray-500">No products found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
