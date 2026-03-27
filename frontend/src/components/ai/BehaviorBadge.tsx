interface BehaviorBadgeProps {
  behavior: string;
}

export function BehaviorBadge({ behavior }: BehaviorBadgeProps) {
  const getBadgeClass = () => {
    switch (behavior) {
      case "Customer Inactivity":
        return "badge-inactivity";
      case "High Value Purchase":
        return "badge-high-value";
      case "Purchase Made":
        return "badge-purchase";
      case "New Purchase":
        return "badge-new-purchase";
      default:
        return "badge-inactivity";
    }
  };

  return (
    <span className={`badge-behavior ${getBadgeClass()}`}>
      {behavior}
    </span>
  );
}
