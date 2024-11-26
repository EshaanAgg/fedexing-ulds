import Papa from 'papaparse';
import React, { useState } from 'react';
import { Container, Group, Text, Button } from '@mantine/core';
import { Dropzone } from '@mantine/dropzone';
import { notifications } from '@mantine/notifications';
import type { ULDData, PackageData, PackingResult } from '../utils/dataConvert';
import { IconUpload, IconX } from '@tabler/icons-react';
import { useProblemDataActions } from '../stores/problemDataStore';
import { getProcessedULDs } from '../utils/dataConvert';

const parseCSV = <T,>(file: File): Promise<T[]> => {
  return new Promise((resolve, reject) => {
    Papa.parse<T>(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results: { data: T[] }) => resolve(results.data),
      error: (error: unknown) => {
        notifications.show({
          title: 'Error parsing CSV',
          message: 'An error occurred while parsing the CSV file.',
          color: 'red',
          icon: <IconX size={16} />,
        });
        reject(error);
      },
    });
  });
};

const DropzoneUploadedFile: React.FC<{
  files: (File | null)[];
  name: 'uld' | 'package' | 'solution';
}> = ({ files, name }) => {
  let file = null;
  if (name === 'uld') file = files[0];
  if (name === 'package') file = files[1];
  if (name === 'solution') file = files[2];

  if (!file) return null;

  return (
    <>
      <Text>Selected '{file.name}'</Text>
      <Text size="xs">You can click here to upload any other file</Text>
    </>
  );
};

const UploadPackingData: React.FC = () => {
  const { setProblemData } = useProblemDataActions();

  const [uldFile, setUldFile] = useState<File | null>(null);
  const [packageFile, setPackageFile] = useState<File | null>(null);
  const [solutionFile, setSolutionFile] = useState<File | null>(null);

  const handleFileUpload = (
    file: File,
    type: 'uld' | 'package' | 'solution',
  ) => {
    switch (type) {
      case 'uld':
        setUldFile(file);
        break;
      case 'package':
        setPackageFile(file);
        break;
      case 'solution':
        setSolutionFile(file);
        break;
    }
  };

  const processFiles = async () => {
    try {
      if (!uldFile || !packageFile || !solutionFile) {
        notifications.show({
          title: 'Missing files!',
          message:
            'Please upload all required files to generate the visualizations.',
          color: 'red',
        });
        return;
      }

      notifications.show({
        title: 'Processing files!',
        message:
          'Please wait while we process the uploaded files to generate the visualizations.',
        color: 'cyan',
      });

      const [ulds, packages, packingResults] = await Promise.all([
        parseCSV<ULDData>(uldFile),
        parseCSV<PackageData>(packageFile),
        parseCSV<PackingResult>(solutionFile),
      ]);

      setProblemData({
        ulds,
        packages,
        packingResults,
        processedUlds: getProcessedULDs({ ulds, packages, packingResults }),
      });
      notifications.show({
        title: 'Files processed!',
        message: 'The files have been processed successfully!',
        color: 'green',
      });
    } catch (err) {
      console.error(`Error processing files: ${err}`);
    }
  };

  const dropzones = [
    {
      name: 'uld',
      label: 'Upload ULDs CSV',
    },
    {
      name: 'package',
      label: 'Upload Packages CSV',
    },
    {
      name: 'solution',
      label: 'Upload Solution CSV',
    },
  ];

  return (
    <Container mt="lg" mb="lg" p="lg">
      <Group dir="column" grow>
        {dropzones.map((dropzone) => (
          <Dropzone
            key={dropzone.name}
            accept={{ 'text/csv': ['.csv'] }}
            onDrop={(files) =>
              handleFileUpload(
                files[0],
                dropzone.name as 'uld' | 'package' | 'solution',
              )
            }
          >
            <Group align="center">
              <IconUpload size={40} />
              <Text>{dropzone.label}</Text>
            </Group>

            <DropzoneUploadedFile
              files={[uldFile, packageFile, solutionFile]}
              name={dropzone.name as 'uld' | 'package' | 'solution'}
            />
          </Dropzone>
        ))}
      </Group>

      <Button onClick={processFiles} color="teal">
        Process Files
      </Button>
    </Container>
  );
};

export default UploadPackingData;