import jsPDF from 'jspdf';
import 'jspdf-autotable';

export const generatePDF = (
  file_name: string,
  title: string,
  headers: string[],
  data: string[][],
) => {
  const doc = new jsPDF();

  doc.text(title, 20, 10);

  // Type-case to any to avoid type errors
  // with the autoTable plugin
  (doc as any).autoTable({
    head: [headers],
    body: data,
    startY: 20,
  });

  doc.save(`${file_name}.pdf`);
};
