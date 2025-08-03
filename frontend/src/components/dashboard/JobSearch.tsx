import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { findJobPostings } from '../../lib/api';

const JobSearch = () => {
  const { userId } = useAuth();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: () => findJobPostings(userId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['jobPostings'] });
    },
  });

  return (
    <div className="p-4 border rounded">
      <h2 className="mb-2 text-lg font-bold">Find Jobs</h2>
      <button onClick={() => mutation.mutate()} className="px-4 py-2 text-white bg-blue-500 rounded" disabled={mutation.isPending}>
        {mutation.isPending ? 'Searching...' : 'Find Jobs'}
      </button>
      {mutation.isError && <p className="mt-2 text-red-500">{mutation.error.message}</p>}
    </div>
  );
};

export default JobSearch;
