"use client";

import React from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { 
  Search, 
  FileText, 
  BarChart3, 
  Upload, 
  Briefcase, 
  Target,
  RefreshCw
} from "lucide-react";

const JobActionsSidebar = () => {
  const actions = [
    {
      title: "Search Jobs",
      description: "Find jobs matching your skills",
      icon: Search,
      action: () => console.log("Search jobs clicked"),
    },
    {
      title: "Analyze Resume",
      description: "Get feedback on your current resume",
      icon: FileText,
      action: () => console.log("Analyze resume clicked"),
    },
    {
      title: "Job Fit Analysis",
      description: "See how you match a specific job",
      icon: BarChart3,
      action: () => console.log("Job fit analysis clicked"),
    },
    {
      title: "Upload Resume",
      description: "Add or update your resume",
      icon: Upload,
      action: () => console.log("Upload resume clicked"),
    },
    {
      title: "Create Targeted Resume",
      description: "Generate a resume for a specific job",
      icon: Target,
      action: () => console.log("Create targeted resume clicked"),
    },
    {
      title: "Refresh Job Data",
      description: "Update your job search results",
      icon: RefreshCw,
      action: () => console.log("Refresh job data clicked"),
    },
  ];

  return (
    <Card className="w-full max-w-xs">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Briefcase className="w-5 h-5" />
          Job Tools
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {actions.map((action, index) => {
          const Icon = action.icon;
          return (
            <Button
              key={index}
              variant="outline"
              className="w-full justify-start h-auto py-3 px-4 text-left"
              onClick={action.action}
            >
              <div className="flex items-start gap-3">
                <Icon className="w-5 h-5 mt-0.5 flex-shrink-0" />
                <div>
                  <div className="font-medium">{action.title}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {action.description}
                  </div>
                </div>
              </div>
            </Button>
          );
        })}
      </CardContent>
    </Card>
  );
};

export default JobActionsSidebar;