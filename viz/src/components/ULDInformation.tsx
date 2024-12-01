import { Dialog, Text } from '@mantine/core';
import { useActiveUld, useActiveUldActions } from '../stores/activeUldStore';

export default function ULDInformation() {
  const activeULD = useActiveUld();
  const { deactivateUld } = useActiveUldActions();

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
        ULD {activeULD}
      </Text>
    </Dialog>
  );
}
