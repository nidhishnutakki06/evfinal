import React, { useState, useEffect } from 'react';
import { useDomainStore } from '@/store';
import { controlsApi } from '@/services/api/controls';
import { Loader2 } from 'lucide-react';

export const WeatherControl: React.FC = () => {
  const envState = useDomainStore(state => state.systemState?.environment);
  
  const [weather, setWeather] = useState<string>('');
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (envState?.weather && !isPending) {
      setWeather(envState.weather);
    }
  }, [envState?.weather, isPending]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!weather.trim()) return;

    setIsPending(true);
    setError(null);
    try {
      await controlsApi.setWeather({ weather: weather.trim() });
    } catch (err: any) {
      setError(err.message || 'Failed to update weather');
    } finally {
      setIsPending(false);
    }
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-zinc-200">Environment</h3>
        {isPending && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
      </div>
      
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input 
          type="text" 
          value={weather} 
          onChange={(e) => setWeather(e.target.value)} 
          placeholder="e.g. Sunny"
          className="flex-1 bg-zinc-800 border border-zinc-700 rounded-lg px-3 py-1.5 text-sm text-zinc-200 focus:outline-none focus:border-blue-500"
        />
        <button 
          type="submit"
          disabled={isPending || !weather.trim() || weather === envState?.weather}
          className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium px-4 py-1.5 rounded-lg transition-colors"
        >
          Set
        </button>
      </form>
      
      {error && <div className="mt-3 text-xs text-red-500">{error}</div>}
    </div>
  );
};
