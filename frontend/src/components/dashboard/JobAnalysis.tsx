import { useMutation } from '@tanstack/react-query';
import { analyzeJobAndResume } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';

const JobAnalysis = () => {
  const { userId } = useAuth();
  const mutation = useMutation({
    mutationFn: () => analyzeJobAndResume(userId!),
  });

  // This component is simplified. You would typically trigger the mutation
  // from the JobPostingList component and display the results here.

  return (
    <div className="p-4 border rounded">
      <h2 className="mb-2 text-lg font-bold">Job Analysis</h2>
      {mutation.isPending && <p>Analyzing...</p>}
      {mutation.isError && <p>Error: {mutation.error.message}</p>}
      {mutation.data && <pre>{JSON.stringify(mutation.data, null, 2)}</pre>}
    </div>
  );
};

export default JobAnalysis;
