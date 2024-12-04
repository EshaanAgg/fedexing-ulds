import axios from 'axios';
import { useQuery } from '@tanstack/react-query';
import { Loader, Table, Text } from '@mantine/core';

interface Package {
  x1: number;
  x2: number;
  y1: number;
  y2: number;
  z1: number;
  z2: number;
  weight: number;
}

interface ULD {
  id: string | null;
  dimensions: Vector | null;
  weight: number;
  packages: Package[] | null;
}

interface Metrics {
  count: number;
  moi: number;
  utilization: number;
  weight_utilization: number;
  stability: number;
}

const ULDMetrics = (props: ULD) => {
  const { data, isLoading, error } = useQuery<Metrics>({
    queryKey: ['uldMetrics', props.id, props.dimensions, props.packages],
    queryFn: async () => {
      if (!props.dimensions || !props.packages)
        return {
          count: 0,
          moi: 0,
          utilization: 0,
          weight_utilization: 0,
          stability: 0,
        };

      const response = await axios.post<Metrics>(
        '/api/metrics',
        {
          uld_length: props.dimensions[0],
          uld_width: props.dimensions[1],
          uld_height: props.dimensions[2],
          uld_weight: props.weight,
          packages: props.packages,
        },
        {
          baseURL: import.meta.env.VITE_BACKEND_API_URL,
        },
      );

      return response.data;
    },
  });

  if (isLoading) return <Loader />;
  if (error instanceof Error) return <Text>Error: {error.message}</Text>;

  const dataToDisplay = [
    { label: 'Package Count', val: data?.count.toString() },
    { label: 'Moment Stabilization', val: data?.moi.toFixed(3) },
    {
      label: 'Space Utilization',
      val: `${((data?.utilization ?? 0) * 100).toFixed(2)} %`,
    },
    {
      label: 'Weight Utilization',
      val: `${((data?.weight_utilization ?? 0) * 100).toFixed(2)} %`,
    },
    {
      label: 'Physical Stability',
      val: data?.stability.toFixed(3),
    },
  ];

  return (
    <Table highlightOnHover withTableBorder>
      <Table.Tbody>
        {dataToDisplay.map((item) => (
          <Table.Tr key={item.label}>
            <Table.Td>{item.label}</Table.Td>
            <Table.Td>{item.val}</Table.Td>
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
};

export default ULDMetrics;
