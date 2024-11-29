import Papa from 'papaparse';
import { ZodSchema } from 'zod';
import { IconX } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';

export const parseCSV = <T,>(
  file: File,
  schema: ZodSchema<T>,
): Promise<T[]> => {
  return new Promise((resolve, reject) => {
    Papa.parse<T>(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results: { data: T[] }) => {
        try {
          // Validate each row against the schema
          const validatedData = results.data.map((row) => schema.parse(row));
          resolve(validatedData);
        } catch (validationError) {
          notifications.show({
            title: 'Validation Error',
            message: `Some rows in the CSV file did not match the expected format: ${validationError}`,
            color: 'red',
            icon: <IconX size={16} />,
          });
          reject(validationError);
        }
      },
      error: (error: unknown) => {
        notifications.show({
          title: 'Error Parsing CSV',
          message: 'An error occurred while parsing the CSV file.',
          color: 'red',
          icon: <IconX size={16} />,
        });
        reject(error);
      },
    });
  });
};
