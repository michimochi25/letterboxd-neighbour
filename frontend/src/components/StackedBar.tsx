import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface DataItem {
  label: string;
  value: number;
  color: string;
}

const StackedBar = ({ data }: { data: DataItem[] }) => {
  // Calculate the total sum of all segments to determine percentages
  const totalValue = data.reduce((acc, item) => acc + item.value, 0);

  return (
    <div className="w-full max-w-2xl p-4 space-y-4 rounded-lg shadow-sm border border-gray-100">
      <div className="flex h-12 w-full overflow-hidden bg-gray-100 rounded-lg">
        {data.map((item, index) => {
          // Calculate width percentage
          const percentage = (item.value / totalValue) * 100;

          return (
            <Tooltip>
              <TooltipTrigger asChild>
                <div
                  key={index}
                  style={{ width: `${percentage}%` }}
                  className={`
                ${item.color} 
                flex items-center justify-center 
                transition-all duration-700 ease-in-out 
                hover:opacity-90 group relative
              `}
                >
                  {/* Label inside the bar (only show if wide enough) */}
                  {percentage > 5 && (
                    <span className="text-white font-bold text-sm truncate px-2 drop-shadow-md">
                      {item.value}
                    </span>
                  )}
                </div>
              </TooltipTrigger>
              <TooltipContent className="opacity-90">
                <p>{item.value}</p>
              </TooltipContent>
            </Tooltip>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-4 justify-center">
        {data.map((item, index) => (
          <div key={index} className="flex items-center gap-2">
            <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
            <span className="text-sm text-slate-100">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export { StackedBar };
