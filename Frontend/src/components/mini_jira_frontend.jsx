import React, { useEffect, useMemo, useRef, useState } from "react";
import.meta.env.VITE_MINI_JIRA_API

// UI libs (available in this environment). If your project doesn't use shadcn/ui yet,
// you can replace these with plain HTML elements or install shadcn/ui.
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Loader2, Send, RefreshCw, Trash2, Plus, Database, ListChecks, UserPlus } from "lucide-react";
import { motion } from "framer-motion";

// -----------------------------------------------------------------------------
// ⚙️ CONFIG — point this to your tiny HTTP bridge to the LangGraph CLI agent
// -----------------------------------------------------------------------------
// By default we look at the same origin. Override with VITE/ENV var if needed.
const BASE_URL = (import.meta?.env?.VITE_MINI_JIRA_API || process.env?.VITE_MINI_JIRA_API || "").trim() || "";

// Expected minimal API (implement a tiny FastAPI/Flask bridge that shells out to your CLI or calls your LangGraph functions directly):
// POST   /api/chat                 { message: string }                 -> { reply: string, steps?: any }
// GET    /api/users                                                    -> { users: Array<{user_id:number,name:string}> }
// POST   /api/users                { user_id:number, name:string }     -> { ok: true }
// DELETE /api/users/:user_id                                           -> { ok: true }
// GET    /api/tickets?status=OPEN|CLOSED|IN_PROGRESS|ALL              -> { tickets: Ticket[] }
// POST   /api/tickets              { title:string, assignee:string }   -> { ok: true }
// PATCH  /api/tickets/:id          { status:"OPEN"|"CLOSED"|"IN_PROGRESS" } -> { ok: true }
// DELETE /api/tickets/:id                                             -> { ok: true }
// POST   /api/reset                                                    -> { ok: true }

// Types
/** @typedef {{ id:number, title:string, assignee:string, status:"OPEN"|"IN_PROGRESS"|"CLOSED" }} Ticket */

function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function api(path, options = {}) {
    setError("");
    setLoading(true);
    try {
      const res = await fetch((BASE_URL ? BASE_URL : "") + path, {
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        ...options,
      });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      return await res.json();
    } catch (e) {
      setError(e.message || String(e));
      throw e;
    } finally {
      setLoading(false);
    }
  }

  return { api, loading, error, setError };
}

function StatusBadge({ s }) {
  const map = {
    OPEN: "bg-emerald-100 text-emerald-700",
    IN_PROGRESS: "bg-amber-100 text-amber-800",
    CLOSED: "bg-red-100 text-red-700",
  };
  return <Badge className={`rounded-xl ${map[s] || ""}`}>{s.replace("_", " ")}</Badge>;
}

function SectionHeader({ icon: Icon, title, children, right }) {
  return (
    <div className="flex items-center justify-between mb-3">
      <div className="flex items-center gap-2">
        {Icon && <Icon className="w-5 h-5" />}
        <h3 className="text-xl font-semibold">{title}</h3>
      </div>
      {right}
      {children}
    </div>
  );
}

function EmptyState({ title, hint }) {
  return (
    <div className="text-center text-sm text-muted-foreground py-8">
      <p className="font-medium text-base">{title}</p>
      {hint && <p className="mt-1">{hint}</p>}
    </div>
  );
}

// -----------------------------------------------------------------------------
// 🗨️ Chat Panel — send natural‑language commands to the agent
// -----------------------------------------------------------------------------
function ChatPanel() {
  const { api, loading, error, setError } = useApi();
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: "assistant", text: "Hi! I can manage your mini‑Jira. Try: 'create ticket Login for Alice'" },
  ]);
  const listRef = useRef(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", text: input.trim() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    try {
      const data = await api("/api/chat", { method: "POST", body: JSON.stringify({ message: userMsg.text }) });
      setMessages((m) => [...m, { role: "assistant", text: data.reply || JSON.stringify(data) }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", text: `⚠️ ${error || "Failed to reach backend"}` }]);
    }
  };

  return (
    <Card className="w-full h-full flex flex-col">
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><ListChecks className="w-5 h-5"/> Chat with Admin Agent</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col">
        <div ref={listRef} className="flex-1 overflow-auto rounded-xl border p-3 bg-muted/30">
          {messages.map((m, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} className="mb-3">
              <div className="text-xs text-muted-foreground mb-1">{m.role === "user" ? "You" : "Agent"}</div>
              <div className={`p-3 rounded-2xl shadow-sm ${m.role === "user" ? "bg-white" : "bg-slate-50"}`}>
                <pre className="whitespace-pre-wrap break-words text-sm">{m.text}</pre>
              </div>
            </motion.div>
          ))}
        </div>
        <div className="mt-3 flex gap-2">
          <Textarea value={input} onChange={(e)=>setInput(e.target.value)} placeholder="e.g., create ticket Login for Alice" className="min-h-[60px]"/>
          <Button onClick={send} disabled={loading} className="self-end h-[60px]">
            {loading ? <Loader2 className="w-4 h-4 animate-spin"/> : <Send className="w-4 h-4"/>}
          </Button>
        </div>
        {!!error && (
          <div className="mt-2 text-xs text-red-600">{error} — Is your bridge server running?</div>
        )}
      </CardContent>
    </Card>
  );
}

// -----------------------------------------------------------------------------
// 👤 Users Panel — CRUD on users
// -----------------------------------------------------------------------------
function UsersPanel() {
  const { api, loading, error, setError } = useApi();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState({ user_id: "", name: "" });

  const load = async () => {
    try {
      const data = await api("/api/users");
      setUsers(data.users || []);
    } catch {}
  };
  useEffect(() => { load(); }, []);

  const add = async (e) => {
    e?.preventDefault();
    if (!form.user_id || !form.name) return;
    await api("/api/users", { method: "POST", body: JSON.stringify({ user_id: Number(form.user_id), name: form.name }) });
    setForm({ user_id: "", name: "" });
    await load();
  };

  const del = async (uid) => {
    await api(`/api/users/${uid}`, { method: "DELETE" });
    await load();
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><UserPlus className="w-5 h-5"/> Manage Users</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={add} className="grid grid-cols-1 md:grid-cols-3 gap-2 mb-3">
          <Input type="number" placeholder="User ID" value={form.user_id} onChange={(e)=>setForm(f=>({...f,user_id:e.target.value}))} />
          <Input placeholder="Name" value={form.name} onChange={(e)=>setForm(f=>({...f,name:e.target.value}))} />
          <Button type="submit" disabled={loading}><Plus className="w-4 h-4 mr-1"/> Add User</Button>
        </form>

        <div className="rounded-xl border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead className="w-24 text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {users.length === 0 && (
                <TableRow><TableCell colSpan={3}><EmptyState title="No users yet" hint="Create your first user above."/></TableCell></TableRow>
              )}
              {users.map(u => (
                <TableRow key={u.user_id}>
                  <TableCell>{u.user_id}</TableCell>
                  <TableCell>{u.name}</TableCell>
                  <TableCell className="text-right">
                    <Button variant="ghost" size="icon" onClick={()=>del(u.user_id)} title="Delete">
                      <Trash2 className="w-4 h-4"/>
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {!!error && <div className="mt-2 text-xs text-red-600">{error}</div>}
      </CardContent>
    </Card>
  );
}

// -----------------------------------------------------------------------------
// 🎫 Tickets Panel — create/list/update/delete/reset
// -----------------------------------------------------------------------------
function TicketsPanel() {
  const { api, loading, error } = useApi();
  const [tickets, setTickets] = useState(/** @type {Ticket[]} */([]));
  const [status, setStatus] = useState("OPEN");
  const [form, setForm] = useState({ title: "", assignee: "" });

  const load = async () => {
    const data = await api(`/api/tickets?status=${encodeURIComponent(status)}`);
    setTickets(data.tickets || []);
  };
  useEffect(() => { load(); }, [status]);

  const create = async (e) => {
    e?.preventDefault();
    if (!form.title || !form.assignee) return;
    await api("/api/tickets", { method: "POST", body: JSON.stringify(form) });
    setForm({ title: "", assignee: "" });
    await load();
  };

  const updateStatus = async (id, s) => {
    await api(`/api/tickets/${id}`, { method: "PATCH", body: JSON.stringify({ status: s }) });
    await load();
  };

  const del = async (id) => {
    await api(`/api/tickets/${id}`, { method: "DELETE" });
    await load();
  };

  const reset = async () => {
    await api(`/api/reset`, { method: "POST" });
    await load();
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2"><Database className="w-5 h-5"/> Tickets</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={create} className="grid grid-cols-1 md:grid-cols-4 gap-2 mb-3">
          <Input placeholder="Ticket title" value={form.title} onChange={(e)=>setForm(f=>({...f,title:e.target.value}))} />
          <Input placeholder="Assignee (name)" value={form.assignee} onChange={(e)=>setForm(f=>({...f,assignee:e.target.value}))} />
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger><SelectValue placeholder="Filter status"/></SelectTrigger>
            <SelectContent>
              <SelectItem value="ALL">All</SelectItem>
              <SelectItem value="OPEN">OPEN</SelectItem>
              <SelectItem value="IN_PROGRESS">IN_PROGRESS</SelectItem>
              <SelectItem value="CLOSED">CLOSED</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex gap-2">
            <Button type="submit" className="flex-1"><Plus className="w-4 h-4 mr-1"/> Create</Button>
            <Button type="button" variant="secondary" onClick={reset} className="flex-1"><RefreshCw className="w-4 h-4 mr-1"/> Reset DB</Button>
          </div>
        </form>

        <div className="rounded-xl border overflow-hidden">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-16">ID</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Assignee</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right w-48">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tickets.length === 0 && (
                <TableRow><TableCell colSpan={5}><EmptyState title="No tickets" hint="Create one above or use the Chat tab."/></TableCell></TableRow>
              )}
              {tickets.map(t => (
                <TableRow key={t.id}>
                  <TableCell>{t.id}</TableCell>
                  <TableCell className="max-w-[320px]"><div className="truncate" title={t.title}>{t.title}</div></TableCell>
                  <TableCell>{t.assignee}</TableCell>
                  <TableCell><StatusBadge s={t.status}/></TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-1">
                      <Select onValueChange={(v)=>updateStatus(t.id, v)}>
                        <SelectTrigger className="w-40"><SelectValue placeholder="Set status"/></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="OPEN">Set OPEN</SelectItem>
                          <SelectItem value="IN_PROGRESS">Set IN_PROGRESS</SelectItem>
                          <SelectItem value="CLOSED">Set CLOSED</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button variant="ghost" size="icon" onClick={()=>del(t.id)} title="Delete ticket">
                        <Trash2 className="w-4 h-4"/>
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>

        {!!error && <div className="mt-2 text-xs text-red-600">{error}</div>}
      </CardContent>
    </Card>
  );
}

// -----------------------------------------------------------------------------
// 🧩 Root App — Tabs for Chat / Tickets / Users
// -----------------------------------------------------------------------------
export default function MiniJiraFrontend() {
  return (
    <div className="min-h-screen w-full bg-gradient-to-b from-slate-50 to-white text-slate-900 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <motion.h1 initial={{ opacity:0, y:6 }} animate={{ opacity:1, y:0 }} transition={{ duration:0.4 }} className="text-3xl md:text-4xl font-bold tracking-tight mb-1">
          Mini‑Jira Admin — Web UI
        </motion.h1>
        <p className="text-sm text-muted-foreground mb-6">
          A lightweight React front‑end for your LangGraph + SQLite admin agent. Configure <code>VITE_MINI_JIRA_API</code> to point at your HTTP bridge.
        </p>

        <Tabs defaultValue="chat" className="w-full">
          <TabsList className="grid grid-cols-3 w-full md:w-[520px]">
            <TabsTrigger value="chat">Chat</TabsTrigger>
            <TabsTrigger value="tickets">Tickets</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
          </TabsList>

          <TabsContent value="chat" className="mt-4">
            <ChatPanel/>
          </TabsContent>

          <TabsContent value="tickets" className="mt-4">
            <TicketsPanel/>
          </TabsContent>

          <TabsContent value="users" className="mt-4">
            <UsersPanel/>
          </TabsContent>
        </Tabs>
          
        </div>
      </div>
  );
}
