import { create } from 'zustand';

interface ProblemDataState {
  incompatiblePackages: Record<string, string[]>;
  incompatibleUlds: Record<string, string[]>;
  unstackableFaces: Record<string, string[]>;
  heavyPackages: Set<string>;
  fragilePackages: Set<string>;

  actions: {
    setIncompatiblePackages: (id: string, packIds: string[]) => void;
    setIncompatibleUlds: (id: string, uldIds: string[]) => void;
    setUnstackableFaces: (id: string, faces: string[]) => void;
    toggleHeavyPackage: (id: string) => void;
    toggleFragilePackage: (id: string) => void;
  };
}

const usePackageDataStore = create<ProblemDataState>()((set) => ({
  incompatiblePackages: {},
  incompatibleUlds: {},
  unstackableFaces: {},
  heavyPackages: new Set(),
  fragilePackages: new Set(),

  actions: {
    setIncompatiblePackages: (id: string, packIds: string[]) =>
      set((state) => ({
        incompatiblePackages: {
          ...state.incompatiblePackages,
          [id]: packIds,
        },
      })),

    setIncompatibleUlds(id: string, uldIds: string[]) {
      set((state) => ({
        incompatibleUlds: {
          ...state.incompatibleUlds,
          [id]: uldIds,
        },
      }));
    },

    setUnstackableFaces(id: string, faces: string[]) {
      set((state) => ({
        unstackableFaces: {
          ...state.unstackableFaces,
          [id]: faces,
        },
      }));
    },

    toggleHeavyPackage(id: string) {
      set((state) => {
        const heavyPackages = new Set(state.heavyPackages);
        if (heavyPackages.has(id)) heavyPackages.delete(id);
        else heavyPackages.add(id);

        return { heavyPackages };
      });
    },

    toggleFragilePackage(id: string) {
      set((state) => {
        const fragilePackages = new Set(state.fragilePackages);
        if (fragilePackages.has(id)) fragilePackages.delete(id);
        else fragilePackages.add(id);

        return { fragilePackages };
      });
    },
  },
}));

export const usePackageDataActions = () =>
  usePackageDataStore((state) => state.actions);

export const getIncompatiblePackages = (id: string) =>
  usePackageDataStore((state) => state.incompatiblePackages[id]);

export const getIncompatibleUlds = (id: string) =>
  usePackageDataStore((state) => state.incompatibleUlds[id]);

export const getUnstackableFaces = (id: string) =>
  usePackageDataStore((state) => state.unstackableFaces[id]);

export const getIsHeavyPackage = (id: string) =>
  usePackageDataStore((state) => state.heavyPackages.has(id));

export const getIsFragilePackage = (id: string) =>
  usePackageDataStore((state) => state.fragilePackages.has(id));
