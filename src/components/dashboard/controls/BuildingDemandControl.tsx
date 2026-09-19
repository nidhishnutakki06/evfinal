import React, { useState, useEffect } from 'react';
import { useDomainStore } from '@/store';
import { controlsApi } from '@/services/api/controls';
import { useDebounce } from '@/hooks/useDebounce';
import { Loader2 } from 'lucide-react';

export const BuildingDemandControl: React.FC = () => {
  const building = useDomainStore(state => state.systemState?.building);
  
  const [ac, setAc] = useState<number>(0);
  const [lights, setLights] = useState<number>(0);
  const [lifts, setLifts] = useState<number>(0);
  const [appliances, setAppliances] = useState<number>(0);
  
  const [isPending, setIsPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Track if user is actively interacting to prevent WS overrides
  const [isInteracting, setIsInteracting] = useState(false);

  // Reconcile from backend when not interacting
  useEffect(() => {
    if (!isInteracting && building) {
      setAc(building.ac_demand ?? 0);
      setLights(building.lights_demand ?? 0);
      setLifts(building.lifts_demand ?? 0);
      setAppliances(building.appliances_demand ?? 0);
    }
  }, [building, isInteracting]);

  const debouncedAc = useDebounce(ac, 500);
  const debouncedLights = useDebounce(lights, 500);
  const debouncedLifts = useDebounce(lifts, 500);
  const debouncedAppliances = useDebounce(appliances, 500);

  // Send request when debounced values settle
  useEffect(() => {
    // Only send if we are actively interacting (to prevent initial mount re-sending)
    if (!isInteracting) return;
    
    const sendRequest = async () => {
      setIsPending(true);
      setError(null);
      try {
        await controlsApi.setBuildingDemand({
          ac: debouncedAc,
          lights: debouncedLights,
          lifts: debouncedLifts,
          appliances: debouncedAppliances
        });
      } catch (err: any) {
        setError(err.message || 'Failed to set building demand');
      } finally {
        setIsPending(false);
        setIsInteracting(false); // Let authoritative state take over again
      }
    };
    sendRequest();
  }, [debouncedAc, debouncedLights, debouncedLifts, debouncedAppliances]);

  const handleSlider = (setter: React.Dispatch<React.SetStateAction<number>>, value: string) => {
    setIsInteracting(true);
    setter(parseFloat(value) || 0);
  };

  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-zinc-200">Building Demand</h3>
        {isPending && <Loader2 className="w-4 h-4 animate-spin text-blue-500" />}
      </div>
      
      <div className="space-y-4">
        <InputRow label="AC / HVAC" value={ac} onChange={(v) => handleSlider(setAc, v)} />
        <InputRow label="Lights" value={lights} onChange={(v) => handleSlider(setLights, v)} />
        <InputRow label="Lifts" value={lifts} onChange={(v) => handleSlider(setLifts, v)} />
        <InputRow label="Appliances" value={appliances} onChange={(v) => handleSlider(setAppliances, v)} />
      </div>
      
      {error && <div className="mt-3 text-xs text-red-500">{error}</div>}
    </div>
  );
};

const InputRow = ({ label, value, onChange }: { label: string, value: number, onChange: (v: string) => void }) => (
  <div>
    <div className="flex justify-between text-xs text-zinc-400 mb-1">
      <span>{label}</span>
      <span>kW</span>
    </div>
    <input 
      type="number" 
      value={value} 
      onChange={(e) => onChange(e.target.value)} 
      className="w-full bg-zinc-800 border border-zinc-700 rounded-md px-2 py-1 text-sm text-zinc-200 focus:outline-none focus:border-blue-500"
    />
  </div>
);
