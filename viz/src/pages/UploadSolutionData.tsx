import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Dropzone } from '@mantine/dropzone';
import { notifications } from '@mantine/notifications';
import { IconUpload } from '@tabler/icons-react';
import {
  Container,
  Group,
  Text,
  Button,
  Card,
  Title,
  Flex,
} from '@mantine/core';

import {
  getProcessedULDs,
  PackageDataSchema,
  PackingResultSchema,
  ULDDataSchema,
} from '../utils/dataConvert';
import { useProblemDataActions } from '../stores/problemDataStore';
import type { ULDData, PackageData, PackingResult } from '../utils/dataConvert';
import { parseCSV } from '../utils/parse';

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
    <Card withBorder p="sm" mt="sm">
      <Flex direction="column" align="center">
        <Title order={5}>Selected '{file.name}'</Title>
        <Text size="xs">You can click here to upload any other file</Text>
      </Flex>
    </Card>
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
      <Flex direction="column" align="center" justify="center">
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
              w={400}
            >
              <Flex align="center" justify="center" direction="column">
                <Group align="center">
                  <IconUpload size={40} />
                  <Text>{dropzone.label}</Text>
                </Group>

                <DropzoneUploadedFile
                  files={[uldFile, packageFile, solutionFile]}
                  name={dropzone.name as 'uld' | 'package' | 'solution'}
                />
              </Flex>
            </Dropzone>
          ))}
        </Group>

        <Button
          onClick={processFiles}
          color="teal"
          mt="lg"
          rightSection={<IconUpload />}
        >
          Process Files
        </Button>
      </Flex>
    </Container>
  );
}

export default UploadPackingData;
