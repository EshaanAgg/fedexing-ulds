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
import PackageTable from '../components/PackageTable';
import ULDTable from '../components/ULDTable';

function DataReview() {
  const iconStyle = { width: rem(12), height: rem(12) };

  const handleSubmit = () => {
    console.log('Generating solution');
  };

  return (
    <Container fluid style={{ paddingX: rem(20) }}>
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

              <Text size="sm" pt="sm">
                You can use this section to upload the CSV files for package and
                ULD compability!
              </Text>
              <Button color="violet" fullWidth mt="md" radius="md">
                Submit
              </Button>
            </Card>
          </Grid.Col>
        </Grid>

        <Button onClick={handleSubmit} mt="lg" w={512} color="orange">
          Generate Solution
        </Button>
      </Flex>
    </Container>
  );
}

export default DataReview;
