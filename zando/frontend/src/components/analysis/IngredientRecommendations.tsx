import React, { useState } from 'react';
import { IngredientRecommendation } from '../../types/analysis';
import { FaCheck, FaExclamationTriangle } from 'react-icons/fa';

type IngredientRecommendationsProps = {
  recommendations: {
    beneficial: IngredientRecommendation[];
    cautionary: IngredientRecommendation[];
  };
};

const IngredientRecommendations: React.FC<IngredientRecommendationsProps> = ({ recommendations }) => {
  const [activeTab, setActiveTab] = useState<'beneficial' | 'cautionary'>('beneficial');
  const { beneficial, cautionary } = recommendations;
  
  if (!beneficial?.length && !cautionary?.length) {
    return (
      <p className="text-gray-500 italic">No ingredient recommendations available based on your genetics.</p>
    );
  }
  
  return (
    <div>
      <div className="border-b border-gray-200 mb-4">
        <ul className="flex -mb-px">
          <li className="mr-2">
            <button
              className={`inline-block py-2 px-4 text-sm font-medium ${
                activeTab === 'beneficial'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('beneficial')}
            >
              Beneficial ({beneficial?.length || 0})
            </button>
          </li>
          <li>
            <button
              className={`inline-block py-2 px-4 text-sm font-medium ${
                activeTab === 'cautionary'
                  ? 'text-amber-600 border-b-2 border-amber-600'
                  : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setActiveTab('cautionary')}
            >
              Cautionary ({cautionary?.length || 0})
            </button>
          </li>
        </ul>
      </div>
      
      {activeTab === 'beneficial' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {beneficial?.length > 0 ? (
            beneficial.map((ingredient, index) => (
              <div key={index} className="bg-green-50 rounded-lg p-4 border border-green-100">
                <div className="flex items-start">
                  <div className="bg-green-100 p-2 rounded-full mr-3">
                    <FaCheck className="text-green-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{ingredient.name}</h4>
                    <p className="text-sm text-gray-600 mt-1">{ingredient.benefit}</p>
                    {ingredient.genes && (
                      <p className="text-xs text-gray-500 mt-2">
                        Related genes: {ingredient.genes.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 italic col-span-2">No beneficial ingredients identified based on your genetics.</p>
          )}
        </div>
      )}
      
      {activeTab === 'cautionary' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cautionary?.length > 0 ? (
            cautionary.map((ingredient, index) => (
              <div key={index} className="bg-amber-50 rounded-lg p-4 border border-amber-100">
                <div className="flex items-start">
                  <div className="bg-amber-100 p-2 rounded-full mr-3">
                    <FaExclamationTriangle className="text-amber-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{ingredient.name}</h4>
                    <p className="text-sm text-gray-600 mt-1">{ingredient.caution}</p>
                    {ingredient.genes && (
                      <p className="text-xs text-gray-500 mt-2">
                        Related genes: {ingredient.genes.join(', ')}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <p className="text-gray-500 italic col-span-2">No cautionary ingredients identified based on your genetics.</p>
          )}
        </div>
      )}
    </div>
  );
};

export default IngredientRecommendations;