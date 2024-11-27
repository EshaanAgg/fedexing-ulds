import Papa from 'papaparse';
import { useEffect } from 'react';
import type { ULDData, PackageData, PackingResult } from '../utils/dataConvert';
import { useProblemDataActions } from '../stores/problemDataStore';
import { getProcessedULDs } from '../utils/dataConvert';
import Arena from './Arena';

const fetchAndParseCSV = async <T,>(url: string): Promise<T[]> => {
  const fileContent = await fetch(url).then((response) => response.text());
  return new Promise((resolve, reject) => {
    Papa.parse<T>(fileContent, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results: { data: T[] }) => resolve(results.data),
      error: (error: unknown) => {
        reject(error);
      },
    });
  });
};

export default function DemoArena() {
  const { setProblemData } = useProblemDataActions();

  useEffect(() => {
    const loadAndSetFiles = async () => {
      try {
        const [uldData, packageData, packingResults] = await Promise.all([
          fetchAndParseCSV<ULDData>('/sample/ulds.csv'),
          fetchAndParseCSV<PackageData>('/sample/packages.csv'),
          fetchAndParseCSV<PackingResult>('/sample/solution.csv'),
        ]);

        setProblemData({
          ulds: uldData,
          packages: packageData,
          packingResults: packingResults,
          processedUlds: getProcessedULDs({
            ulds: uldData,
            packages: packageData,
            packingResults: packingResults,
          }),
        });
      } catch (error) {
        console.error('Error fetching or parsing CSV:', error);
      }
    };

    loadAndSetFiles();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return <Arena />;
}