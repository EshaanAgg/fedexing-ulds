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

import { PackageDataSchema, ULDDataSchema } from '../utils/dataConvert';
import { useProblemDataActions } from '../stores/problemDataStore';
import type { ULDData, PackageData } from '../utils/dataConvert';
import { parseCSV } from '../utils/parse';
import { useDisclosure } from '@mantine/hooks';
import PastRequests from '../components/PastRequests';

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

function Home() {
  const { setPackageAndUldData } = useProblemDataActions();
  const navigate = useNavigate();

  const [uldFile, setUldFile] = useState<File | null>(null);
  const [packageFile, setPackageFile] = useState<File | null>(null);
  const [
    requestDrawerOpened,
    { open: openRequestDrawer, close: closeRequestDrawer },
  ] = useDisclosure(false);

  const handleFileUpload = (file: File, type: 'uld' | 'package') => {
    switch (type) {
      case 'uld':
        setUldFile(file);
        break;
      case 'package':
        setPackageFile(file);
        break;
    }
  };

  const processFiles = async () => {
    try {
      if (!uldFile || !packageFile) {
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

      const [ulds, packages] = await Promise.all([
        parseCSV<ULDData>(uldFile, ULDDataSchema),
        parseCSV<PackageData>(packageFile, PackageDataSchema),
      ]);
      setPackageAndUldData(packages, ulds);

      notifications.show({
        title: 'Files processed!',
        message: 'The files have been processed successfully!',
        color: 'green',
      });
      navigate('/review');
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
                handleFileUpload(files[0], dropzone.name as 'uld' | 'package')
              }
              w={400}
            >
              <Flex align="center" justify="center" direction="column">
                <Group align="center">
                  <IconUpload size={40} />
                  <Text>{dropzone.label}</Text>
                </Group>

                <DropzoneUploadedFile
                  files={[uldFile, packageFile]}
                  name={dropzone.name as 'uld' | 'package'}
                />
              </Flex>
            </Dropzone>
          ))}
        </Group>

        <Button
          onClick={processFiles}
          color="orange"
          mt="lg"
          rightSection={<IconUpload />}
        >
          Process Files
        </Button>

        {/* Request drawer content */}
        <Button variant="default" onClick={openRequestDrawer} mt="lg">
          View Previous Requests
        </Button>
        <PastRequests opened={requestDrawerOpened} close={closeRequestDrawer} />
      </Flex>
    </Container>
  );
}

export default Home;
