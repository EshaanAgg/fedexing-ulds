import { IconSearch } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import { Autocomplete, Burger, Group, Image } from '@mantine/core';

import classes from './Header.module.css';
import { useNavigate } from 'react-router';

const links = [
  { link: '/ship', label: 'Shippinng' },
  { link: '/pricing', label: 'Pricing' },
  { link: '/dashboard', label: 'Dashboard' },
];

export default function Header() {
  const [opened, { toggle }] = useDisclosure(false);
  const navigate = useNavigate();

  const items = links.map((link) => (
    <a
      key={link.label}
      href={link.link}
      className={classes.link}
      onClick={(event) => event.preventDefault()}
    >
      {link.label}
    </a>
  ));

  return (
    <header className={classes.header}>
      <div className={classes.inner}>
        <Group>
          <Burger opened={opened} onClick={toggle} size="sm" hiddenFrom="sm" />
          <Image
            src="/logo.png"
            alt="FedEx Logo"
            height={55}
            onClick={() => navigate('/')}
            style={{ cursor: 'pointer' }}
          />
        </Group>

        <Group>
          <Group ml={50} gap={5} className={classes.links} visibleFrom="sm">
            {items}
          </Group>
          <Autocomplete
            className={classes.search}
            placeholder="Search"
            leftSection={<IconSearch size={16} stroke={1.5} />}
            data={['Shipping', 'Commerce', 'Pricing', 'Dashboard', 'Support']}
            visibleFrom="xs"
          />
        </Group>
      </div>
    </header>
  );
}
