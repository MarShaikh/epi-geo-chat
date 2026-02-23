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
          <tr key={key} className="border-t border-[#0A0A0A]" style={{ borderWidth: '1px' }}>
            <td className="py-1 pr-2 text-[10px] uppercase tracking-[0.1em] text-[#666666] whitespace-nowrap" style={{ fontFamily: 'var(--font-mono)' }}>
              {key.replace(/_/g, " ")}
            </td>
            <td className="py-1 text-[#0A0A0A] break-all">{String(value)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
