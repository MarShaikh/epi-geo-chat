interface Props {
  data: Record<string, string | number | null | undefined>;
}

export function MetadataTable({ data }: Props) {
  const entries = Object.entries(data).filter(([, v]) => v != null && v !== "");

  if (entries.length === 0) return null;

  return (
    <table className="w-full text-xs">
      <tbody>
        {entries.map(([key, value]) => (
          <tr key={key} className="border-t border-slate-100">
            <td className="py-1 pr-2 text-slate-500 font-medium capitalize whitespace-nowrap">
              {key.replace(/_/g, " ")}
            </td>
            <td className="py-1 text-slate-700 break-all">{String(value)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
