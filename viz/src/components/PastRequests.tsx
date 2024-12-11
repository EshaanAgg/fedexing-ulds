import axios from 'axios';
import { Badge, Button, Drawer, Loader, Table, Text } from '@mantine/core';
import { useQuery } from '@tanstack/react-query';

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
  const { data, isLoading } = useQuery({
    queryKey: ['requests'],
    refetchInterval: 10 * 1000,
    queryFn: async () => {
      const response = await axios.get<PastRequest[]>('/api/requests', {
        baseURL: import.meta.env.VITE_BACKEND_API_URL,
      });
      return response.data;
    },
  });

  const fetchAndSetResultsFor = (id: number) => {};

  return (
    <Drawer opened={props.opened} onClose={props.close} title="Past Requests">
      {isLoading ? (
        <Loader />
      ) : data?.length ? (
        <Table striped withTableBorder>
          <Table.Thead>
            <Table.Td>ID</Table.Td>
            <Table.Td>Submitted</Table.Td>
            <Table.Td>Status</Table.Td>
          </Table.Thead>

          <Table.Tbody>
            {data.map((r) => (
              <Table.Tr key={r.id}>
                <Table.Td>{r.id}</Table.Td>
                <Table.Td>{r.timestamp}</Table.Td>
                <Table.Td>
                  {r.status === 'PENDING' ? (
                    <Badge color="yellow">Pending</Badge>
                  ) : (
                    <Button onClick={() => fetchAndSetResultsFor(r.id)}>
                      <Badge>Completed</Badge>
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
