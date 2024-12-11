import axios from 'axios';
import { useState } from 'react';
import { notifications } from '@mantine/notifications';
import {
  Card,
  Container,
  Grid,
  Tabs,
  Title,
  rem,
  Flex,
  Button,
  Text,
} from '@mantine/core';
import { IconPackage, IconBoxMultiple, IconUpload } from '@tabler/icons-react';

import ULDTable from '../components/ULDTable';
import PackageTable from '../components/PackageTable';
import type { PackingResult } from '../utils/dataConvert';
import UploadDataInterface from '../components/CompatibilityUploads';
import {
  usePackages,
  useProblemDataActions,
  useUlds,
} from '../stores/problemDataStore';
import { useNavigate } from 'react-router';

const iconStyle = { width: rem(12), height: rem(12) };

type PackingRespone =
  | {
      status: 'processed';
      result: PackingResult[];
    }
  | {
      status: 'processing';
      request_id: number;
    };

function DataReview() {
  const [packageCompFile, setPackageCompFile] = useState<File | null>(null);
  const [uldCompFile, setUldCompFile] = useState<File | null>(null);
  const navigate = useNavigate();

  const ulds = useUlds();
  const packages = usePackages();
  const { setPackingResults, calculateProcessedUlds } = useProblemDataActions();

  const handleSubmit = async () => {
    notifications.show({
      title: 'Generating solution!',
      color: 'yellow',
      message:
        'Please wait for a couple of minutes while we generate the solution for you!',
    });

    const response = await axios.post<PackingRespone>(
      '/api',
      { packages, ulds },
      { baseURL: import.meta.env.VITE_BACKEND_API_URL },
    );
    const res = response.data;

    if (res.status === 'processed') {
      setPackingResults(res.result);
      calculateProcessedUlds();

      notifications.show({
        title: 'Solution generated!',
        color: 'green',
        message: 'The solution has been generated successfully!',
      });
      navigate('/arena');
    } else {
      notifications.show({
        title: 'Request submitted successfully!',
        color: 'yellow',
        message: `Your request has been submitted with the ID ${res.request_id}. You can access the same from the past requests section on the homepage!`,
      });
      navigate('/');
    }
  };

  return (
    <Container fluid style={{ paddingX: rem(20), margin: rem(20) }}>
      <Flex align="center" justify="center" direction="column">
        <Grid align="center" justify="center">
          <Grid.Col span={8}>
            <Tabs color="indigo" defaultValue="packages">
              <Tabs.List justify="center">
                <Tabs.Tab
                  value="packages"
                  leftSection={<IconPackage style={iconStyle} />}
                >
                  Packages
                </Tabs.Tab>
                <Tabs.Tab
                  value="ulds"
                  leftSection={<IconBoxMultiple style={iconStyle} />}
                  color="lime"
                >
                  ULD Data
                </Tabs.Tab>
              </Tabs.List>

              <Tabs.Panel value="packages">
                <PackageTable />
              </Tabs.Panel>

              <Tabs.Panel value="ulds">
                <ULDTable />
              </Tabs.Panel>
            </Tabs>
          </Grid.Col>

          <Grid.Col span={4}>
            <Card shadow="md" padding="lg" radius="md" withBorder>
              <Card.Section>
                <Flex align="center" direction="row" justify="center" pt="lg">
                  <IconUpload style={{ width: rem(20), height: rem(20) }} />
                  <Title order={4} ml="sm">
                    OR Upload CSVs!
                  </Title>
                </Flex>
              </Card.Section>

              <Flex
                direction="column"
                align="center"
                justify="space-around"
                gap="lg"
              >
                <Text size="sm" pt="sm">
                  You can use this section to upload the CSV files for package
                  and ULD compability!
                </Text>

                <UploadDataInterface
                  file={packageCompFile}
                  setFile={setPackageCompFile}
                  label="Package Compatibility Data"
                />

                <UploadDataInterface
                  file={uldCompFile}
                  setFile={setUldCompFile}
                  label="ULD Compatibility Data"
                />

                <Button color="violet" fullWidth mt="md" radius="md">
                  Submit
                </Button>
              </Flex>
            </Card>
          </Grid.Col>
        </Grid>

        <Button
          onClick={(e) => {
            e.preventDefault();
            handleSubmit();
          }}
          mt="lg"
          w={512}
          color="orange"
        >
          Generate Solution
        </Button>
      </Flex>
    </Container>
  );
}

export default DataReview;
