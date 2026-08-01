import React from 'react';

export interface AppCardProps {
  id: string;
  name: string;
  description: string;
  developerName: string;
  category: string;
  appType: 'Official' | 'Partner' | 'Private';
  iconUrl?: string;
  rating?: number;
  onClick: (id: string) => void;
}

export const AppCard: React.FC<AppCardProps> = ({
  id,
  name,
  description,
  developerName,
  category,
  appType,
  iconUrl,
  rating,
  onClick
}) => {
  return (
    <div 
      className="glass-card flex flex-col p-6 hover:-translate-y-1 hover:shadow-xl transition-all duration-300 cursor-pointer h-full border border-white/10 relative overflow-hidden"
      onClick={() => onClick(id)}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => e.key === 'Enter' && onClick(id)}
      aria-label={`View details for ${name} by ${developerName}`}
    >
      {/* AppType Badge */}
      <div className="absolute top-4 right-4 flex gap-2">
        <span className={`text-xs px-2 py-1 rounded-full bg-black/40 backdrop-blur-sm border ${
          appType === 'Official' ? 'border-blue-500/50 text-blue-300' : 
          appType === 'Partner' ? 'border-purple-500/50 text-purple-300' : 
          'border-gray-500/50 text-gray-300'
        }`}>
          {appType}
        </span>
      </div>

      <div className="flex items-center gap-4 mb-4">
        <div className="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center p-2 shrink-0">
          {iconUrl ? (
            <img src={iconUrl} alt={`${name} logo`} className="w-full h-full object-contain rounded-xl" loading="lazy" />
          ) : (
            <span className="text-2xl font-bold text-white/40">{name.charAt(0)}</span>
          )}
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white group-hover:text-blue-400 transition-colors">{name}</h3>
          <p className="text-sm text-white/50">{developerName}</p>
        </div>
      </div>
      
      <p className="text-sm text-white/70 line-clamp-3 mb-6 flex-grow">{description}</p>
      
      <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/10">
        <span className="text-xs font-medium text-white/40 bg-white/5 px-2 py-1 rounded">{category}</span>
        {rating && (
          <div className="flex items-center gap-1 text-yellow-500 text-sm">
            <span>★</span>
            <span className="text-white/80">{rating.toFixed(1)}</span>
          </div>
        )}
      </div>
    </div>
  );
};
