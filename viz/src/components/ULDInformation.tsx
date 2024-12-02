import { Button, Dialog, Flex, Text } from '@mantine/core';
import { useActiveUld, useActiveUldActions } from '../stores/activeUldStore';
import { useNavigate } from 'react-router';

export default function ULDInformation() {
  const activeULD = useActiveUld();
  const { deactivateUld } = useActiveUldActions();
  const navigate = useNavigate();

  return (
    <Dialog
      opened={activeULD !== null}
      withCloseButton
      onClose={deactivateUld}
      size="lg"
      radius="md"
      position={{ top: 75, left: 20 }}
    >
      <Text size="sm" fw={500}>
        <Flex justify="center" align="center" gap="md" direction="column">
          ULD {activeULD}
          <Button
            onClick={() => {
              navigate(`/load/${activeULD}`);
              deactivateUld();
            }}
            color="blue"
          >
            Load ULD
          </Button>
        </Flex>
      </Text>
    </Dialog>
  );
}
