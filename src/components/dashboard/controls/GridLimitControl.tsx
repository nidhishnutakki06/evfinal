import React, { useState, useEffect } from 'react';
import { useDomainStore } from '@/store';
import { controlsApi } from '@/services/api/controls';
import { useDebounce } from '@/hooks/useDebounce';
import { Loader2 } from 'lucide-react';

export const GridLimitControl: React.FC = () => {
  const grid = useDomainStore(state => state.systemState?.grid);
  
  const [limit, setLimit] = useState<number>(0);
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isInteracting, setIsInteracting] = useState(false);

  useEffect(() => {
    if (!isInteracting && grid) {
      setLimit(grid.active_limit ?? 0);
    }
  }, [grid, isInteracting]);

  const debouncedLimit = useDebounce(limit, 500);

  useEffect(() => {
    if (!isInteracting) return;
    
    const sendRequest = async () => {
      setIsPending(true);
      setError(null);
      try {
        await controlsApi.setGridLimit({ limit: debouncedLimit });
      } catch (err: any) {
        setError(err.message || 'Failed to set grid limit');
      } finally {
        setIsPending(false);
        setIsInteracting(false);
      }
    };
    
    // Only dispatch if the user changed the slider
    sendRequest();
  }, [debouncedLimit]);

  const handleSlider = (value: string) => {
    setIsInteracting(true);
    setLimit(parseFloat(value) || 0);
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-zinc-200">Grid Limit</h3>
        {isPending && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
      </div>
      
      <div>
        <div className="flex justify-between text-xs text-zinc-400 mb-1">
          <span>Active Limit (kW)</span>
        </div>
        <input 
          type="number" 
          value={limit} 
          onChange={(e) => handleSlider(e.target.value)} 
          className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-2 py-1 text-sm text-zinc-200 focus:outline-none focus:border-blue-500"
        />
      </div>
      
      {error && <div className="mt-3 text-xs text-red-500">{error}</div>}
    </div>
  );
};
