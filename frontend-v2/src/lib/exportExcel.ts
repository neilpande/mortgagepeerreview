import ExcelJS from 'exceljs';

export interface SheetColumn<T> {
  header: string;
  get: (row: T) => number | string | null;
  numFmt?: string;
}

export interface SheetDef<T> {
  sheetName: string;
  rows: T[];
  labelHeader: string;
  labelGet: (row: T) => string;
  columns: SheetColumn<T>[];
}

// PRD M5: "Download as Excel" on the active tab/view, with consistent
// formatting, verified against on-screen data. Callers build sheet defs
// directly from the same rows the tables on screen render from, so the
// export can never drift from what's displayed.
export async function exportWorkbook<T>(filename: string, sheets: SheetDef<T>[]) {
  const workbook = new ExcelJS.Workbook();
  workbook.creator = 'Cloverstone Servicer Peer Analytics Dashboard';
  workbook.created = new Date();

  for (const sheet of sheets) {
    const worksheet = workbook.addWorksheet(sheet.sheetName);
    worksheet.columns = [
      { header: sheet.labelHeader, key: 'label', width: 30 },
      ...sheet.columns.map((c, i) => ({ header: c.header, key: `c${i}`, width: 20 })),
    ];
    worksheet.getRow(1).font = { bold: true };
    worksheet.getRow(1).alignment = { vertical: 'middle' };

    for (const row of sheet.rows) {
      const record: Record<string, number | string | null> = { label: sheet.labelGet(row) };
      sheet.columns.forEach((c, i) => {
        record[`c${i}`] = c.get(row);
      });
      const addedRow = worksheet.addRow(record);
      sheet.columns.forEach((c, i) => {
        if (c.numFmt) addedRow.getCell(`c${i}`).numFmt = c.numFmt;
      });
    }
  }

  const buffer = await workbook.xlsx.writeBuffer();
  const blob = new Blob([buffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}
