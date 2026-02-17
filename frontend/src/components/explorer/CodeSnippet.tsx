import { useState } from "react";

interface Props {
  bbox: number[] | null;
  datetime: string | null;
  collections: string[];
}

function generateSnippet(bbox: number[] | null, datetime: string | null, collections: string[]): string {
  const bboxStr = bbox ? `[${bbox.map((n) => n.toFixed(4)).join(", ")}]` : "None";
  const collectionsStr = collections.length > 0
    ? `[${collections.map((c) => `"${c}"`).join(", ")}]`
    : "None";
  const datetimeStr = datetime ? `"${datetime}"` : "None";

  return `from azure.identity import DefaultAzureCredential
import pystac_client
import requests
import os

# --- Configuration ---
CATALOG_URL = os.environ["GEOCATALOG_URL"]
SCOPE = os.environ["GEOCATALOG_SCOPE"]

# --- Authenticate ---
credential = DefaultAzureCredential()
token = credential.get_token(SCOPE).token

catalog = pystac_client.Client.open(
    f"{CATALOG_URL}/stac",
    headers={"Authorization": f"Bearer {token}"},
)

# --- Search ---
results = catalog.search(
    collections=${collectionsStr},
    bbox=${bboxStr},
    datetime=${datetimeStr},
)

# --- Download ---
os.makedirs("downloads", exist_ok=True)
for item in results.items():
    for key, asset in item.assets.items():
        filename = f"downloads/{item.id}_{key}.tif"
        if os.path.exists(filename):
            print(f"Skipping {filename} (already exists)")
            continue
        print(f"Downloading {filename}...")
        resp = requests.get(
            asset.href,
            headers={"Authorization": f"Bearer {token}"},
        )
        resp.raise_for_status()
        with open(filename, "wb") as f:
            f.write(resp.content)

print("Done!")
`;
}

export function CodeSnippet({ bbox, datetime, collections }: Props) {
  const [copied, setCopied] = useState(false);
  const code = generateSnippet(bbox, datetime, collections);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-medium text-slate-600">Download Code (Python)</h4>
        <button
          onClick={handleCopy}
          className="text-xs px-2 py-0.5 rounded bg-slate-200 hover:bg-slate-300 text-slate-700 transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>
      <pre className="text-[11px] bg-slate-900 text-green-400 rounded p-3 overflow-auto max-h-64 leading-relaxed">
        {code}
      </pre>
    </div>
  );
}
