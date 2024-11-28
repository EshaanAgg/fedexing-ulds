import Papa from 'papaparse';
import { useState } from 'react';
import { ZodSchema } from 'zod';
import { useNavigate } from 'react-router';
import { Dropzone } from '@mantine/dropzone';
import { notifications } from '@mantine/notifications';
import { IconUpload, IconX } from '@tabler/icons-react';
import { Container, Group, Text, Button } from '@mantine/core';

import {
  getProcessedULDs,
  PackageDataSchema,
  PackingResultSchema,
  ULDDataSchema,
} from '../utils/dataConvert';
import { useProblemDataActions } from '../stores/problemDataStore';
import type { ULDData, PackageData, PackingResult } from '../utils/dataConvert';

const parseCSV = <T,>(file: File, schema: ZodSchema<T>): Promise<T[]> => {
  return new Promise((resolve, reject) => {
    Papa.parse<T>(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results: { data: T[] }) => {
        try {
          // Validate each row against the schema
          const validatedData = results.data.map((row) => schema.parse(row));
          resolve(validatedData);
        } catch (validationError) {
          notifications.show({
            title: 'Validation Error',
            message: `Some rows in the CSV file did not match the expected format: ${validationError}`,
            color: 'red',
            icon: <IconX size={16} />,
          });
          reject(validationError);
        }
      },
      error: (error: unknown) => {
        notifications.show({
          title: 'Error Parsing CSV',
          message: 'An error occurred while parsing the CSV file.',
          color: 'red',
          icon: <IconX size={16} />,
        });
        reject(error);
      },
    });
  });
};

function DropzoneUploadedFile({
  files,
  name,
}: {
  files: (File | null)[];
  name: 'uld' | 'package' | 'solution';
}) {
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
}

function UploadPackingData() {
  const { setProblemData } = useProblemDataActions();
  const navigate = useNavigate();

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
        parseCSV<ULDData>(uldFile, ULDDataSchema),
        parseCSV<PackageData>(packageFile, PackageDataSchema),
        parseCSV<PackingResult>(solutionFile, PackingResultSchema),
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
      navigate('/arena');
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
}

export default UploadPackingData;
