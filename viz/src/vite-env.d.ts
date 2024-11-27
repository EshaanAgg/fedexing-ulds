/// <reference types="vite/client" />

interface PackageMeta {
  position: [number, number, number];
  size: [number, number, number];
  id: string;
  weight: number;
  priority: boolean;
  cost: number;
}

interface ULDMeta {
  position: [number, number, number];
  size: [number, number, number];
  id: string;
  packages: PackageMeta[];
  weight: number;
}

type Vector = [number, number, number];
