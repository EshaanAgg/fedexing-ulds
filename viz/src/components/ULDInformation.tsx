import { Button, Dialog, Flex, Text } from '@mantine/core';
import { useActiveUld, useActiveUldActions } from '../stores/activeUldStore';
import { useNavigate } from 'react-router';
import {
  usePackages,
  usePackingResults,
  useUlds,
} from '../stores/problemDataStore';
import { getLoadingPlan } from '../utils/dataConvert';
import { generatePDF } from '../utils/pdf';
import { notifications } from '@mantine/notifications';
import ULDMetrics from './ULDMetrics';

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

  const targetULD = useUlds().find((uld) => uld.id === activeULD);
  const pkgs = solutionData
    .filter((r) => r.uld_id === activeULD)
    .map((r) => ({
      ...r,
      weight: packages.find((p) => p.id === r.pack_id)!.weight,
    }));

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

        <ULDMetrics
          id={activeULD}
          dimensions={[
            targetULD?.length ?? 0,
            targetULD?.width ?? 0,
            targetULD?.height ?? 0,
          ]}
          weight={targetULD?.weight ?? 0}
          packages={pkgs}
        />

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
