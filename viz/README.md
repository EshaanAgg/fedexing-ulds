# Visualization

This project makes use of [Three JS](https://threejs.org/) to render the visualizations. We make use of [React Three Fiber](https://r3f.docs.pmnd.rs/getting-started/introduction) to act as an abstraction layer over Three JS so that we can use React components to create the visualizations.

Other libraries used in this project are:

- [Zustand](https://zustand.surge.sh/) for state management
- [Mantine UI](https://mantine.dev/) for UI components
- [DREI](https://drei.pmnd.rs/) for useful components and hooks for React Three Fiber
- [Papa Parse](https://www.papaparse.com/) for parsing CSV files in the browser
- [Tabler Icons](https://tablericons.com/) for icons

The project is bundled with [Vite](https://vitejs.dev/) and uses [TypeScript](https://www.typescriptlang.org/) for type checking.

## Setting up the project

We use [PNPM](https://pnpm.io/) as the package manager for this project. To set up the project, run the following commands:

```bash
pnpm install
```

To start the development server, run:

```bash
pnpm dev
```
