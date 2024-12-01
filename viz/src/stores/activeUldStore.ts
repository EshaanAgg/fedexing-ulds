import { create } from 'zustand';

interface ActiveUldState {
  activeUld: string | null;

  actions: {
    activateUld: (uldId: string) => void;
    deactivateUld: () => void;
  };
}

const useProblemDataStore = create<ActiveUldState>()((set) => ({
  activeUld: null,

  actions: {
    activateUld: (uldId: string) => set(() => ({ activeUld: uldId })),
    deactivateUld: () => set(() => ({ activeUld: null })),
  },
}));

export const useActiveUld = () =>
  useProblemDataStore((state) => state.activeUld);

export const useActiveUldActions = () =>
  useProblemDataStore((state) => state.actions);
