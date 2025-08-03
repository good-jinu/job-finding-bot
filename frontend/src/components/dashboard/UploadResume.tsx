import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../../contexts/AuthContext';
import { uploadResumeSource } from '../../lib/api';
import { useState } from 'react';

const UploadResume = () => {
  const { userId } = useAuth();
  const queryClient = useQueryClient();
  const [file, setFile] = useState<File | null>(null);

  const mutation = useMutation({
    mutationFn: (file: File) => uploadResumeSource(userId!, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumeSources', userId] });
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (file) {
      mutation.mutate(file);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded">
      <h2 className="mb-2 text-lg font-bold">Upload Resume</h2>
      <input type="file" onChange={handleFileChange} className="mb-2" />
      <button type="submit" className="px-4 py-2 text-white bg-blue-500 rounded" disabled={!file || mutation.isPending}>
        {mutation.isPending ? 'Uploading...' : 'Upload'}
      </button>
      {mutation.isError && <p className="mt-2 text-red-500">{mutation.error.message}</p>}
    </form>
  );
};

export default UploadResume;
