import { create } from 'zustand';

interface UIState {
  packages: PackageMeta[];
  selectedPackage: string | null;
  actions: {
    addPackages: (pkg: PackageMeta[]) => void;
    selectPackage: (id: string) => void;
    deselectPackage: (id: string) => void;
  };
}

const useUIStore = create<UIState>()((set) => ({
  packages: [],
  selectedPackage: null,
  actions: {
    // Adds a package to the store
    addPackages: (pkgs) =>
      set((state) => ({
        packages: [...state.packages, ...pkgs],
      })),

    // Sets the selectedPackage to the given id
    selectPackage: (id) =>
      set((state) => {
        if (state.selectedPackage === id) return { selectedPackage: null };
        return {};
      }),

    // Sets the selectedPackage to null
    deselectPackage: () =>
      set(() => ({
        selectedPackage: null,
      })),
  },
}));

// Returns if the package is selected
export const useIsSelected = (packageId: string) =>
  useUIStore((state) => state.selectedPackage !== packageId);

// Returns the selected package
export const useSelectedPackage = () =>
  useUIStore((state) => state.selectedPackage);

// One selector for all our actions as they are not techincally "state"
export const useUIActions = () => useUIStore((state) => state.actions);
