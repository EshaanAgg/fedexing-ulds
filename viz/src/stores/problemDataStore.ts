import { create } from 'zustand';
import {
  type PackageData,
  type ULDData,
  type PackingResult,
  getProcessedULDs,
} from '../utils/dataConvert';

interface ProblemDataState {
  packages: PackageData[];
  ulds: ULDData[];
  packingResults: PackingResult[];
  processedUlds: ULDMeta[];

  actions: {
    setProblemData: (data: {
      packages: PackageData[];
      ulds: ULDData[];
      packingResults: PackingResult[];
      processedUlds: ULDMeta[];
    }) => void;

    setPackageAndUldData(packages: PackageData[], ulds: ULDData[]): void;
    setPackingResults(packingResults: PackingResult[]): void;
    calculateProcessedUlds(): void;
  };
}

const useProblemDataStore = create<ProblemDataState>()((set) => ({
  packages: [],
  ulds: [],
  packingResults: [],
  processedUlds: [],

  actions: {
    setProblemData: (data: {
      packages: PackageData[];
      ulds: ULDData[];
      packingResults: PackingResult[];
      processedUlds: ULDMeta[];
    }) =>
      set(() => ({
        packages: data.packages,
        ulds: data.ulds,
        packingResults: data.packingResults,
        processedUlds: data.processedUlds,
      })),

    setPackageAndUldData: (packages, ulds) =>
      set(() => ({
        packages,
        ulds,
      })),

    setPackingResults: (packingResults) =>
      set(() => ({
        packingResults,
      })),

    calculateProcessedUlds: () => {
      set((state) => ({
        processedUlds: getProcessedULDs({
          packages: state.packages,
          ulds: state.ulds,
          packingResults: state.packingResults,
        }),
      }));
    },
  },
}));

export const useProblemDataActions = () =>
  useProblemDataStore((state) => state.actions);

export const useProcessedUlds = () =>
  useProblemDataStore((state) => state.processedUlds);

export const usePackages = () => useProblemDataStore((state) => state.packages);
export const useUlds = () => useProblemDataStore((state) => state.ulds);
export const usePackingResults = () =>
  useProblemDataStore((state) => state.packingResults);
