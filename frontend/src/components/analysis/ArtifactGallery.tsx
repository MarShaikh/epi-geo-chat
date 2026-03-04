import { useState, useEffect } from "react";
import type { AnalysisArtifact } from "../../types/api";

const API_BASE = "/api/v1";

interface Props {
  artifacts: AnalysisArtifact[];
}

export function ArtifactGallery({ artifacts }: Props) {
  if (artifacts.length === 0) return null;

  return (
    <div className="space-y-3">
      <h4 className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">
        Outputs ({artifacts.length})
      </h4>
      {artifacts.map((a) => (
        <ArtifactRenderer key={a.artifact_id} artifact={a} />
      ))}
    </div>
  );
}

function ArtifactRenderer({ artifact }: { artifact: AnalysisArtifact }) {
  const url = `${API_BASE}/artifacts/${artifact.artifact_id}`;

  if (artifact.content_type.startsWith("image/")) {
    return (
      <div className="border border-[#0A0A0A]" style={{ borderWidth: '1px' }}>
        <img
          src={url}
          alt={artifact.filename}
          className="w-full"
          loading="lazy"
        />
        <div className="px-2 py-1 border-t border-[#0A0A0A] flex items-center justify-between" style={{ borderWidth: '1px' }}>
          <span className="text-[10px] text-[#666666]" style={{ fontFamily: 'var(--font-mono)' }}>
            {artifact.filename}
          </span>
          <a
            href={url}
            download={artifact.filename}
            className="text-[10px] uppercase tracking-[0.1em] text-[#D9381E] hover:underline"
            style={{ fontFamily: 'var(--font-mono)' }}
          >
            DOWNLOAD
          </a>
        </div>
      </div>
    );
  }

  if (artifact.content_type === "text/html") {
    return (
      <div className="border border-[#0A0A0A]" style={{ borderWidth: '1px' }}>
        <iframe
          src={url}
          sandbox="allow-scripts"
          className="w-full h-80 border-none"
          title={artifact.filename}
        />
        <div className="px-2 py-1 border-t border-[#0A0A0A]" style={{ borderWidth: '1px' }}>
          <span className="text-[10px] text-[#666666]" style={{ fontFamily: 'var(--font-mono)' }}>
            {artifact.filename}
          </span>
        </div>
      </div>
    );
  }

  if (artifact.content_type === "text/csv") {
    return <CsvViewer url={url} filename={artifact.filename} />;
  }

  // Fallback: download link
  return (
    <div className="px-2 py-1.5 border border-[#0A0A0A]" style={{ borderWidth: '1px' }}>
      <a
        href={url}
        download={artifact.filename}
        className="text-xs text-[#D9381E] hover:underline"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        {artifact.filename} ({(artifact.size_bytes / 1024).toFixed(1)} KB)
      </a>
    </div>
  );
}

function CsvViewer({ url, filename }: { url: string; filename: string }) {
  const [rows, setRows] = useState<string[][]>([]);

  useEffect(() => {
    fetch(url)
      .then((r) => r.text())
      .then((text) => {
        const lines = text.trim().split("\n").slice(0, 50); // Limit to 50 rows
        setRows(lines.map((line) => line.split(",")));
      })
      .catch(() => {});
  }, [url]);

  if (rows.length === 0) return null;

  const headers = rows[0];
  const body = rows.slice(1);

  return (
    <div className="border border-[#0A0A0A]" style={{ borderWidth: '1px' }}>
      <div className="overflow-auto max-h-64">
        <table className="w-full text-[11px]" style={{ fontFamily: 'var(--font-mono)' }}>
          <thead>
            <tr className="bg-[#0A0A0A] text-[#F2F2EC]">
              {headers.map((h, i) => (
                <th key={i} className="px-2 py-1 text-left font-normal whitespace-nowrap">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {body.map((row, ri) => (
              <tr key={ri} className="border-t border-[#0A0A0A]/10">
                {row.map((cell, ci) => (
                  <td key={ci} className="px-2 py-0.5 whitespace-nowrap">{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="px-2 py-1 border-t border-[#0A0A0A]" style={{ borderWidth: '1px' }}>
        <span className="text-[10px] text-[#666666]" style={{ fontFamily: 'var(--font-mono)' }}>
          {filename}
        </span>
      </div>
    </div>
  );
}
