import React, { createContext, useState, ReactNode } from 'react';
import { AnalysisState } from '../types';

interface AnalysisContextType {
  currentAnalysis: AnalysisState;
  setCurrentAnalysis: React.Dispatch<React.SetStateAction<AnalysisState>>;
}

export const AnalysisContext = createContext<AnalysisContextType | undefined>(undefined);

interface AnalysisProviderProps {
  children: ReactNode;
}

export const AnalysisProvider: React.FC<AnalysisProviderProps> = ({ children }) => {
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisState>({
    status: 'idle'
  });
  
  return (
    <AnalysisContext.Provider value={{ currentAnalysis, setCurrentAnalysis }}>
      {children}
    </AnalysisContext.Provider>
  );
};