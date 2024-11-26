export const getRandomColor = () => {
  const supportedThreeColors = [
    'black',
    'white',
    'red',
    'green',
    'blue',
    'yellow',
    'purple',
    'orange',
    'cyan',
    'magenta',
  ];

  return supportedThreeColors[
    Math.floor(Math.random() * supportedThreeColors.length)
  ];
};
