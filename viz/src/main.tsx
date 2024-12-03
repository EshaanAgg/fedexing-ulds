import gsap from 'gsap';
import { StrictMode } from 'react';
import { useGSAP } from '@gsap/react';
import { createRoot } from 'react-dom/client';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import App from './App.tsx';

import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/dropzone/styles.css';
import 'mantine-react-table/styles.css';
import '@mantine/notifications/styles.css';

gsap.registerPlugin(useGSAP);

const queryClient = new QueryClient();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <MantineProvider>
      <QueryClientProvider client={queryClient}>
        <Notifications />
        <App />
      </QueryClientProvider>
    </MantineProvider>
  </StrictMode>,
);
