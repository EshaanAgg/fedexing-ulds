import { Grid } from '@react-three/drei';

interface OptionalGroundProps {
  cellSize: number;
  cellThickness: number;
  cellColor: string;
  sectionSize: number;
  sectionThickness: number;
  sectionColor: string;
  fadeDistance: number;
  fadeStrength: number;
  followCamera: boolean;
  infiniteGrid: boolean;
}

const defaultGroundProps: OptionalGroundProps = {
  cellSize: 0.5,
  cellThickness: 0.5,
  cellColor: '#6f6f6f',
  sectionSize: 3,
  sectionThickness: 1,
  sectionColor: '#9d4b4b',
  fadeDistance: 30,
  fadeStrength: 1,
  followCamera: false,
  infiniteGrid: true,
};

interface GridProps extends Partial<OptionalGroundProps> {
  position: [number, number, number];
  args: [number, number];
}

export default function Ground(props: GridProps) {
  return <Grid {...defaultGroundProps} {...props} />;
}
