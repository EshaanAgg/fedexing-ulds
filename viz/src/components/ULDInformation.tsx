import { Button, Dialog, Flex, Text } from '@mantine/core';
import { useActiveUld, useActiveUldActions } from '../stores/activeUldStore';
import { useNavigate } from 'react-router';
import { usePackages, usePackingResults } from '../stores/problemDataStore';
import { getLoadingPlan } from '../utils/dataConvert';
import { generatePDF } from '../utils/pdf';
import { notifications } from '@mantine/notifications';

export default function ULDInformation() {
  const activeULD = useActiveUld();

  const { deactivateUld } = useActiveUldActions();
  const navigate = useNavigate();

  const solutionData = usePackingResults();
  const packages = usePackages();

  const handleLoadingPlan = () => {
    if (!activeULD) return;

    // Loading notification to the user
    notifications.show({
      title: 'Processing...',
      color: 'yellow',
      message: 'Please wait while we are generating the loading plan.',
    });

    const { headers, data } = getLoadingPlan(activeULD, solutionData, packages);
    generatePDF(activeULD, `Loading Plan for ULD ${activeULD}`, headers, data);

    // Completion notification to the user
    notifications.show({
      title: 'Success',
      color: 'teal',
      message: 'Loading plan has been generated successfully.',
    });
  };

  return (
    <Dialog
      opened={activeULD !== null}
      withCloseButton
      onClose={deactivateUld}
      size="lg"
      radius="md"
      withBorder
      shadow="md"
      position={{ top: 75, left: 20 }}
      bg="whitesmoke"
    >
      <Flex justify="center" align="center" gap="md" direction="column">
        <Text size="md" fw={500}>
          ULD {activeULD}
        </Text>

        <Flex direction="row" gap="md">
          <Button
            onClick={() => {
              deactivateUld();
              navigate(`/load/${activeULD}`);
            }}
          >
            Load ULD
          </Button>
          <Button onClick={handleLoadingPlan}>Download Plan</Button>
        </Flex>
      </Flex>
    </Dialog>
  );
}
