import { useQuery } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { getResumeSources } from '../../lib/api';

const ResumeSourceList = () => {
  const { userId } = useAuth();
  const { data, error, isLoading } = useQuery({
    queryKey: ['resumeSources', userId],
    queryFn: () => getResumeSources(userId!),
    enabled: !!userId,
  });

  if (isLoading) return <p>Loading resume sources...</p>;
  if (error) return <p>Error loading resume sources: {error.message}</p>;

  return (
    <div className="p-4 border rounded">
      <h2 className="mb-2 text-lg font-bold">Resume Sources</h2>
      <ul>
        {data && data.map((source: any) => (
          <li key={source.id}>{source.source_file_name}</li>
        ))}
      </ul>
    </div>
  );
};

export default ResumeSourceList;
