import { Dropzone } from '@mantine/dropzone';
import { notifications } from '@mantine/notifications';
import { IconUpload } from '@tabler/icons-react';
import { Group, Text, Card, Title, Flex } from '@mantine/core';

function DropzoneUploadedFile({ file }: { file: File | null }) {
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

interface UploadDataInterface {
  file: File | null;
  setFile: (file: File | null) => void;
  label: string;
}

function UploadDataInterface(props: UploadDataInterface) {
  return (
    <Dropzone
      accept={{ 'text/csv': ['.csv'] }}
      onDrop={(files) => {
        props.setFile(files[0]);
        notifications.show({
          title: 'File uploaded',
          message: `Uploaded ${files[0].name}!`,
          color: 'teal',
        });
      }}
      w={350}
    >
      <Flex align="center" justify="center" direction="column">
        <Group align="center">
          <IconUpload size={30} />
          <Text>{props.label}</Text>
        </Group>

        <DropzoneUploadedFile file={props.file} />
      </Flex>
    </Dropzone>
  );
}

export default UploadDataInterface;
