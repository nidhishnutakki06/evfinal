import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class DigitalTwinErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('DigitalTwinScene caught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="w-full h-full min-h-[400px] rounded-xl overflow-hidden border border-zinc-800 bg-zinc-900/50 flex flex-col items-center justify-center text-zinc-500">
          <p>3D Visualization Unavailable</p>
        </div>
      );
    }

    return this.props.children;
  }
}
