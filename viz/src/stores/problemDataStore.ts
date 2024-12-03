import { create } from 'zustand';
import type { PackageData, ULDData, PackingResult } from '../utils/dataConvert';

interface ProblemDataState {
  packages: PackageData[];
  ulds: ULDData[];
  packingResults: PackingResult[];
  processedUlds: ULDMeta[];
  dataAvailable: boolean;

  actions: {
    setProblemData: (data: {
      packages: PackageData[];
      ulds: ULDData[];
      packingResults: PackingResult[];
      processedUlds: ULDMeta[];
    }) => void;
  };
}

const useProblemDataStore = create<ProblemDataState>()((set) => ({
  packages: [],
  ulds: [],
  packingResults: [],
  processedUlds: [],
  dataAvailable: false,

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
        dataAvailable: true,
      })),
  },
}));

export const useProblemDataActions = () =>
  useProblemDataStore((state) => state.actions);

export const useProblemDataAvailable = () =>
  useProblemDataStore((state) => state.dataAvailable);

export const useProcessedUlds = () =>
  useProblemDataStore((state) => state.processedUlds);

export const usePackages = () => useProblemDataStore((state) => state.packages);
export const useUlds = () => useProblemDataStore((state) => state.ulds);
export const usePackingResults = () =>
  useProblemDataStore((state) => state.packingResults);
