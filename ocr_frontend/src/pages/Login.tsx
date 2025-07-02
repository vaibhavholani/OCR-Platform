import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { User } from "../types/document";

const API_URL = "http://localhost:5000/api/users/";

const Login: React.FC = () => {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch(API_URL + "login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Login failed");
      localStorage.setItem("user_id", String(data.user.user_id));
      navigate("/");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <h1 className="text-3xl font-bold mb-6">Login</h1>
      <form
        onSubmit={handleLogin}
        className="flex flex-col w-80 p-6 border rounded shadow"
      >
        <input
          className="mb-2 p-2 border rounded"
          type="email"
          name="email"
          placeholder="Email"
          value={form.email}
          onChange={handleChange}
          required
        />
        <input
          className="mb-4 p-2 border rounded"
          type="password"
          name="password"
          placeholder="Password"
          value={form.password}
          onChange={handleChange}
          required
        />
        {error && <div className="text-red-500 mb-2">{error}</div>}
        <button className="bg-blue-600 text-white py-2 rounded" type="submit">
          Login
        </button>
      </form>
      <button
        className="mt-4 text-blue-500 underline"
        onClick={() => navigate("/signup")}
      >
        Don't have an account? Sign Up
      </button>
    </div>
  );
};

export default Login;
