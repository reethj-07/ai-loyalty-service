"use client";

import { useState } from "react";
import { analyzeCampaign } from "@/lib/api";
import CampaignSummary from "@/components/CampaignSummary";

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const runAnalysis = async () => {
    setLoading(true);
    try {
      const data = await analyzeCampaign();
      setResult(data);
    } catch (err) {
      alert("Failed to analyze campaign");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">
        AI Campaign Recommendation Module
      </h1>

      <button
        onClick={runAnalysis}
        className="px-4 py-2 bg-blue-600 text-white rounded"
        disabled={loading}
      >
        {loading ? "Analyzing..." : "Analyze Campaign Opportunity"}
      </button>

      {result && <CampaignSummary data={result} />}
    </main>
  );
}
