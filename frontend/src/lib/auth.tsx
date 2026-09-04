import { createContext, useContext, useState, ReactNode } from "react";
import { api, getStoredUser, setStoredUser, clearStoredUser, StoredUser } from "./api";

interface AuthContextValue {
  user: StoredUser | null;
  loginCandidate: (email: string, password: string) => Promise<void>;
  loginEmployer: (email: string, password: string) => Promise<void>;
  signupCandidate: (fullName: string, email: string, password: string) => Promise<void>;
  signupEmployer: (companyName: string, email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<StoredUser | null>(getStoredUser);

  function persist(u: StoredUser) {
    setStoredUser(u);
    setUser(u);
  }

  async function loginCandidate(email: string, password: string) {
    const res = await api.login({ email, password });
    if (res.role !== "candidate") throw new Error("This is an employer account — use the employer login instead.");
    persist({ token: res.access_token, role: res.role, id: res.id, email });
  }

  async function loginEmployer(email: string, password: string) {
    const res = await api.login({ email, password });
    if (res.role !== "employer") throw new Error("This is a candidate account — use the candidate login instead.");
    persist({ token: res.access_token, role: res.role, id: res.id, email });
  }

  async function signupCandidate(fullName: string, email: string, password: string) {
    const res = await api.signupCandidate({ full_name: fullName, email, password });
    persist({ token: res.access_token, role: res.role, id: res.id, email, fullName });
  }

  async function signupEmployer(companyName: string, email: string, password: string) {
    const res = await api.signupEmployer({ company_name: companyName, email, password });
    persist({ token: res.access_token, role: res.role, id: res.id, email, fullName: companyName });
  }

  function logout() {
    clearStoredUser();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loginCandidate, loginEmployer, signupCandidate, signupEmployer, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
