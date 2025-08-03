import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getJobPostings, analyzeJobAndResume } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';

const JobPostingList = () => {
  const { userId } = useAuth();
  const queryClient = useQueryClient();
  const { data, error, isLoading } = useQuery({
    queryKey: ['jobPostings'],
    queryFn: () => getJobPostings(),
  });

  const mutation = useMutation({
    mutationFn: () => analyzeJobAndResume(userId!),
    onSuccess: () => {
      // You might want to invalidate or update some state here
      // after a successful analysis.
    },
  });

  if (isLoading) return <p>Loading job postings...</p>;
  if (error) return <p>Error loading job postings: {error.message}</p>;

  return (
    <div className="p-4 border rounded">
      <h2 className="mb-2 text-lg font-bold">Job Postings</h2>
      <ul>
        {data && data.map((job: any) => (
          <li key={job.id} className="mb-2">
            <h3 className="font-bold">{job.title}</h3>
            <p>{job.company}</p>
            <button onClick={() => mutation.mutate()} className="px-2 py-1 text-sm text-white bg-green-500 rounded" disabled={mutation.isPending}>
              {mutation.isPending ? 'Analyzing...' : 'Analyze'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default JobPostingList;
