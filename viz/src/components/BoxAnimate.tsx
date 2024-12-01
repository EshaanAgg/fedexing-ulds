export const BoxWithRef = forwardRef(function (props: Box, ref: Ref<Mesh>) {
  return (
    <mesh position={addCoordinates(OFFSET_VECTOR, props.center)} ref={ref}>
      <boxGeometry args={props.size} />
      <meshStandardMaterial color={props.color} transparent opacity={0.5} />
      <Edges scale={1.0} color="black" />
    </mesh>
  );
});
