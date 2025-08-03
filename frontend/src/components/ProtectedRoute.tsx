import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const ProtectedRoute = () => {
  const { userId } = useAuth();

  return userId ? <Outlet /> : <Navigate to="/login" />;
};

export default ProtectedRoute;
