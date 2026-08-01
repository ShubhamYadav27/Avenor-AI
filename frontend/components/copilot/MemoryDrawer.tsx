"use client";

import React, { useEffect, useState } from "react";
import { Brain, Plus, RefreshCw, X, Tag, Shield } from "lucide-react";

interface MemoryItem {
  id: string;
  category: string;
  tier: string;
  content: string;
  confidence_score: number;
  importance: string;
  citation_id: string;
  created_at: string;
}

interface MemoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const MemoryDrawer: React.FC<MemoryDrawerProps> = ({ isOpen, onClose }) => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [newContent, setNewContent] = useState("");
  const [category, setCategory] = useState("workspace");
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const fetchMemories = async () => {
    setIsLoading(true);
    try {
      const res = await fetch("/api/v1/copilot/memories");
      if (res.ok) {
        const data = await res.json();
        setMemories(data || []);
      }
    } catch {
      // Fallback baseline display
      setMemories([
        {
          id: "mem-seed-1",
          category: "workspace",
          tier: "long_term",
          content: "Workspace strategy: Prioritize high-intent Tier 1 accounts with recent hiring triggers.",
          confidence_score: 1.0,
          importance: "CRITICAL",
          citation_id: "cit-mem-seed-1",
          created_at: new Date().toISOString(),
        },
        {
          id: "mem-seed-2",
          category: "knowledge",
          tier: "semantic",
          content: "Avenor Playbook: Respond to objection on price by proving 10x ROI via buying signal velocity.",
          confidence_score: 0.95,
          importance: "HIGH",
          citation_id: "cit-mem-seed-2",
          created_at: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newContent.trim()) return;

    setIsSaving(true);
    try {
      await fetch(`/api/v1/copilot/memories?content=${encodeURIComponent(newContent)}&category=${category}`, {
        method: "POST",
      });
      setNewContent("");
      await fetchMemories();
    } catch {
      // Ignore
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchMemories();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-gray-900 border-l border-gray-800 shadow-2xl z-50 flex flex-col p-5">
      <div className="flex items-center justify-between pb-4 border-b border-gray-800">
        <div className="flex items-center space-x-2 text-indigo-400">
          <Brain className="w-5 h-5" />
          <h2 className="font-semibold text-gray-100 text-base">Enterprise Memory</h2>
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-200">
          <X className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleSaveMemory} className="py-3 border-b border-gray-800 space-y-2">
        <textarea
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          placeholder="Store strategic note or playbook rule..."
          rows={2}
          className="w-full bg-gray-950 border border-gray-800 rounded-lg p-2 text-xs text-gray-200 focus:outline-none focus:border-indigo-500"
        />
        <div className="flex items-center justify-between">
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="bg-gray-950 border border-gray-800 text-[11px] text-gray-300 rounded px-2 py-1 focus:outline-none"
          >
            <option value="workspace">Workspace</option>
            <option value="company">Company</option>
            <option value="user">User Strategy</option>
            <option value="knowledge">Knowledge</option>
          </select>
          <button
            type="submit"
            disabled={isSaving}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-xs flex items-center gap-1 font-medium transition-colors"
          >
            <Plus className="w-3.5 h-3.5" /> Save Memory
          </button>
        </div>
      </form>

      <div className="py-2 flex items-center justify-between text-xs text-gray-400">
        <span>Stored Memories ({memories.length})</span>
        <button onClick={fetchMemories} className="hover:text-indigo-400 flex items-center gap-1">
          <RefreshCw className={`w-3 h-3 ${isLoading ? "animate-spin" : ""}`} /> Refresh
        </button>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {memories.map((mem) => (
          <div key={mem.id} className="p-3 bg-gray-950/80 rounded-lg border border-gray-800 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-indigo-950/60 border border-indigo-800/60 text-indigo-300 flex items-center gap-1">
                <Tag className="w-2.5 h-2.5" />
                {mem.category}
              </span>
              <span className="text-[10px] text-emerald-400 font-mono flex items-center gap-1">
                <Shield className="w-2.5 h-2.5" />
                {(mem.confidence_score * 100).toFixed(0)}% Conf
              </span>
            </div>
            <p className="text-xs text-gray-200 leading-relaxed">{mem.content}</p>
            <div className="text-[10px] text-gray-500 font-mono pt-1 border-t border-gray-900">
              Citation: {mem.citation_id}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
