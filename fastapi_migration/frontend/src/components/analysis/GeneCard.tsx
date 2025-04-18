import React from 'react';
import { Mutation } from '../../types/analysis';

type GeneCardProps = {
  gene: Mutation;
};

const GeneCard: React.FC<GeneCardProps> = ({ gene }) => {
  const { rsid, gene_name, effect, evidence_level, allele } = gene;
  
  // Define color coding based on evidence level
  const evidenceColors = {
    high: 'bg-red-100 text-red-800 border-red-200',
    medium: 'bg-amber-100 text-amber-800 border-amber-200',
    low: 'bg-blue-100 text-blue-800 border-blue-200',
  };
  
  const evidenceColor = evidence_level === 'high' 
    ? evidenceColors.high 
    : evidence_level === 'medium' 
      ? evidenceColors.medium 
      : evidenceColors.low;
      
  return (
    <div className="border rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
      <div className="p-4">
        <div className="flex justify-between items-start mb-2">
          <h4 className="font-bold text-gray-900">{gene_name || 'Unknown Gene'}</h4>
          <span className={`text-xs px-2 py-1 rounded-full ${evidenceColor}`}>
            {evidence_level.toUpperCase()}
          </span>
        </div>
        
        <p className="text-sm text-gray-700 mb-2">{effect}</p>
        
        <div className="mt-3 pt-3 border-t border-gray-100 flex justify-between text-xs text-gray-500">
          <span>SNP: {rsid}</span>
          <span>Allele: {allele}</span>
        </div>
      </div>
    </div>
  );
};

export default GeneCard;