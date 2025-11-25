import { cn } from "@/lib/utils";

const Card = ({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) => {
  return (
    <div
      className={cn(
        "bg-[#00e054] rounded-lg p-4 hover:opacity-90 transition-all duration-700 ease-in-out shadow-md",
        className
      )}
    >
      {children}
    </div>
  );
};

export { Card };
