"use client";

import { useEffect, useState } from "react";
import { getMe } from "@/lib/api";
import Link from "next/link";

export default function Home() {
  const [user, setUser] = useState<{ username: string } | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMe().then((res) => {
      if (res.ok) setUser(res.data as { username: string });
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="p-8 text-gray-500">Loading...</div>;

  if (!user) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Boilerworks</h1>
          <p className="text-gray-600 mb-6">FastAPI + Next.js template</p>
          <Link href="/login" className="rounded-md bg-indigo-600 px-6 py-3 text-white font-semibold hover:bg-indigo-500">
            Sign In
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <span className="text-sm text-gray-500">Welcome, {user.username}</span>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link href="/products" className="block rounded-lg border bg-white p-6 shadow-sm hover:shadow-md">
          <h3 className="text-lg font-semibold text-gray-900">Products</h3>
          <p className="mt-2 text-sm text-gray-500">Manage the product catalogue.</p>
        </Link>
      </div>
    </div>
  );
}
