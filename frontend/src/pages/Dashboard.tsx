import UploadResume from '../components/dashboard/UploadResume';
import ResumeSourceList from '../components/dashboard/ResumeSourceList';
import JobSearch from '../components/dashboard/JobSearch';
import JobPostingList from '../components/dashboard/JobPostingList';
import JobAnalysis from '../components/dashboard/JobAnalysis';
import ResumeMaker from '../components/dashboard/ResumeMaker';

const Dashboard = () => {
  return (
    <div className="flex h-screen">
      <div className="w-1/4 p-4 space-y-4 overflow-y-auto border-r">
        <UploadResume />
        <ResumeSourceList />
        <JobSearch />
        <ResumeMaker />
      </div>
      <div className="flex-1 p-4 overflow-y-auto">
        <JobPostingList />
        <JobAnalysis />
      </div>
    </div>
  );
};

export default Dashboard;
