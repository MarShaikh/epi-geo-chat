import type { AnalysisResult } from "../../types/api";
import { CodeBlock } from "./CodeBlock";
import { ArtifactGallery } from "./ArtifactGallery";
import { ExecutionInfo } from "./ExecutionInfo";

interface Props {
  analysis: AnalysisResult;
}

export function AnalysisPanel({ analysis }: Props) {
  return (
    <section className="space-y-3">
      <h3
        className="text-lg mb-1 border-b border-[#0A0A0A] pb-1"
        style={{ fontFamily: 'var(--font-serif)', borderWidth: '1px' }}
      >
        Analysis
      </h3>

      <p className="text-xs text-[#0A0A0A]">{analysis.description}</p>

      <ArtifactGallery artifacts={analysis.artifacts} />

      <ExecutionInfo
        stdout={analysis.stdout}
        stderr={analysis.stderr}
        executionTimeMs={analysis.execution_time_ms}
        error={analysis.error}
      />

      <details className="text-xs">
        <summary className="cursor-pointer text-[#666666] uppercase tracking-[0.1em] text-[10px]">
          Generated Code
        </summary>
        <div className="mt-1">
          <CodeBlock code={analysis.code} />
        </div>
      </details>
    </section>
  );
}
