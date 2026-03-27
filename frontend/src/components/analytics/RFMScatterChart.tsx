import { Scatter, ScatterChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export interface RFMPoint {
  memberId: string;
  memberName: string;
  segment: string;
  frequency: number;
  monetary: number;
}

interface Props {
  data: RFMPoint[];
  onSelect: (point: RFMPoint) => void;
}

export function RFMScatterChart({ data, onSelect }: Props) {
  return (
    <div className="h-[320px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" dataKey="frequency" name="Frequency" />
          <YAxis type="number" dataKey="monetary" name="Monetary" />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Scatter
            data={data}
            fill="currentColor"
            className="text-primary"
            onClick={(event) => {
              const payload = (event as any)?.payload as RFMPoint | undefined;
              if (payload) onSelect(payload);
            }}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
