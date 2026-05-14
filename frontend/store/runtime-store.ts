import { create } from "zustand";

type RuntimeState = {
  logs: string[];
  setLogs: (logs: string[]) => void;
  appendLogs: (logs: string[]) => void;
};

export const useRuntimeStore = create<RuntimeState>((set) => ({
  logs: [],
  setLogs: (logs) => set({ logs }),
  appendLogs: (logs) => set((state) => ({ logs: [...state.logs, ...logs] }))
}));
