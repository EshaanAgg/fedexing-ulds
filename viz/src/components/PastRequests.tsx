import axios from 'axios';
import dayjs from 'dayjs';
import { useNavigate } from 'react-router';
import { useQuery } from '@tanstack/react-query';
import { notifications } from '@mantine/notifications';
import { IconArrowForward, IconRefresh } from '@tabler/icons-react';
import { Badge, Button, Drawer, Loader, Table, Text } from '@mantine/core';

import { PackingResult } from '../utils/dataConvert';
import { useProblemDataActions } from '../stores/problemDataStore';

interface Props {
  opened: boolean;
  close: () => void;
}

type PastRequest = {
  id: number;
  timestamp: string;
  status: 'COMPLETED' | 'PENDING';
};

export default function PastRequests(props: Props) {
  const { setPackingResults, calculateProcessedUlds } = useProblemDataActions();
  const navigate = useNavigate();

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['requests'],
    refetchInterval: 10 * 1000,
    queryFn: async () => {
      const response = await axios.get<PastRequest[]>('/api/requests', {
        baseURL: import.meta.env.VITE_BACKEND_API_URL,
      });
      return response.data;
    },
  });

  const fetchAndSetResultsFor = async (id: number) => {
    notifications.show({
      color: 'yellow',
      title: 'Processing...',
      message:
        'Please wait a couple of moments as we fetch the packing details from the server',
    });

    const res = await axios.post<PackingResult[]>(
      '/api/request',
      { id },
      { baseURL: import.meta.env.VITE_BACKEND_API_URL },
    );

    setPackingResults(res.data);
    calculateProcessedUlds();

    navigate('/arena');
  };

  return (
    <Drawer opened={props.opened} onClose={props.close} title="Past Requests">
      <IconRefresh
        onClick={() => {
          refetch();
          notifications.show({
            title: 'Success!',
            color: 'green',
            message: 'Successfully refetched all the unique past requests!',
          });
        }}
        cursor="pointer"
      />
      <br />

      {isLoading ? (
        <Loader />
      ) : data?.length ? (
        <Table striped withTableBorder>
          <Table.Thead>
            <Table.Th>ID</Table.Th>
            <Table.Th>Submitted</Table.Th>
            <Table.Th>Status</Table.Th>
          </Table.Thead>

          <Table.Tbody>
            {data.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>{r.id}</Table.Td>
                <Table.Td>
                  {dayjs(r.timestamp).format('DD/MM/YYYY HH:MM:ss')}
                </Table.Td>
                <Table.Td>
                  {r.status === 'PENDING' ? (
                    <Badge color="yellow">Pending</Badge>
                  ) : (
                    <Button
                      onClick={() => fetchAndSetResultsFor(r.id)}
                      rightSection={<IconArrowForward />}
                      color="green"
                      size="compact-sm"
                    >
                      Completed
                    </Button>
                  )}
                </Table.Td>
              </Table.Tr>
            ))}
          </Table.Tbody>
        </Table>
      ) : (
        <Text>No past request have been made till now</Text>
      )}
    </Drawer>
  );
}
