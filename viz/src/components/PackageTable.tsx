import { useMemo } from 'react';
import { Grid, MultiSelect, Switch } from '@mantine/core';
import { MantineReactTable } from 'mantine-react-table';

import { usePackages, useUlds } from '../stores/problemDataStore';
import type { PackageData } from '../utils/dataConvert';
import {
  getIncompatiblePackages,
  getIncompatibleUlds,
  getUnstackableFaces,
  usePackageDataActions,
  getIsFragilePackage,
  getIsHeavyPackage,
} from '../stores/packageDataStore';

interface ExpandedRowProps {
  data: PackageData;
  packagesIDs: string[];
  uldsIDs: string[];
}

const ExpandedRow = (props: ExpandedRowProps) => {
  const actions = usePackageDataActions();

  const incompatiblePackages = getIncompatiblePackages(props.data.id);
  const incompatibleUlds = getIncompatibleUlds(props.data.id);
  const unstackableFaces = getUnstackableFaces(props.data.id);

  return (
    <Grid>
      {/* Incomptabile Packages */}
      <Grid.Col span={6}>
        <MultiSelect
          checkIconPosition="right"
          data={props.packagesIDs.filter((p) => p !== props.data.id)}
          searchable
          label="Incompatible Packages"
          value={incompatiblePackages}
          onChange={(value) =>
            actions.setIncompatiblePackages(props.data.id, value)
          }
        />
      </Grid.Col>

      {/* Incomptabile ULDs */}
      <Grid.Col span={6}>
        <MultiSelect
          checkIconPosition="right"
          data={props.uldsIDs}
          searchable
          label="Incompatible ULDs"
          value={incompatibleUlds}
          onChange={(value) =>
            actions.setIncompatibleUlds(props.data.id, value)
          }
        />
      </Grid.Col>

      {/* Incomptabile Faces for Stacking */}
      <Grid.Col span={6}>
        <MultiSelect
          checkIconPosition="right"
          data={['XY[1]', 'XY[2]', 'YZ[1]', 'YZ[2]', 'XZ[1]', 'XZ[2]']}
          searchable
          label="Cannot be stacked on"
          value={unstackableFaces}
          onChange={(value) =>
            actions.setUnstackableFaces(props.data.id, value)
          }
        />
      </Grid.Col>

      {/* Switches for Heavy and Fragile Packages */}
      <Grid.Col span={3}>
        <Switch
          label="Heavy Package"
          checked={getIsHeavyPackage(props.data.id)}
          onChange={(_) => actions.toggleHeavyPackage(props.data.id)}
        />
      </Grid.Col>

      <Grid.Col span={3}>
        <Switch
          label="Fragile Package"
          checked={getIsFragilePackage(props.data.id)}
          onChange={(_) => actions.toggleFragilePackage(props.data.id)}
        />
      </Grid.Col>
    </Grid>
  );
};

type Alignment = 'left' | 'center' | 'right';

const PackageTable = () => {
  const columns = useMemo(() => {
    const columnDefs = [
      { header: 'ID', accessorKey: 'id' },
      { header: 'Length', accessorKey: 'length', numeric: true },
      { header: 'Width', accessorKey: 'width', numeric: true },
      { header: 'Height', accessorKey: 'height', numeric: true },
      { header: 'Weight', accessorKey: 'weight', numeric: true },
      { header: 'Priority', accessorKey: 'priority' },
      { header: 'Cost', accessorKey: 'cost', numeric: true },
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

  const packages = usePackages();
  const ulds = useUlds();

  const allPackagesIDs = packages.map((p) => p.id);
  const allULDsIDs = ulds.map((u) => u.id);

  return (
    <MantineReactTable
      columns={columns}
      data={packages}
      enableDensityToggle={false}
      initialState={{ density: 'xs' }}
      mantinePaginationProps={{
        showRowsPerPage: false,
        __size: 'xs',
      }}
      enableTopToolbar={false}
      renderDetailPanel={({ row }) => (
        <ExpandedRow
          data={row.original}
          packagesIDs={allPackagesIDs}
          uldsIDs={allULDsIDs}
        />
      )}
    />
  );
};

export default PackageTable;
