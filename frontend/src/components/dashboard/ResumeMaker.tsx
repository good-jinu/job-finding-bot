import { useMutation } from '@tanstack/react-query';
import { makeResume } from '../../lib/api';
import { useAuth } from '../../contexts/AuthContext';
import { useState } from 'react';

const ResumeMaker = () => {
  const { userId } = useAuth();
  const [jobTarget, setJobTarget] = useState('');

  const mutation = useMutation({
    mutationFn: (jobTarget: string) => makeResume(userId!, jobTarget),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (jobTarget) {
      mutation.mutate(jobTarget);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded">
      <h2 className="mb-2 text-lg font-bold">Make Resume</h2>
      <input
        type="text"
        value={jobTarget}
        onChange={(e) => setJobTarget(e.target.value)}
        placeholder="Enter job target"
        className="w-full px-3 py-2 mb-2 border rounded"
      />
      <button type="submit" className="px-4 py-2 text-white bg-blue-500 rounded" disabled={!jobTarget || mutation.isPending}>
        {mutation.isPending ? 'Making...' : 'Make Resume'}
      </button>
      {mutation.isError && <p className="mt-2 text-red-500">{mutation.error.message}</p>}
      {mutation.data && (
        <div className="mt-2">
          <p>Resume created successfully!</p>
          <a href={mutation.data.resume_path} download className="text-blue-500">
            Download Resume
          </a>
        </div>
      )}
    </form>
  );
};

export default ResumeMaker;
