import { Container, Flex, Text, Title } from '@mantine/core';

export default function DoesNotExist() {
  return (
    <Container>
      <Flex
        align="center"
        justify="center"
        direction="column"
        className="my-auto"
      >
        <Title order={1} style={{ color: 'teal' }} pt={36}>
          404
        </Title>
        <Title order={4}>You have found a secret place.</Title>

        <Text c="dimmed" size="lg" ta="center" pt={48}>
          Unfortunately, this is a 404 page. You may have mistyped the address,
          or the page has been moved to another URL.
        </Text>
      </Flex>
    </Container>
  );
}
