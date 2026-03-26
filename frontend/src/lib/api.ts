const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export interface ApiResponse<T = unknown> {
  ok: boolean;
  data: T | null;
  errors: Array<{ detail: string }> | null;
}

export async function apiFetch<T = unknown>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  const res = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  return res.json();
}

export async function login(username: string, password: string) {
  return apiFetch("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });
}

export async function logout() {
  return apiFetch("/api/auth/logout", { method: "POST" });
}

export async function getMe() {
  return apiFetch("/api/auth/me");
}

export interface Product {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  price: string;
  sku: string | null;
  is_active: boolean;
  created_at: string;
}

export async function getProducts(search = "") {
  const q = search ? `?search=${encodeURIComponent(search)}` : "";
  return apiFetch<Product[]>(`/api/products${q}`);
}

export async function createProduct(data: {
  name: string;
  price: string;
  description?: string;
  sku?: string;
}) {
  return apiFetch<Product>("/api/products", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
