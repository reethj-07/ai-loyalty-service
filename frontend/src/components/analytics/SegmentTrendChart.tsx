import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface Props {
  data: Array<Record<string, any>>;
}

export function SegmentTrendChart({ data }: Props) {
  return (
    <div className="h-[280px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 16, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Area type="monotone" dataKey="Champions" stroke="currentColor" fillOpacity={0.2} className="text-primary" fill="currentColor" />
          <Area type="monotone" dataKey="Loyal" stroke="currentColor" fillOpacity={0.15} className="text-secondary-foreground" fill="currentColor" />
          <Area type="monotone" dataKey="At Risk" stroke="currentColor" fillOpacity={0.1} className="text-muted-foreground" fill="currentColor" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
