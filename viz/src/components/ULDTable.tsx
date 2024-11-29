import { useMemo } from 'react';
import { MantineReactTable } from 'mantine-react-table';
import { useUlds } from '../stores/problemDataStore';

type Alignment = 'left' | 'center' | 'right';

const ULDTable = () => {
  const columns = useMemo(() => {
    const columnDefs = [
      { header: 'ID', accessorKey: 'id' },
      { header: 'Length', accessorKey: 'length', numeric: true, width: 50 },
      { header: 'Width', accessorKey: 'width', numeric: true },
      { header: 'Height', accessorKey: 'height', numeric: true },
      { header: 'Weight', accessorKey: 'weight', numeric: true },
    ];

    return columnDefs.map((col) => ({
      ...col,
      mantineTableHeadCellProps: {
        align: (col.numeric ? 'center' : 'left') as Alignment,
      },
      mantineTableBodyCellProps: {
        align: (col.numeric ? 'center' : 'left') as Alignment,
      },
      size: 50,
    }));
  }, []);

  const ulds = useUlds();

  return (
    <MantineReactTable
      columns={columns}
      data={ulds}
      enableTopToolbar={false}
      enableDensityToggle={false}
      initialState={{ density: 'xs' }}
      enablePagination={false}
    />
  );
};

export default ULDTable;
