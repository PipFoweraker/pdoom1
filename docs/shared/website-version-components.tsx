/**
 * Website Version Display Components
 * 
 * React/Next.js components for displaying game version information
 * on the pdoom1-website. These components consume the version APIs
 * and provide a consistent UI for version tracking.
 */

import React, { useState, useEffect } from 'react';

// === Types ===

interface GameVersion {
  version: string;
  display_version: string;
  release_date: string;
  release_name: string;
  status: 'stable' | 'prerelease' | 'deprecated';
  download_url: string;
  changelog_url: string;
  size_mb?: number;
  requirements?: {
    python: string;
    os: string[];
    memory: string;
    storage: string;
  };
}

interface VersionHistory {
  versions: GameVersion[];
  last_updated: string;
}

interface WebsiteVersion {
  version: string;
  name: string;
  release_date: string;
  description: string;
  build_info: {
    environment: string;
    framework: string;
    node_version: string;
  };
}

// === API Hooks ===

export const useCurrentGameVersion = () => {
  const [version, setVersion] = useState<GameVersion | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchVersion = async () => {
      try {
        const response = await fetch('/api/v1/versions/game/current');
        if (!response.ok) throw new Error('Failed to fetch version');
        const data = await response.json();
        setVersion(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchVersion();
  }, []);

  return { version, loading, error };
};

export const useVersionHistory = (limit: number = 10) => {
  const [history, setHistory] = useState<VersionHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`/api/v1/versions/game/history?limit=${limit}`);
        if (!response.ok) throw new Error('Failed to fetch version history');
        const data = await response.json();
        setHistory(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [limit]);

  return { history, loading, error };
};

// === Version Display Components ===

export const CurrentVersionBadge: React.FC<{ className?: string }> = ({ className = '' }) => {
  const { version, loading, error } = useCurrentGameVersion();

  if (loading) {
    return (
      <div className={`inline-flex items-center px-3 py-1 rounded-full bg-gray-100 animate-pulse ${className}`}>
        <div className="w-16 h-4 bg-gray-300 rounded"></div>
      </div>
    );
  }

  if (error || !version) {
    return (
      <div className={`inline-flex items-center px-3 py-1 rounded-full bg-red-100 text-red-800 ${className}`}>
        <span className="text-sm font-medium">Version Error</span>
      </div>
    );
  }

  const badgeColor = version.status === 'stable' 
    ? 'bg-green-100 text-green-800' 
    : version.status === 'prerelease'
    ? 'bg-yellow-100 text-yellow-800'
    : 'bg-gray-100 text-gray-800';

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full ${badgeColor} ${className}`}>
      <div className="flex items-center space-x-2">
        <span className="text-sm font-medium">{version.display_version}</span>
        {version.status === 'prerelease' && (
          <span className="text-xs px-1.5 py-0.5 bg-yellow-200 text-yellow-900 rounded">
            BETA
          </span>
        )}
      </div>
    </div>
  );
};

export const VersionHeader: React.FC = () => {
  const { version, loading, error } = useCurrentGameVersion();

  if (loading) {
    return (
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <div className="animate-pulse">
            <div className="h-8 bg-white/20 rounded w-64 mb-2"></div>
            <div className="h-4 bg-white/20 rounded w-48"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !version) {
    return (
      <div className="bg-red-600 text-white">
        <div className="container mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold">P(Doom): Bureaucracy Strategy Game</h1>
          <p className="text-red-200">Version information unavailable</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">
              P(Doom): Bureaucracy Strategy Game
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-lg">Current Version: {version.display_version}</span>
              <CurrentVersionBadge />
              <span className="text-sm opacity-90">
                Released {new Date(version.release_date).toLocaleDateString()}
              </span>
            </div>
          </div>
          <div className="text-right">
            <a
              href={version.download_url}
              className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
            >
              Download Game
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export const VersionCard: React.FC<{ version: GameVersion; featured?: boolean }> = ({ 
  version, 
  featured = false 
}) => {
  const releaseDate = new Date(version.release_date);
  const isRecent = Date.now() - releaseDate.getTime() < 30 * 24 * 60 * 60 * 1000; // 30 days

  return (
    <div className={`
      rounded-lg border p-6 transition-shadow hover:shadow-lg
      ${featured ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-white'}
    `}>
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            {version.display_version}
          </h3>
          <p className="text-gray-600 text-sm mt-1">
            {version.release_name}
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <CurrentVersionBadge />
          {isRecent && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              New
            </span>
          )}
        </div>
      </div>
      
      <div className="text-sm text-gray-600 mb-4">
        <p>Released: {releaseDate.toLocaleDateString()}</p>
        {version.size_mb && <p>Size: {version.size_mb}MB</p>}
      </div>

      {version.requirements && (
        <div className="mb-4 p-3 bg-gray-50 rounded">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Requirements</h4>
          <ul className="text-xs text-gray-600 space-y-1">
            <li>Python: {version.requirements.python}</li>
            <li>OS: {version.requirements.os.join(', ')}</li>
            <li>Memory: {version.requirements.memory}</li>
            <li>Storage: {version.requirements.storage}</li>
          </ul>
        </div>
      )}

      <div className="flex space-x-3">
        <a
          href={version.download_url}
          className="flex-1 bg-blue-600 text-white text-center py-2 px-4 rounded hover:bg-blue-700 transition-colors"
        >
          Download
        </a>
        <a
          href={version.changelog_url}
          className="flex-1 border border-gray-300 text-gray-700 text-center py-2 px-4 rounded hover:bg-gray-50 transition-colors"
        >
          Changelog
        </a>
      </div>
    </div>
  );
};

export const VersionTimeline: React.FC<{ limit?: number }> = ({ limit = 5 }) => {
  const { history, loading, error } = useVersionHistory(limit);

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="h-6 bg-gray-200 rounded w-32 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-64 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-48"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error || !history) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>Unable to load version history</p>
        <p className="text-sm mt-1">{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Release Timeline</h2>
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-4 top-0 bottom-0 w-px bg-gray-200"></div>
        
        <div className="space-y-8">
          {history.versions.map((version, index) => (
            <div key={version.version} className="relative flex items-start space-x-6">
              {/* Timeline dot */}
              <div className={`
                relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2
                ${index === 0 ? 'bg-blue-600 border-blue-600' : 'bg-white border-gray-300'}
              `}>
                {index === 0 && <div className="w-3 h-3 bg-white rounded-full"></div>}
              </div>
              
              {/* Content */}
              <div className="flex-1 min-w-0 pb-8">
                <div className="flex items-center space-x-2 mb-2">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {version.display_version}
                  </h3>
                  <CurrentVersionBadge />
                </div>
                <p className="text-gray-600 mb-2">{version.release_name}</p>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>{new Date(version.release_date).toLocaleDateString()}</span>
                  <span>•</span>
                  <a href={version.download_url} className="text-blue-600 hover:text-blue-700">
                    Download
                  </a>
                  <span>•</span>
                  <a href={version.changelog_url} className="text-blue-600 hover:text-blue-700">
                    Release Notes
                  </a>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {history.versions.length >= limit && (
        <div className="text-center">
          <a
            href="/game/releases"
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            View All Releases
          </a>
        </div>
      )}
    </div>
  );
};

export const VersionComparison: React.FC<{ 
  currentVersion?: string; 
  compareVersion?: string 
}> = ({ currentVersion, compareVersion }) => {
  // This would integrate with the version API to show feature comparisons
  // Placeholder for future implementation
  
  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="text-lg font-semibold mb-4">Version Comparison</h3>
      <div className="text-gray-600">
        <p>Compare features between game versions</p>
        <p className="text-sm mt-2">
          Current: {currentVersion || 'Loading...'}
        </p>
        {compareVersion && (
          <p className="text-sm">
            Compare with: {compareVersion}
          </p>
        )}
      </div>
      <div className="mt-4 p-3 bg-blue-50 rounded text-sm text-blue-700">
        Feature comparison functionality will be available when 
        multiple stable versions are released.
      </div>
    </div>
  );
};

// === Data Integration Components (Placeholders) ===

export const DataIntegrationStatus: React.FC = () => {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('/api/v1/versions/data/current');
        const data = await response.json();
        setStatus(data);
      } catch (err) {
        console.error('Failed to fetch data integration status:', err);
      }
    };

    fetchStatus();
  }, []);

  if (!status) {
    return (
      <div className="bg-gray-100 rounded-lg p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 rounded w-48 mb-2"></div>
          <div className="h-3 bg-gray-300 rounded w-64"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border p-6">
      <h3 className="text-lg font-semibold mb-4">Data Integration</h3>
      
      {!status.enabled ? (
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
            <span className="text-gray-700">Integration in development</span>
          </div>
          <p className="text-sm text-gray-600">
            {status.message}
          </p>
          <div className="text-xs text-gray-500">
            Target date: {status.target_date}
          </div>
          <div className="space-y-1">
            <p className="text-sm font-medium text-gray-700">Planned features:</p>
            <ul className="text-sm text-gray-600 ml-4 space-y-1">
              <li>• Real-time leaderboards</li>
              <li>• Player statistics and analytics</li>
              <li>• Community challenges and events</li>
            </ul>
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            <span className="text-gray-700">Integration active</span>
          </div>
          <p className="text-sm text-gray-600">
            Last sync: {new Date(status.last_sync).toLocaleString()}
          </p>
        </div>
      )}
    </div>
  );
};

// === Export all components ===
export default {
  CurrentVersionBadge,
  VersionHeader,
  VersionCard,
  VersionTimeline,
  VersionComparison,
  DataIntegrationStatus,
  // Hooks
  useCurrentGameVersion,
  useVersionHistory,
};
