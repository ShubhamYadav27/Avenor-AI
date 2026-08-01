/** Utility to export JSON array data as CSV file download */
export function exportToCsv<T extends Record<string, any>>(filename: string, rows: T[], headers?: { key: keyof T; label: string }[]) {
  if (!rows || !rows.length) return;

  const cols = headers || Object.keys(rows[0]).map((k) => ({ key: k as keyof T, label: k }));
  const headerLine = cols.map((c) => `"${String(c.label).replace(/"/g, '""')}"`).join(",");
  
  const rowLines = rows.map((row) =>
    cols
      .map((c) => {
        const val = row[c.key];
        if (val === null || val === undefined) return '""';
        if (typeof val === "object") return `"${JSON.stringify(val).replace(/"/g, '""')}"`;
        return `"${String(val).replace(/"/g, '""')}"`;
      })
      .join(",")
  );

  const csvContent = "data:text/csv;charset=utf-8," + [headerLine, ...rowLines].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", `${filename}_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
