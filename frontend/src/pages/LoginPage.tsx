import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const LoginPage = () => {
  const [userId, setUserId] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (userId) {
      login(userId);
      navigate('/dashboard');
    }
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <form onSubmit={handleSubmit} className="p-8 bg-white rounded shadow-md">
        <h1 className="mb-4 text-2xl font-bold">Login</h1>
        <input
          type="text"
          value={userId}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter your User ID"
          className="w-full px-3 py-2 mb-4 border rounded"
        />
        <button type="submit" className="w-full px-4 py-2 text-white bg-blue-500 rounded">
          Login
        </button>
      </form>
    </div>
  );
};

export default LoginPage;
